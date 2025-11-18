import argparse
import json
import time
from pathlib import Path
from typing import Optional

from .utils import setup_logging, load_config, ensure_dir, project_root
from .data import load_json
from .preprocess import apply_normalization, deduplicate
from .features import extract_features
from .models import simple_score
from .detection import threshold


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
    print(json.dumps({"status": "trained", "config": cfg}))


def cmd_evaluate(config_path: Optional[str]) -> None:
    setup_logging()
    cfg = load_config(config_path) if config_path else {}
    print(json.dumps({"status": "evaluated", "config": cfg}))


def cmd_infer(config_path: Optional[str], input_path: Optional[str]) -> None:
    setup_logging()
    cfg = load_config(config_path) if config_path else {}
    if input_path:
        records = load_json(input_path)
        records = apply_normalization(records, field=cfg.get("data", {}).get("text_field", "text"))
        records = deduplicate(records, key="id")
        records = extract_features(records, field=cfg.get("data", {}).get("text_field", "text"))
        records = simple_score(records)
        records = threshold(records, t=cfg.get("detection", {}).get("score_threshold", 0.5))
        summary = {
            "count": len(records),
            "positives": sum(1 for r in records if r.get("label_pred") == 1),
        }
        print(json.dumps({"status": "inferred", "summary": summary}))
    else:
        print(json.dumps({"status": "inferred", "summary": {"count": 0}}))


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


if __name__ == "__main__":
    main()