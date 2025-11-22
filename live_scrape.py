"""
Live Scrape DFRAC - Scrape one by one and update HTML report
"""
import json
import time
from pathlib import Path
from datetime import datetime
from influence_detection.dfrac_scraper import DFRACScraper
from influence_detection.nlp_analyzer import NLPAnalyzer

def generate_html(reports):
    """Generate HTML content from reports list"""
    rows = ""
    for i, report in enumerate(reports, 1):
        analysis = report.get('analysis', {})
        intention = analysis.get('intention', {})
        verdict = report.get('verdict', 'Unknown')
        verdict_class = 'badge-' + verdict.lower() if verdict.lower() in ['fake', 'misleading', 'true'] else ''
        
        rows += f"""
        <tr>
            <td>{i}</td>
            <td>{report.get('date_published', 'N/A')}</td>
            <td><a href="{report.get('url', '#')}" target="_blank">{report.get('title', 'No Title')}</a></td>
            <td><span class="badge {verdict_class}">{verdict}</span></td>
            <td class="intention">{intention.get('category', 'N/A') if isinstance(intention, dict) else 'N/A'}</td>
            <td style="font-size: 0.9em; color: #c0392b;">{report.get('claim', 'N/A')[:200]}...</td>
            <td style="font-size: 0.9em; color: #27ae60;">{report.get('fact_check_details', 'N/A')[:200]}...</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="2"> <!-- Auto-refresh every 2 seconds -->
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DFRAC Live Scrape</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            .status {{ padding: 10px; background: #e3f2fd; color: #1565c0; border-radius: 4px; margin-bottom: 20px; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
            th {{ background: #f8f9fa; color: #2c3e50; font-weight: 600; }}
            tr:hover {{ background: #f8f9fa; }}
            .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 500; }}
            .badge-fake {{ background: #ffebee; color: #c62828; }}
            .badge-misleading {{ background: #fff3e0; color: #ef6c00; }}
            .badge-true {{ background: #e8f5e9; color: #2e7d32; }}
            .intention {{ font-style: italic; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 DFRAC Live Scrape</h1>
            <div class="status">Scraping in progress... Found {len(reports)} articles so far.</div>
            
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Date</th>
                        <th>Title</th>
                        <th>Verdict</th>
                        <th>Intention</th>
                        <th>Misinformation Claim</th>
                        <th>Fact Check</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html

def main():
    print("Initializing scraper...")
    scraper = DFRACScraper()
    analyzer = NLPAnalyzer()
    
    # 1. Find articles
    print("Finding recent articles...")
    # Get articles from last 30 days
    articles_info = scraper.get_recent_articles(days=30, max_pages=10)
    print(f"Found {len(articles_info)} articles to process.")
    
    output_file = Path("data/dfrac_live_report.html")
    csv_file = Path("data/dfrac_reports_export.csv")
    processed_reports = []
    
    # Initial empty report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(generate_html([]))
    
    print(f"\nOpen this file to watch progress: {output_file.absolute()}")
    print("-" * 50)
    
    # 2. Process one by one
    for i, info in enumerate(articles_info, 1):
        print(f"[{i}/{len(articles_info)}] Scraping: {info['title'][:50]}...")
        
        # Scrape
        article_data = scraper.scrape_article(info['url'])
        
        if article_data:
            article_data['date_published'] = info['date']
            
            # Analyze
            analysis = analyzer.analyze(article_data)
            report = {**article_data, 'analysis': analysis}
            
            processed_reports.append(report)
            
            # Update HTML
            html = generate_html(processed_reports)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
                
            print(f"  ✓ Verdict: {article_data['verdict']}")
            print(f"  ✓ Intention: {analysis['intention']['category']}")
        
        # Small pause to make it "one by one" visible
        time.sleep(0.5)

    print("\nDone! All articles scraped.")
    
    # Final update to remove auto-refresh or change status
    final_html = generate_html(processed_reports).replace('Scraping in progress...', '✅ Scraping Complete!')
    final_html = final_html.replace('<meta http-equiv="refresh" content="2">', '') # Stop refreshing
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    # Export to CSV
    print(f"Exporting to CSV: {csv_file}")
    import csv
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Headers
        writer.writerow([
            'Date', 'Title', 'Claim', 'Fact Check Details', 'Verdict', 'Language',
            'Platforms', 'Intention', 'Confidence', 'Categories',
            'Keywords', 'Sentiment', 'URL'
        ])
        
        # Rows
        for report in processed_reports:
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
    print("✓ CSV Export complete")

if __name__ == "__main__":
    main()
