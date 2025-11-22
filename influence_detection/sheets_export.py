"""
Google Sheets Exporter - Export analysis results to Google Sheets
"""
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional
from pathlib import Path
import json


class GoogleSheetsExporter:
    """Export DFRAC analysis to Google Sheets"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, credentials_file: Optional[str] = None):
        """
        Initialize Google Sheets client
        
        Args:
            credentials_file: Path to service account JSON credentials
                            If None, will look for GOOGLE_CREDENTIALS env var
        """
        self.credentials_file = credentials_file
        self.client = None
    
    def authenticate(self):
        """Authenticate with Google Sheets API"""
        if not self.credentials_file:
            raise ValueError(
                "Google Sheets credentials not provided. "
                "Please provide service account JSON file path."
            )
        
        if not Path(self.credentials_file).exists():
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")
        
        creds = Credentials.from_service_account_file(
            self.credentials_file,
            scopes=self.SCOPES
        )
        self.client = gspread.authorize(creds)
        print("✓ Authenticated with Google Sheets")
    
    def export_to_sheet(
        self, 
        reports: List[Dict], 
        spreadsheet_name: str,
        worksheet_name: str = "DFRAC Reports"
    ):
        """
        Export reports to Google Sheets
        
        Args:
            reports: List of analyzed report dictionaries
            spreadsheet_name: Name of spreadsheet to create/update
            worksheet_name: Name of worksheet within spreadsheet
        """
        if not self.client:
            self.authenticate()
        
        try:
            # Try to open existing spreadsheet or create new one
            try:
                spreadsheet = self.client.open(spreadsheet_name)
                print(f"✓ Opened existing spreadsheet: {spreadsheet_name}")
            except gspread.exceptions.SpreadsheetNotFound:
                spreadsheet = self.client.create(spreadsheet_name)
                print(f"✓ Created new spreadsheet: {spreadsheet_name}")
            
            # Get or create worksheet
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
                worksheet.clear()  # Clear existing data
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name, 
                    rows=1000, 
                    cols=20
                )
            
            # Prepare data for export
            headers = [
                'ID',
                'Date Published',
                'Misleading Claim',
                'Verdict',
                'Language',
                'Platforms',
                'Intention',
                'Intention Confidence',
                'Categories',
                'Keywords',
                'Sentiment',
                'Sentiment Polarity',
                'Entities (Locations)',
                'URL',
                'Title'
            ]
            
            rows = [headers]
            
            for i, report in enumerate(reports, 1):
                analysis = report.get('analysis', {})
                intention = analysis.get('intention', {})
                sentiment = analysis.get('sentiment', {})
                entities = analysis.get('entities', {})
                
                row = [
                    f"dfrac_{i:03d}",
                    report.get('date_published', 'N/A'),
                    report.get('claim', 'N/A')[:500],  # Truncate long text
                    report.get('verdict', 'N/A'),
                    analysis.get('language', 'N/A'),
                    ', '.join(report.get('platforms_mentioned', [])),
                    intention.get('category', 'N/A') if isinstance(intention, dict) else 'N/A',
                    intention.get('confidence', 0) if isinstance(intention, dict) else 0,
                    ', '.join(analysis.get('categories', [])),
                    ', '.join(analysis.get('keywords', [])[:10]),
                    sentiment.get('sentiment', 'N/A') if isinstance(sentiment, dict) else 'N/A',
                    sentiment.get('polarity', 0) if isinstance(sentiment, dict) else 0,
                    ', '.join(entities.get('locations', [])),
                    report.get('url', 'N/A'),
                    report.get('title', 'N/A')[:200]
                ]
                rows.append(row)
            
            # Write to sheet
            worksheet.update('A1', rows, value_input_option='USER_ENTERED')
            
            # Format header row
            worksheet.format('A1:O1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9}
            })
            
            # Auto-resize columns
            worksheet.columns_auto_resize(0, len(headers))
            
            print(f"✓ Exported {len(reports)} reports to Google Sheets")
            print(f"✓ Spreadsheet URL: {spreadsheet.url}")
            
            return spreadsheet.url
            
        except Exception as e:
            print(f"Error exporting to Google Sheets: {e}")
            raise

    def export_to_sheet_by_id(
        self, 
        reports: List[Dict], 
        spreadsheet_id: str,
        worksheet_name: str = "DFRAC Reports"
    ):
        """
        Export reports to a specific Google Sheet by ID
        
        Args:
            reports: List of analyzed report dictionaries
            spreadsheet_id: ID of the spreadsheet
            worksheet_name: Name of worksheet within spreadsheet
        """
        if not self.client:
            self.authenticate()
        
        try:
            # Open by key (ID)
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            print(f"✓ Opened spreadsheet by ID: {spreadsheet_id}")
            
            # Get or create worksheet
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
                worksheet.clear()  # Clear existing data
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name, 
                    rows=1000, 
                    cols=20
                )
            
            # Prepare data for export
            headers = [
                'ID',
                'Date Published',
                'Misleading Claim',
                'Verdict',
                'Language',
                'Platforms',
                'Intention',
                'Intention Confidence',
                'Categories',
                'Keywords',
                'Sentiment',
                'Sentiment Polarity',
                'Entities (Locations)',
                'URL',
                'Title'
            ]
            
            rows = [headers]
            
            for i, report in enumerate(reports, 1):
                analysis = report.get('analysis', {})
                intention = analysis.get('intention', {})
                sentiment = analysis.get('sentiment', {})
                entities = analysis.get('entities', {})
                
                row = [
                    f"dfrac_{i:03d}",
                    report.get('date_published', 'N/A'),
                    report.get('claim', 'N/A')[:500],
                    report.get('verdict', 'N/A'),
                    analysis.get('language', 'N/A'),
                    ', '.join(report.get('platforms_mentioned', [])),
                    intention.get('category', 'N/A') if isinstance(intention, dict) else 'N/A',
                    intention.get('confidence', 0) if isinstance(intention, dict) else 0,
                    ', '.join(analysis.get('categories', [])),
                    ', '.join(analysis.get('keywords', [])[:10]),
                    sentiment.get('sentiment', 'N/A') if isinstance(sentiment, dict) else 'N/A',
                    sentiment.get('polarity', 0) if isinstance(sentiment, dict) else 0,
                    ', '.join(entities.get('locations', [])),
                    report.get('url', 'N/A'),
                    report.get('title', 'N/A')[:200]
                ]
                rows.append(row)
            
            # Write to sheet
            worksheet.update('A1', rows, value_input_option='USER_ENTERED')
            
            # Format header row
            worksheet.format('A1:O1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9}
            })
            
            # Auto-resize columns
            worksheet.columns_auto_resize(0, len(headers))
            
            print(f"✓ Exported {len(reports)} reports to Google Sheets")
            print(f"✓ Spreadsheet URL: {spreadsheet.url}")
            
            return spreadsheet.url
            
        except Exception as e:
            print(f"Error exporting to Google Sheets: {e}")
            raise
    
    def export_summary_sheet(
        self,
        summary: Dict,
        spreadsheet_name: str,
        worksheet_name: str = "Summary"
    ):
        """
        Export summary statistics to separate worksheet
        
        Args:
            summary: Summary statistics dictionary
            spreadsheet_name: Name of spreadsheet
            worksheet_name: Name of summary worksheet
        """
        if not self.client:
            self.authenticate()
        
        try:
            spreadsheet = self.client.open(spreadsheet_name)
            
            # Get or create summary worksheet
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
                worksheet.clear()
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=worksheet_name,
                    rows=100,
                    cols=10
                )
            
            # Prepare summary data
            rows = [
                ['DFRAC Analysis Summary'],
                [''],
                ['Total Reports', summary.get('total_reports', 0)],
                ['Scrape Date', summary.get('scrape_date', 'N/A')],
                [''],
                ['By Intention'],
            ]
            
            # Add intention breakdown
            by_intention = summary.get('by_intention', {})
            for intention, count in sorted(by_intention.items(), key=lambda x: x[1], reverse=True):
                rows.append([f'  {intention.capitalize()}', count])
            
            rows.extend([
                [''],
                ['By Platform']
            ])
            
            # Add platform breakdown
            by_platform = summary.get('by_platform', {})
            for platform, count in sorted(by_platform.items(), key=lambda x: x[1], reverse=True):
                rows.append([f'  {platform}', count])
            
            rows.extend([
                [''],
                ['By Language']
            ])
            
            # Add language breakdown
            by_language = summary.get('by_language', {})
            for lang, count in sorted(by_language.items(), key=lambda x: x[1], reverse=True):
                rows.append([f'  {lang}', count])
            
            worksheet.update('A1', rows, value_input_option='USER_ENTERED')
            
            # Format title
            worksheet.format('A1', {
                'textFormat': {'bold': True, 'fontSize': 14},
                'backgroundColor': {'red': 0.9, 'green': 0.6, 'blue': 0.2}
            })
            
            print(f"✓ Exported summary to worksheet: {worksheet_name}")
            
        except Exception as e:
            print(f"Error exporting summary: {e}")
            raise


def setup_google_sheets_credentials():
    """
    Helper function to guide users through Google Sheets setup
    """
    print("""
    === Google Sheets Setup Instructions ===
    
    1. Go to Google Cloud Console: https://console.cloud.google.com/
    2. Create a new project or select existing one
    3. Enable Google Sheets API and Google Drive API
    4. Create Service Account credentials:
       - Go to "Credentials" > "Create Credentials" > "Service Account"
       - Download the JSON key file
    5. Save the JSON file as 'google_credentials.json' in project root
    6. Share your Google Sheet with the service account email (found in JSON)
    
    For detailed guide, visit:
    https://docs.gspread.org/en/latest/oauth2.html#service-account
    """)


if __name__ == "__main__":
    # Show setup instructions
    setup_google_sheets_credentials()
