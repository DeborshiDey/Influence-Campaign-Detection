"""
DFRAC Pipeline - Orchestrates scraping, analysis, and export
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from collections import Counter

from .dfrac_scraper import DFRACScraper
from .nlp_analyzer import NLPAnalyzer
from .sheets_export import GoogleSheetsExporter


class DFRACPipeline:
    """Main pipeline for DFRAC analysis"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.scraper = DFRACScraper()
        self.analyzer = NLPAnalyzer()
        self.reports_file = self.data_dir / "dfrac_reports.json"
    
    def run_full_pipeline(
        self, 
        days: int = 7,
        export_to_sheets: bool = False,
        spreadsheet_name: str = "DFRAC Analysis",
        credentials_file: Optional[str] = None
    ) -> Dict:
        """
        Run complete pipeline: scrape -> analyze -> save -> export
        
        Args:
            days: Number of days to look back
            export_to_sheets: Whether to export to Google Sheets
            spreadsheet_name: Name of Google Sheet
            credentials_file: Path to Google credentials JSON
            
        Returns:
            Summary statistics
        """
        print("\n" + "="*60)
        print("DFRAC ANALYSIS PIPELINE")
        print("="*60 + "\n")
        
        # Step 1: Scrape articles
        print("Step 1: Scraping DFRAC articles...")
        articles = self.scraper.scrape_all_recent(days=days)
        
        if not articles:
            print("No articles found!")
            return {}
        
        # Step 2: Analyze articles
        print(f"\nStep 2: Analyzing {len(articles)} articles...")
        analyzed_reports = []
        
        for i, article in enumerate(articles, 1):
            print(f"  Analyzing {i}/{len(articles)}: {article.get('title', '')[:50]}...")
            analysis = self.analyzer.analyze(article)
            
            # Combine article and analysis
            report = {**article, 'analysis': analysis}
            analyzed_reports.append(report)
        
        # Step 3: Generate summary
        print("\nStep 3: Generating summary statistics...")
        summary = self._generate_summary(analyzed_reports)
        
        # Step 4: Save to JSON
        print("\nStep 4: Saving results...")
        self._save_reports(analyzed_reports, summary)
        
        # Step 5: Export to Google Sheets (if requested)
        if export_to_sheets:
            print("\nStep 5: Exporting to Google Sheets...")
            try:
                exporter = GoogleSheetsExporter(credentials_file)
                url = exporter.export_to_sheet(
                    analyzed_reports,
                    spreadsheet_name
                )
                exporter.export_summary_sheet(
                    summary,
                    spreadsheet_name
                )
                print(f"\n✓ Google Sheets URL: {url}")
            except Exception as e:
                print(f"\n✗ Google Sheets export failed: {e}")
                print("  Data is still saved in JSON format.")
        
        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        self._print_summary(summary)
        
        return summary
    
    def scrape_only(self, days: int = 7) -> List[Dict]:
        """Just scrape articles without analysis"""
        articles = self.scraper.scrape_all_recent(days=days)
        
        # Save raw data
        raw_file = self.data_dir / "dfrac_raw.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump({
                'scrape_date': datetime.now().isoformat(),
                'articles': articles
            }, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(articles)} raw articles to {raw_file}")
        return articles
    
    def analyze_existing(self) -> Dict:
        """Analyze previously scraped data"""
        raw_file = self.data_dir / "dfrac_raw.json"
        
        if not raw_file.exists():
            print(f"No data found at {raw_file}")
            return {}
        
        with open(raw_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        articles = data.get('articles', [])
        print(f"Analyzing {len(articles)} articles from {raw_file}...")
        
        analyzed_reports = []
        for article in articles:
            analysis = self.analyzer.analyze(article)
            report = {**article, 'analysis': analysis}
            analyzed_reports.append(report)
        
        summary = self._generate_summary(analyzed_reports)
        self._save_reports(analyzed_reports, summary)
        
        self._print_summary(summary)
        return summary
    
    def export_to_csv(self, output_file: Optional[str] = None):
        """Export reports to CSV"""
        if not self.reports_file.exists():
            print("No reports found. Run pipeline first.")
            return
        
        with open(self.reports_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        reports = data.get('reports', [])
        
        if not output_file:
            output_file = self.data_dir / "dfrac_reports.csv"
        
        # Create CSV content
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Headers
            writer.writerow([
                'Date', 'Title', 'Claim', 'Fact Check Details', 'Verdict', 'Language',
                'Platforms', 'Intention', 'Confidence', 'Categories',
                'Keywords', 'Sentiment', 'URL'
            ])
            
            # Rows
            for report in reports:
                analysis = report.get('analysis', {})
                intention = analysis.get('intention', {})
                sentiment = analysis.get('sentiment', {})
                
                writer.writerow([
                    report.get('date_published', ''),
                    report.get('title', '')[:100],
                    report.get('claim', '')[:500],
                    report.get('fact_check_details', '')[:500],
                    report.get('verdict', ''),
                    analysis.get('language', ''),
                    '; '.join(report.get('platforms_mentioned', [])),
                    intention.get('category', '') if isinstance(intention, dict) else '',
                    intention.get('confidence', '') if isinstance(intention, dict) else '',
                    '; '.join(analysis.get('categories', [])),
                    '; '.join(analysis.get('keywords', [])[:5]),
                    sentiment.get('sentiment', '') if isinstance(sentiment, dict) else '',
                    report.get('url', '')
                ])
        
        print(f"✓ Exported to CSV: {output_file}")
    
    def _generate_summary(self, reports: List[Dict]) -> Dict:
        """Generate summary statistics"""
        summary = {
            'scrape_date': datetime.now().isoformat(),
            'total_reports': len(reports),
            'by_intention': {},
            'by_platform': {},
            'by_language': {},
            'by_verdict': {},
            'by_sentiment': {}
        }
        
        all_platforms = []
        
        for report in reports:
            analysis = report.get('analysis', {})
            
            # Count intentions
            intention = analysis.get('intention', {})
            if isinstance(intention, dict):
                cat = intention.get('category', 'unknown')
                summary['by_intention'][cat] = summary['by_intention'].get(cat, 0) + 1
            
            # Count platforms
            platforms = report.get('platforms_mentioned', [])
            all_platforms.extend(platforms)
            
            # Count languages
            lang = analysis.get('language', 'unknown')
            summary['by_language'][lang] = summary['by_language'].get(lang, 0) + 1
            
            # Count verdicts
            verdict = report.get('verdict', 'unknown')
            summary['by_verdict'][verdict] = summary['by_verdict'].get(verdict, 0) + 1
            
            # Count sentiments
            sentiment = analysis.get('sentiment', {})
            if isinstance(sentiment, dict):
                sent = sentiment.get('sentiment', 'unknown')
                summary['by_sentiment'][sent] = summary['by_sentiment'].get(sent, 0) + 1
        
        # Platform counts
        platform_counts = Counter(all_platforms)
        summary['by_platform'] = dict(platform_counts)
        
        return summary
    
    def _save_reports(self, reports: List[Dict], summary: Dict):
        """Save reports and summary to JSON"""
        data = {
            'scrape_date': summary['scrape_date'],
            'reports': reports,
            'summary': summary
        }
        
        with open(self.reports_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved {len(reports)} analyzed reports to {self.reports_file}")
    
    def _print_summary(self, summary: Dict):
        """Print summary statistics"""
        print(f"\nTotal Reports: {summary.get('total_reports', 0)}")
        
        print("\nBy Intention:")
        for intention, count in sorted(
            summary.get('by_intention', {}).items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"  {intention:15s}: {count:3d}")
        
        print("\nBy Platform:")
        for platform, count in sorted(
            summary.get('by_platform', {}).items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]:  # Top 10
            print(f"  {platform:15s}: {count:3d}")
        
        print("\nBy Language:")
        for lang, count in sorted(summary.get('by_language', {}).items()):
            print(f"  {lang:15s}: {count:3d}")
        
        print("\nBy Verdict:")
        for verdict, count in sorted(
            summary.get('by_verdict', {}).items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"  {verdict:15s}: {count:3d}")
