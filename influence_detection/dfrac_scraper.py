"""
DFRAC Scraper - Web scraper for DFRAC.org fact-checking website
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import json
from pathlib import Path
import concurrent.futures
import time

class DFRACScraper:
    """Scraper for DFRAC.org fact-checking website"""
    
    BASE_URL = "https://dfrac.org/en/"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_recent_articles(self, days: int = 7, max_pages: int = 5) -> List[Dict]:
        """
        Fetch articles from last N days by crawling multiple pages
        
        Args:
            days: Number of days to look back
            max_pages: Maximum number of pages to crawl
            
        Returns:
            List of article dictionaries with basic info
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        articles = []
        seen_urls = set()
        
        print(f"Searching for articles since {cutoff_date.strftime('%Y-%m-%d')}...")
        
        for page in range(1, max_pages + 1):
            url = self.BASE_URL if page == 1 else f"{self.BASE_URL}page/{page}/"
            print(f"Scanning page {page}: {url}")
            
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 404:
                    print("Reached end of pages.")
                    break
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find article links - DFRAC uses h3 tags for article titles in listing
                # Also look for specific 2025 year links to be safe
                article_links = soup.select('h3 a') + soup.select('a[href*="/en/2025/"]')
                
                page_articles_found = 0
                
                for link in article_links:
                    url = link.get('href')
                    if not url or url in seen_urls:
                        continue
                        
                    # Make URL absolute if needed
                    if url.startswith('/'):
                        url = f"https://dfrac.org{url}"
                        
                    # Filter for actual article URLs (usually contain date)
                    date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
                    if not date_match:
                        continue
                        
                    seen_urls.add(url)
                    
                    year, month, day = map(int, date_match.groups())
                    article_date = datetime(year, month, day)
                    
                    if article_date >= cutoff_date:
                        articles.append({
                            'url': url,
                            'date': article_date.strftime('%Y-%m-%d'),
                            'title': link.get_text(strip=True) or 'Unknown'
                        })
                        page_articles_found += 1
                    
                print(f"  Found {page_articles_found} relevant articles on page {page}")
                
                # If we found no relevant articles on this page, and it's not page 1,
                # we might have gone too far back. But sometimes dates are mixed, 
                # so we'll check if the oldest article on page is older than cutoff.
                # For now, simple heuristic: if 0 found on page 2+, stop.
                if page > 1 and page_articles_found == 0:
                    print("No more recent articles found. Stopping pagination.")
                    break
                    
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                continue
                
        return articles
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape full article content
        
        Args:
            url: Article URL
            
        Returns:
            Dictionary with article details
        """
    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape full article content
        
        Args:
            url: Article URL
            
        Returns:
            Dictionary with article details
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.select_one('h1')
            title_text = title.get_text(strip=True) if title else 'Unknown'
            
            # Extract main content
            content_div = soup.select_one('article') or soup.select_one('.entry-content')
            content_text = content_div.get_text(separator='\n', strip=True) if content_div else ''
            
            # Extract claim and fact check details
            claim, fact_check = self._parse_claim_and_fact_check(soup, content_text)
            
            # Extract verdict
            verdict = self._parse_verdict(soup, content_text)
            
            # Extract platforms mentioned
            platforms = self._extract_platforms(content_text)
            
            # Detect language
            language = self._detect_language_from_url(url)
            
            return {
                'url': url,
                'title': title_text,
                'claim': claim,
                'fact_check_details': fact_check,
                'verdict': verdict,
                'content': content_text,
                'platforms_mentioned': platforms,
                'language': language
            }
            
        except Exception as e:
            print(f"Error scraping article {url}: {e}")
            return None
    
    def _parse_claim_and_fact_check(self, soup: BeautifulSoup, content: str) -> tuple[str, str]:
        """Extract the misleading claim and the fact check details"""
        # Normalize newlines
        content = content.replace('\r\n', '\n')
        
        # 1. Extract Claim
        claim = "Claim not extracted"
        
        # Split by "Fact Check" header if present
        # This header usually separates the intro (claim) from the investigation
        parts = re.split(r'\nFact Check\s*\n', content, flags=re.I)
        
        intro_text = parts[0]
        
        # Look for specific claim indicators in intro
        claim_match = re.search(r'(?:claim|allegation|caption|text reads).*?that\s+(.*?)(?:\n\n|\nFact Check|$)', intro_text, re.S | re.I)
        if claim_match:
            claim = claim_match.group(1).strip()
        else:
            # Fallback: Take the first substantial paragraph of intro
            # Skip lines that look like dates or authors
            paragraphs = [p.strip() for p in intro_text.split('\n') if len(p.strip()) > 50]
            if paragraphs:
                # If first paragraph is very short or looks like meta, take second
                claim = paragraphs[1] if len(paragraphs) > 1 else paragraphs[0]
        
        # 2. Extract Fact Check Details
        fact_check = "Fact check details not found"
        
        if len(parts) > 1:
            # We have a Fact Check section
            fc_section = parts[1]
            
            # Stop at Conclusion
            fc_parts = re.split(r'\nConclusion', fc_section, flags=re.I)
            fact_check = fc_parts[0].strip()
        else:
            # Try to find "Investigation" or similar if "Fact Check" header is missing
            investigation_match = re.search(r'(?:investigation|found that|revealed that)(.*?)(?:\nConclusion|$)', content, re.S | re.I)
            if investigation_match:
                fact_check = investigation_match.group(1).strip()
                
        return claim, fact_check
    
    def _parse_verdict(self, soup: BeautifulSoup, content: str) -> str:
        """Extract fact-check verdict with improved accuracy"""
        # 1. Explicit DFRAC Analysis/Verdict line (Strongest signal)
        explicit_patterns = [
            r'DFRAC Analysis:\s*([A-Za-z\s]+?)(?:\n|$)',
            r'Verdict:\s*([A-Za-z\s]+?)(?:\n|$)',
            r'Conclusion:\s*([A-Za-z\s]+?)(?:\n|$)'
        ]
        
        for pattern in explicit_patterns:
            match = re.search(pattern, content, re.I)
            if match:
                candidate = match.group(1).strip().lower()
                # Filter out common non-verdict words that might be caught
                if candidate not in ['the', 'in', 'a', 'this', 'we', 'upon', 'it']:
                    # Check if it contains key verdict words
                    if any(w in candidate for w in ['fake', 'misleading', 'true', 'false']):
                        return candidate.title()

        # 2. Look for verdict in the Conclusion paragraph
        # Capture everything after Conclusion: until "Share this" or end
        conclusion_match = re.search(r'Conclusion[:\s]+(.*?)(?:Share this|DFRAC Analysis|$)', content, re.S | re.I)
        if conclusion_match:
            conclusion_text = conclusion_match.group(1).lower()
            
            # Priority keywords in conclusion
            if 'fake' in conclusion_text:
                return 'Fake'
            if 'misleading' in conclusion_text:
                return 'Misleading'
            if 'false' in conclusion_text:
                return 'False'
            if 'true' in conclusion_text:
                return 'True'

        # 3. Look for "Misleading-en" style tags at start of content
        # Often appears in first few lines
        header_text = content[:500].lower()
        if 'misleading-en' in header_text:
            return 'Misleading'
        if 'fake-en' in header_text:
            return 'Fake'
            
        return "Unknown"
    
    def _extract_platforms(self, content: str) -> List[str]:
        """Detect mentioned social media platforms"""
        platforms = {
            'Facebook': r'facebook|fb',
            'Twitter': r'twitter|tweet',
            'X': r'\bx\b(?!\s*ray)',  # Match X but not "X ray"
            'WhatsApp': r'whatsapp',
            'Instagram': r'instagram',
            'YouTube': r'youtube',
            'TikTok': r'tiktok',
            'Telegram': r'telegram',
            'Reddit': r'reddit'
        }
        
        found = []
        content_lower = content.lower()
        
        for platform, pattern in platforms.items():
            if re.search(pattern, content_lower):
                found.append(platform)
        
        return found
    
    def _detect_language_from_url(self, url: str) -> str:
        """Detect language from URL"""
        if '/en/' in url:
            return 'en'
        elif '/hi/' in url:
            return 'hi'
        return 'unknown'
    
    def scrape_all_recent(self, days: int = 7, save_to: Optional[str] = None) -> List[Dict]:
        """
        Scrape all recent articles with full details using concurrency
        
        Args:
            days: Days to look back
            save_to: Optional path to save results
            
        Returns:
            List of fully scraped articles
        """
        print(f"\nStep 1: Finding articles from last {days} days...")
        articles = self.get_recent_articles(days)
        print(f"Found {len(articles)} articles to scrape.")
        
        results = []
        if not articles:
            return results

        print(f"\nStep 2: Scraping {len(articles)} articles concurrently...")
        start_time = time.time()
        
        # Use ThreadPoolExecutor for concurrent scraping
        # Limit to 10 workers to be polite to the server
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Create a future for each article
            future_to_article = {
                executor.submit(self.scrape_article, article['url']): article 
                for article in articles
            }
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_article):
                article_info = future_to_article[future]
                try:
                    data = future.result()
                    if data:
                        # Merge with date from article list
                        data['date_published'] = article_info['date']
                        results.append(data)
                    
                    completed += 1
                    print(f"  [{completed}/{len(articles)}] Scraped: {article_info['title'][:40]}...")
                    
                except Exception as exc:
                    print(f"  Article {article_info['url']} generated an exception: {exc}")
        
        duration = time.time() - start_time
        print(f"\nScraping completed in {duration:.2f} seconds.")
        
        if save_to:
            self._save_results(results, save_to)
        
        return results
    
    def _save_results(self, results: List[Dict], filepath: str):
        """Save results to JSON file"""
        data = {
            'scrape_date': datetime.now().isoformat(),
            'total_articles': len(results),
            'articles': results
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(results)} articles to {filepath}")


if __name__ == "__main__":
    scraper = DFRACScraper()
    articles = scraper.scrape_all_recent(days=7, save_to='data/dfrac_raw.json')

