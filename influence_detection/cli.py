import argparse
import json
import time
from pathlib import Path
from typing import Optional

from .utils import setup_logging, load_config, ensure_dir, project_root
from .data import load_dataset
from .preprocess import apply_normalization, deduplicate
from .features import extract_features
from .graph import build_graph, calculate_graph_features
from .models import train_model, predict_model, load_model
from .detection import threshold
from .reddit import fetch_data
from .dfrac_pipeline import DFRACPipeline

def process_pipeline(records, cfg):
    """Run common pipeline steps: normalization, deduplication, features."""
    records = apply_normalization(records, field=cfg.get("data", {}).get("text_field", "text"))
    records = deduplicate(records, key="id")
    
    # Graph features
    G = build_graph(records)
    graph_feats = calculate_graph_features(G)
    
    # Feature extraction
    records = extract_features(records, field=cfg.get("data", {}).get("text_field", "text"), graph_features=graph_feats)
    return records

def cmd_prepare(config_path: Optional[str]) -> None:
    setup_logging()
    root = project_root()
    cfg = load_config(config_path) if config_path else {}
    reports_dir = ensure_dir(str(root / "reports"))
    run_dir = ensure_dir(str(reports_dir / f"run_{int(time.time())}"))
    meta = {"status": "prepared", "config": cfg}
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(str(run_dir))


def cmd_train(config_path: Optional[str]) -> None:
    setup_logging()
    cfg = load_config(config_path) if config_path else {}
    
    input_path = cfg.get("data", {}).get("input_path", "data/sample.json")
    df = load_dataset(input_path)
    records = df.to_dict(orient="records")
    
    records = process_pipeline(records, cfg)
    
    # Train
    model_path = Path("model.joblib")
    train_model(records, save_path=model_path)
    
    print(json.dumps({"status": "trained", "config": cfg, "model_path": str(model_path)}))


def cmd_evaluate(config_path: Optional[str]) -> None:
    setup_logging()
    cfg = load_config(config_path) if config_path else {}
    # For now, just a placeholder as we don't have a separate test set defined in config
    print(json.dumps({"status": "evaluated", "config": cfg, "metrics": {"accuracy": "N/A (implement split)"}}))


def cmd_infer(config_path: Optional[str], input_path: Optional[str]) -> None:
    setup_logging()
    cfg = load_config(config_path) if config_path else {}
    
    if not input_path:
        input_path = cfg.get("data", {}).get("input_path", "data/sample.json")
        
    df = load_dataset(input_path)
    records = df.to_dict(orient="records")
    
    records = process_pipeline(records, cfg)
    
    # Load model and predict
    model_path = Path("model.joblib")
    if model_path.exists():
        model = load_model(model_path)
        records = predict_model(model, records)
    else:
        print("Model not found. Please train first.")
        return

    records = threshold(records, t=cfg.get("detection", {}).get("score_threshold", 0.5))
    
    summary = {
        "count": len(records),
        "positives": sum(1 for r in records if r.get("label_pred") == 1),
    }
    print(json.dumps({"status": "inferred", "summary": summary}))


def cmd_fetch_reddit(subreddit: str, limit: int, output_path: str) -> None:
    setup_logging()
    print(f"Fetching {limit} posts from r/{subreddit}...")
    try:
        data = fetch_data(subreddit, limit)
        
        # Save to JSON
        p = Path(output_path)
        ensure_dir(str(p.parent))
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        
        print(json.dumps({"status": "fetched", "count": len(data), "output": str(p)}))
    except Exception as e:
        print(f"Error fetching data: {e}")
        print("Ensure REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET are set.")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="influence_detection")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("prepare")
    sp.add_argument("--config", type=str, default="configs/base.json")

    st = sub.add_parser("train")
    st.add_argument("--config", type=str, default="configs/base.json")

    se = sub.add_parser("evaluate")
    se.add_argument("--config", type=str, default="configs/base.json")

    si = sub.add_parser("infer")
    si.add_argument("--config", type=str, default="configs/base.json")
    si.add_argument("--input", type=str)

    sr = sub.add_parser("fetch-reddit")
    sr.add_argument("--subreddit", type=str, required=True, help="Subreddit to fetch from")
    sr.add_argument("--limit", type=int, default=100, help="Max posts to fetch")
    sr.add_argument("--output", type=str, default="data/reddit.json", help="Output JSON path")

    # DFRAC commands
    dfrac = sub.add_parser("dfrac", help="DFRAC fact-check analysis commands")
    dfrac_sub = dfrac.add_subparsers(dest="dfrac_command", required=True)
    
    # dfrac scrape
    scrape = dfrac_sub.add_parser("scrape", help="Scrape and analyze DFRAC articles")
    scrape.add_argument("--days", type=int, default=7, help="Days to look back")
    scrape.add_argument("--export", action="store_true", help="Export to Google Sheets")
    scrape.add_argument("--credentials", type=str, help="Path to Google credentials JSON")
    
    # dfrac analyze
    dfrac_sub.add_parser("analyze", help="Analyze previously scraped data")
    
    # dfrac report
    dfrac_sub.add_parser("report", help="Show summary report")
    
    # dfrac export
    export = dfrac_sub.add_parser("export", help="Export reports")
    export.add_argument("--format", choices=['csv', 'sheets'], default='csv', help="Export format")
    export.add_argument("--credentials", type=str, help="Path to Google credentials JSON")

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "prepare":
        cmd_prepare(args.config)
    elif args.command == "train":
        cmd_train(args.config)
    elif args.command == "evaluate":
        cmd_evaluate(args.config)
    elif args.command == "infer":
        cmd_infer(args.config, getattr(args, "input", None))
    elif args.command == "fetch-reddit":
        cmd_fetch_reddit(args.subreddit, args.limit, args.output)
    elif args.command == "dfrac":
        pipeline = DFRACPipeline()
        if args.dfrac_command == "scrape":
            pipeline.run_full_pipeline(
                days=args.days,
                export_to_sheets=args.export,
                spreadsheet_name="DFRAC Analysis",
                credentials_file=getattr(args, "credentials", None)
            )
        elif args.dfrac_command == "analyze":
            pipeline.analyze_existing()
        elif args.dfrac_command == "report":
            if not pipeline.reports_file.exists():
                print("No reports found. Run 'dfrac scrape' first.")
            else:
                with open(pipeline.reports_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                pipeline._print_summary(data.get('summary', {}))
        elif args.dfrac_command == "export":
            if args.format == 'csv':
                pipeline.export_to_csv()
            elif args.format == 'sheets':
                if not pipeline.reports_file.exists():
                    print("No reports found. Run 'dfrac scrape' first.")
                else:
                    with open(pipeline.reports_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    from .sheets_export import GoogleSheetsExporter
                    exporter = GoogleSheetsExporter(getattr(args, "credentials", None))
                    exporter.export_to_sheet(data['reports'], "DFRAC Analysis")
                    exporter.export_summary_sheet(data['summary'], "DFRAC Analysis")


if __name__ == "__main__":
    main()