import os
import praw
from typing import List, Dict, Optional
from datetime import datetime

class RedditClient:
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "influence_detection_bot/1.0")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables must be set.")
            
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )

    def fetch_subreddit_posts(self, subreddit_name: str, limit: int = 100) -> List[Dict]:
        """
        Fetch posts from a subreddit.
        
        Args:
            subreddit_name: Name of the subreddit (e.g., 'politics').
            limit: Maximum number of posts to fetch.
            
        Returns:
            List of dictionaries with post data.
        """
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        
        for submission in subreddit.new(limit=limit):
            post = {
                "id": submission.id,
                "text": submission.title + " " + submission.selftext,
                "src": str(submission.author) if submission.author else "[deleted]",
                "dst": "", # Top-level post has no destination user
                "timestamp": int(submission.created_utc),
                "url": submission.url,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "type": "post"
            }
            posts.append(post)
            
            # Optional: Fetch top comments as well? 
            # For now, let's keep it simple and just get posts.
            
        return posts

def fetch_data(subreddit: str, limit: int = 100) -> List[Dict]:
    """Wrapper function to initialize client and fetch data."""
    client = RedditClient()
    return client.fetch_subreddit_posts(subreddit, limit)
