"""Test DFRAC scraper"""
from influence_detection.dfrac_scraper import DFRACScraper
import requests
from bs4 import BeautifulSoup

scraper = DFRACScraper()

# Test basic connection
print("Testing DFRAC connection...")
response = scraper.session.get(scraper.BASE_URL, timeout=10)
print(f"Status code: {response.status_code}")

# Parse HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Debug: find article links
print("\nLooking for article links...")
print(f"Total links: {len(soup.find_all('a'))}")

# Try different selectors
selectors_to_try = [
    'article a',
    'a[href*="/en/2025/"]',
    '.post a',
    '.entry-title a',
    'h2 a',
    'h3 a'
]

for selector in selectors_to_try:
    links = soup.select(selector)
    print(f"\nSelector '{selector}': found {len(links)} links")
    if links:
        for i, link in enumerate(links[:3]):
            print(f"  {i+1}. {link.get('href')} - {link.get_text(strip=True)[:50]}")

# Show first few article titles
print("\n\nAll h2 and h3 headers:")
for header in soup.find_all(['h2', 'h3'])[:10]:
    print(f"  - {header.get_text(strip=True)[:60]}")
