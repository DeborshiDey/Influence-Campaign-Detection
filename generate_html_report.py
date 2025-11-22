"""
Generate HTML Report for DFRAC Analysis
"""
import json
from pathlib import Path
from datetime import datetime

def generate_html_report():
    data_file = Path("data/dfrac_reports.json")
    if not data_file.exists():
        print("No data found.")
        return

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    reports = data.get('reports', [])
    summary = data.get('summary', {})
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DFRAC Analysis Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #3498db; }}
            .card h3 {{ margin: 0 0 10px 0; color: #7f8c8d; font-size: 0.9em; text-transform: uppercase; }}
            .card .value {{ font-size: 1.8em; font-weight: bold; color: #2c3e50; }}
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
            <h1>DFRAC Analysis Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="summary-grid">
                <div class="card">
                    <h3>Total Reports</h3>
                    <div class="value">{summary.get('total_reports', 0)}</div>
                </div>
                <div class="card">
                    <h3>Top Intention</h3>
                    <div class="value">{list(summary.get('by_intention', {}).keys())[0] if summary.get('by_intention') else 'N/A'}</div>
                </div>
                <div class="card">
                    <h3>Top Platform</h3>
                    <div class="value">{list(summary.get('by_platform', {}).keys())[0] if summary.get('by_platform') else 'N/A'}</div>
                </div>
            </div>

            <h2>Detailed Reports</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Title</th>
                        <th>Verdict</th>
                        <th>Misinformation Claim</th>
                        <th>Fact Check</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for report in reports:
        analysis = report.get('analysis', {})
        intention = analysis.get('intention', {})
        verdict = report.get('verdict', 'Unknown')
        verdict_class = 'badge-' + verdict.lower() if verdict.lower() in ['fake', 'misleading', 'true'] else ''
        
        html_content += f"""
                    <tr>
                        <td>{report.get('date_published', 'N/A')}</td>
                        <td><a href="{report.get('url', '#')}" target="_blank">{report.get('title', 'No Title')}</a></td>
                        <td><span class="badge {verdict_class}">{verdict}</span></td>
                        <td style="font-size: 0.9em; color: #c0392b;">{report.get('claim', 'N/A')[:300]}...</td>
                        <td style="font-size: 0.9em; color: #27ae60;">{report.get('fact_check_details', 'N/A')[:300]}...</td>
                    </tr>
        """
    
    html_content += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    output_file = Path("data/dfrac_report.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[SUCCESS] HTML Report generated: {output_file}")

if __name__ == "__main__":
    generate_html_report()
