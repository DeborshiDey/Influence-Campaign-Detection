"""
NLP Analyzer - Performs intention detection and content analysis
"""
from typing import Dict, List
import re
from collections import Counter
from textblob import TextBlob
from langdetect import detect, LangDetectException


class NLPAnalyzer:
    """NLP analysis for fact-check articles"""
    
    # Intention classification keywords
    INTENTION_KEYWORDS = {
        'political': [
            'election', 'vote', 'voting', 'government', 'party', 'minister', 
            'congress', 'bjp', 'politik', 'campaign', 'parliament', 'mla', 'mp',
            'leader', 'rally', 'protest', 'policy', 'scheme', 'modi', 'gandhi',
            'aap', 'tmc', 'samajwadi', 'democratic', 'constitution'
        ],
        'religious': [
            'hindu', 'muslim', 'islam', 'christian', 'temple', 'mosque', 
            'church', 'religious', 'allah', 'god', 'pray', 'religion', 'sikh',
            'festival', 'diwali', 'eid', 'christmas', 'convert', 'conversion',
            'sacred', 'idol', 'prophet', 'quran', 'bible', 'gita'
        ],
        'health': [
            'vaccine', 'medicine', 'covid', 'cure', 'doctor', 'hospital', 
            'disease', 'treatment', 'health', 'virus', 'pandemic', 'ayurveda',
            'cancer', 'heart attack', 'died suddenly', 'side effect', 'who',
            'medical', 'remedy', 'homeopathy'
        ],
        'commercial': [
            'product', 'company', 'scam', 'fraud', 'money', 'prize', 'lottery', 
            'investment', 'business', 'bank', 'financial', 'scheme', 'offer',
            'discount', 'free', 'giveaway', 'amazon', 'flipkart', 'delivery'
        ],
        'communal': [
            'riot', 'attack', 'community', 'violence', 'clash', 'tension', 
            'mob', 'assault', 'hate', 'target', 'stone pelting', 'slogan',
            'flag', 'procession', 'encroachment'
        ],
        'international': [
            'pakistan', 'china', 'war', 'border', 'army', 'military', 
            'foreign', 'country', 'nation', 'kashmir', 'israel', 'palestine',
            'ukraine', 'russia', 'usa', 'biden', 'trump', 'putin', 'gaza',
            'hamas', 'terrorist', 'un'
        ],
        'crime': [
            'murder', 'rape', 'robbery', 'theft', 'crime', 'criminal', 
            'police', 'arrest', 'kidnap', 'abuse', 'killed', 'dead', 'body',
            'found', 'investigation', 'fir', 'accused', 'victim'
        ],
        'entertainment': [
            'bollywood', 'actor', 'actress', 'movie', 'film', 'celebrity', 
            'star', 'khan', 'kumar', 'kapoor', 'marriage', 'divorce', 'dating',
            'viral video', 'song', 'dance'
        ]
    }
    
    def analyze(self, article: Dict) -> Dict:
        """
        Perform complete NLP analysis on article
        
        Args:
            article: Article dictionary from scraper
            
        Returns:
            Analysis results dictionary
        """
        text = f"{article.get('title', '')} {article.get('claim', '')} {article.get('content', '')}"
        
        return {
            'language': self.detect_language(text),
            'keywords': self.extract_keywords(text),
            'intention': self.classify_intention(text),
            'sentiment': self.analyze_sentiment(text),
            'entities': self.extract_entities(text),
            'categories': self.categorize_content(article)
        }
    
    def detect_language(self, text: str) -> str:
        """Detect text language"""
        try:
            lang = detect(text)
            return lang if lang in ['en', 'hi'] else 'other'
        except LangDetectException:
            return 'unknown'
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract top keywords using frequency analysis"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'this', 'that', 'with', 'from', 'have', 'been', 'were', 
            'they', 'their', 'there', 'these', 'those', 'about', 
            'would', 'could', 'should', 'which', 'what', 'when'
        }
        words = [w for w in words if w not in stop_words]
        
        # Count and return top N
        counter = Counter(words)
        return [word for word, count in counter.most_common(top_n)]
    
    def classify_intention(self, text: str) -> Dict[str, any]:
        """
        Classify intention based on keyword matching
        
        Returns:
            Dict with intention category and confidence
        """
        text_lower = text.lower()
        scores = {}
        
        # Calculate score for each intention category
        for intention, keywords in self.INTENTION_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            scores[intention] = matches
        
        if not any(scores.values()):
            return {
                'category': 'unknown',
                'confidence': 0.0,
                'all_scores': scores
            }
        
        # Get top intention
        top_intention = max(scores, key=scores.get)
        top_score = scores[top_intention]
        total_matches = sum(scores.values())
        
        # Calculate confidence
        confidence = (top_score / total_matches) if total_matches > 0 else 0.0
        
        return {
            'category': top_intention,
            'confidence': round(confidence, 2),
            'match_count': top_score,
            'all_scores': scores
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """Analyze sentiment of text"""
        try:
            blob = TextBlob(text[:5000])  # Limit text length
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'polarity': round(polarity, 2),
                'subjectivity': round(blob.sentiment.subjectivity, 2)
            }
        except Exception as e:
            return {
                'sentiment': 'unknown',
                'polarity': 0.0,
                'subjectivity': 0.0,
                'error': str(e)
            }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities (simple pattern-based approach)
        For more advanced extraction, use spaCy or similar
        """
        entities = {
            'locations': [],
            'organizations': [],
            'persons': []
        }
        
        # Simple capitalized word extraction as a placeholder
        # In production, use spaCy or similar NER library
        capitalized_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Common Indian locations
        locations = {
            'india', 'pakistan', 'delhi', 'mumbai', 'kashmir', 'bengal',
            'bihar', 'punjab', 'britain', 'china', 'america', 'london'
        }
        
        for word in capitalized_words:
            if word.lower() in locations:
                if word not in entities['locations']:
                    entities['locations'].append(word)
        
        return entities
    
    def categorize_content(self, article: Dict) -> List[str]:
        """Categorize type of misinformation"""
        categories = []
        
        content = article.get('content', '').lower()
        title = article.get('title', '').lower()
        
        # Check for different types of misinformation
        if any(word in content for word in ['video', 'footage', 'clip']):
            categories.append('video_misinformation')
        
        if any(word in content for word in ['image', 'photo', 'picture']):
            categories.append('image_misinformation')
        
        if any(word in content for word in ['fake', 'fabricated', 'doctored', 'manipulated']):
            categories.append('fabricated_content')
        
        if any(word in content for word in ['old', 'unrelated', 'different']):
            categories.append('out_of_context')
        
        if any(word in content for word in ['ai', 'deepfake', 'generated']):
            categories.append('ai_generated')
        
        if any(word in content for word in ['satire', 'parody']):
            categories.append('satire')
        
        return categories if categories else ['general_misinformation']


if __name__ == "__main__":
    # Test the analyzer
    analyzer = NLPAnalyzer()
    
    test_article = {
        'title': 'Viral Classroom Video Claiming Islamic Indoctrination found to be Fake',
        'claim': 'Children being indoctrinated into Islam in British school',
        'content': 'A video is circulating online with allegations about Islamic indoctrination. The video shows manipulated footage.'
    }
    
    results = analyzer.analyze(test_article)
    print("Analysis Results:")
    for key, value in results.items():
        print(f"{key}: {value}")
