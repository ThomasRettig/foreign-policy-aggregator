import unittest
import os
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, mock_open

from app.aggregator import (
    Article, 
    parse_date, 
    is_published_in_window, 
    enforce_local_diversity, 
    get_briefing,
    CACHE_FILE
)

class TestParserAndPipeline(unittest.TestCase):

    def setUp(self):
        """Set up standard mock data structures for stable testing."""
        self.now_utc = datetime.now(timezone.utc)
        
        # Sample articles from diverse sources
        self.article_a1 = Article(
            title="The Arctic Shift", source="Chatham House", 
            pub_date=self.now_utc - timedelta(hours=2), url="https://ex.com/1",
            reading_time=8, summary="Summary A1", category_list=[]
        )
        self.article_a2 = Article(
            title="Sovereignty in Deep Waters", source="Chatham House", 
            pub_date=self.now_utc - timedelta(hours=4), url="https://ex.com/2",
            reading_time=12, summary="Summary A2", category_list=[]
        )
        self.article_b1 = Article(
            title="Semiconductor Supply Bottlenecks", source="Brookings", 
            pub_date=self.now_utc - timedelta(hours=1), url="https://ex.com/3",
            reading_time=6, summary="Summary B1", category_list=[]
        )
        self.article_c1 = Article(
            title="Pacific Naval Deployments", source="RAND", 
            pub_date=self.now_utc - timedelta(hours=5), url="https://ex.com/4",
            reading_time=15, summary="Summary C1", category_list=[]
        )

    def test_parse_date_rfc822(self):
        """Verify standard RSS RFC 822 date strings parse into timezone-aware datetimes."""
        rfc_str = "Mon, 06 Jul 2026 12:00:00 +0000"
        parsed = parse_date(rfc_str)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.year, 2026)
        self.assertEqual(parsed.month, 7)
        self.assertEqual(parsed.tzinfo, timezone.utc)

    def test_parse_date_iso(self):
        """Verify modern ISO 8601 strings drop cleanly into time-aware instances."""
        iso_str = "2026-07-06T12:00:00Z"
        parsed = parse_date(iso_str)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.hour, 12)
        self.assertEqual(parsed.tzinfo, timezone.utc)

    def test_is_published_in_window(self):
        """Verify the publication window strictly filters out stale content."""
        fresh_date = self.now_utc - timedelta(hours=12)
        stale_date = self.now_utc - timedelta(days=4)
        
        # Assuming a default window check of 1 or 2 days
        self.assertTrue(is_published_in_window(fresh_date, days_limit=1))
        self.assertFalse(is_published_in_window(stale_date, days_limit=1))

    def test_enforce_local_diversity_balancing(self):
        """Ensure the fallback balancer avoids clustering by distributing distinct sources."""
        # Unbalanced pool containing multiple identical sources
        unbalanced_pool = [self.article_a1, self.article_a2, self.article_b1, self.article_c1]
        
        # Enforce diversity extracting top 3 items
        selected = enforce_local_diversity(unbalanced_pool, max_total=3)
        
        self.assertEqual(len(selected), 3)
        
        # Count occurrences per source in selected items
        source_counts = {}
        for art in selected:
            source_counts[art.source] = source_counts.get(art.source, 0) + 1
            
        # The algorithm should have prioritized selecting unique sources before doubling up
        self.assertLessEqual(source_counts.get("Chatham House", 0), 1, "Should balance sources before repeating.")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_briefing_cache_hit(self, mock_file, mock_exists):
        """Confirm that if a clean, unexpired file cache is present, the system loads it directly."""
        mock_exists.return_value = True
        
        # Fake cached data representing a run executed 15 minutes ago
        fake_cache = {
            "timestamp": (self.now_utc - timedelta(minutes=15)).isoformat(),
            "was_expanded": False,
            "synthesis_report": "## Cached Mock Report",
            "articles": [
                {
                    "title": "Cached Title",
                    "source": "Cached Source",
                    "pub_date": self.now_utc.isoformat(),
                    "url": "https://cached.com",
                    "reading_time": 5,
                    "summary": "Cached Summary Data"
                }
            ]
        }
        
        mock_file.return_value.read.return_value = json.dumps(fake_cache)
        
        # Invoke briefing generation loop
        articles, report, was_expanded = get_briefing()
        
        # Assertions prove it bypassed scraping/AI blocks completely
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, "Cached Title")
        self.assertEqual(report, "## Cached Mock Report")
        self.assertFalse(was_expanded)

    @patch("os.path.exists")
    @patch("app.aggregator.get_top_articles")
    @patch("app.aggregator.generate_synthesis_and_briefing")
    def test_get_briefing_cache_miss_calls_ai(self, mock_ai, mock_fetch, mock_exists):
        """Confirm that a cache miss hits the live processing line and generates new files."""
        mock_exists.return_value = False
        mock_fetch.return_value = [self.article_b1, self.article_a1, self.article_c1]
        
        # Mock successful Gemini payload response
        mock_ai.return_value = ([self.article_b1, self.article_a1], "# Live Generated Synthesis")
        
        # Use a localized context patch to swallow filesystem output tracking for code stability
        with patch("builtins.open", mock_open()):
            articles, report, was_expanded = get_briefing()
            
        self.assertEqual(len(articles), 2)
        self.assertEqual(report, "# Live Generated Synthesis")
        mock_ai.assert_called_once()

if __name__ == "__main__":
    unittest.main()