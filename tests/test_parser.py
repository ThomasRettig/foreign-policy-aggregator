import unittest
from datetime import datetime, timezone, timedelta
from app.aggregator import (
    parse_date, is_published_in_window, process_feed_item
)

class TestParser(unittest.TestCase):
    def test_parse_date_rfc822(self):
        """Verify that RFC 822 publication dates are correctly parsed."""
        date_str = "Fri, 03 Jul 2026 12:00:53 +0000"
        dt = parse_date(date_str)
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 7)
        self.assertEqual(dt.day, 3)

    def test_parse_date_iso(self):
        """Verify that ISO 8601 publication dates are correctly parsed."""
        date_str = "2026-07-04T12:00:00Z"
        dt = parse_date(date_str)
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 7)
        self.assertEqual(dt.day, 4)

    def test_is_published_in_window(self):
        """Verify that date window check operates correctly."""
        now = datetime.now(timezone.utc)
        # Current time should always match a 1-day window
        self.assertTrue(is_published_in_window(now, days_limit=1))

        # Verification for the new rolling 2-day target window
        yesterday_piece = now - timedelta(hours=36)
        self.assertTrue(is_published_in_window(yesterday_piece, days_limit=2))

        # Date from 10 days ago should be excluded
        past_date = now - timedelta(days=10)
        self.assertFalse(is_published_in_window(past_date, days_limit=2))

    def test_process_mock_item_exclusions(self):
        """Verify that short-form categories or title keywords are correctly filtered out."""
        # 1. Test podcast categories filter out
        podcast_item = {
            "title": "Global Briefing Today",
            "link": "https://foreignpolicy.com/2026/07/03/briefing-today/",
            "pubDate": "Fri, 03 Jul 2026 12:00:53 +0000",
            "description": "Weekly briefing audio stream.",
            "categories": ["Podcast"]
        }
        res = process_feed_item(podcast_item, "foreign_policy")
        self.assertIsNone(res)

        # 2. Test URL/title brief keywords filter out
        brief_item = {
            "title": "Latin America Brief",
            "link": "https://foreignpolicy.com/2026/07/03/venezuela-brief/",
            "pubDate": "Fri, 03 Jul 2026 12:00:53 +0000",
            "description": "Briefing page of Latin America.",
            "categories": ["Analysis"]
        }
        res = process_feed_item(brief_item, "foreign_policy")
        self.assertIsNone(res)

if __name__ == "__main__":
    unittest.main()
