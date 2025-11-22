import json
import sys
import subprocess
from unittest.mock import patch, MagicMock
import pytest
from influence_detection.reddit import fetch_data

def test_fetch_reddit_mock(tmp_path):
    # Mock the RedditClient and its methods
    with patch("influence_detection.reddit.RedditClient") as MockClient:
        mock_instance = MockClient.return_value
        
        # Create mock posts
        mock_post1 = MagicMock()
        mock_post1.id = "123"
        mock_post1.title = "Title 1"
        mock_post1.selftext = "Body 1"
        mock_post1.author = "user1"
        mock_post1.created_utc = 1600000000
        mock_post1.url = "http://url1"
        mock_post1.score = 10
        mock_post1.num_comments = 5
        
        mock_instance.fetch_subreddit_posts.return_value = [
            {
                "id": "123",
                "text": "Title 1 Body 1",
                "src": "user1",
                "dst": "",
                "timestamp": 1600000000,
                "url": "http://url1",
                "score": 10,
                "num_comments": 5,
                "type": "post"
            }
        ]
        
        # Run the fetch function
        data = fetch_data("test_subreddit", limit=1)
        
        assert len(data) == 1
        assert data[0]["id"] == "123"
        assert data[0]["src"] == "user1"
        
        # Verify CLI call (mocked env vars)
        with patch.dict("os.environ", {"REDDIT_CLIENT_ID": "fake", "REDDIT_CLIENT_SECRET": "fake"}):
            output_file = tmp_path / "reddit.json"
            # We need to mock fetch_data inside cli as well if we run via subprocess, 
            # but since we can't easily mock subprocess internals, we'll trust the unit test above 
            # and just check if the CLI command exists and runs (it will fail auth but that's expected).
            
            cmd = [sys.executable, "-m", "influence_detection.cli", "fetch-reddit", "--subreddit", "test", "--output", str(output_file)]
            p = subprocess.run(cmd, capture_output=True, text=True)
            
            # It should fail with "Error fetching data" because we didn't mock the inner call in the subprocess
            # But we want to verify it TRIED to run.
            assert "Fetching 100 posts" in p.stdout
