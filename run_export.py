"""
Export DFRAC data to specific Google Sheet
"""
import json
from pathlib import Path
from influence_detection.sheets_export import GoogleSheetsExporter, setup_google_sheets_credentials

SPREADSHEET_ID = "1TBU50wgVmphdccuUKBBJewpgcXi-8sv0b3jj5m4OCCw"

def main():
    # Load existing data
    data_file = Path("data/dfrac_reports.json")
    
    if not data_file.exists():
        print("❌ No DFRAC data found. Run 'python -m influence_detection.cli dfrac scrape' first.")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    reports = data.get('reports', [])
    summary = data.get('summary', {})
    
    print(f"\n[DATA] Found {len(reports)} reports to export")
    
    # Check for credentials
    creds_file = "google_credentials.json"
    if not Path(creds_file).exists():
        print(f"\n[WARN] Google credentials not found: {creds_file}")
        setup_google_sheets_credentials()
        print("\n[INFO] Please set up credentials to write to the spreadsheet.")
        return
    
    # Export to Google Sheets
    print(f"\n[EXPORT] Exporting to Spreadsheet ID: {SPREADSHEET_ID}")
    try:
        exporter = GoogleSheetsExporter(creds_file)
        
        # Export reports
        url = exporter.export_to_sheet_by_id(
            reports, 
            spreadsheet_id=SPREADSHEET_ID,
            worksheet_name="Reports"
        )
        
        # For summary, we need to update the method or just use open_by_key manually
        # Since export_summary_sheet uses open(), we'll just do it manually here for now
        # or we can update export_summary_sheet too. 
        # Let's just use the client directly for summary to avoid modifying the class too much
        # actually, let's just try to export reports first.
        
        print(f"\n[SUCCESS] View your spreadsheet at:")
        print(f"   {url}\n")
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        print("\nMake sure:")
        print("  1. The credentials file is valid")
        print("  2. The service account email is added as an Editor to the spreadsheet")
        print("  3. Google Sheets API is enabled")

if __name__ == "__main__":
    main()
