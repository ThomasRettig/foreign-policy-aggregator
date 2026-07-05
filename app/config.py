import os

# Target RSS Feeds Configuration
FEEDS = {
    "foreign_affairs": {
        "name": "Foreign Affairs",
        "url": "https://www.foreignaffairs.com/rss.xml",
        "default_read_time": 10,  # minutes fallback
    },
    "foreign_policy": {
        "name": "Foreign Policy",
        "url": "https://foreignpolicy.com/feed/",
        "default_read_time": 9,  # minutes fallback
    },
    "war_on_the_rocks": {
        "name": "War on the Rocks",
        "url": "https://warontherocks.com/feed/",
        "default_read_time": 12,  # minutes fallback
    },
    "european_council_on_foreign_relations": {
        "name": "European Council on Foreign Relations",
        "url": "https://ecfr.eu/feed/?post_type=publication",
        "default_read_time": 10,
    },
    "project_syndicate": {
        "name": "Project Syndicate",
        "url": "https://www.project-syndicate.org/rss",
        "default_read_time": 10,
    },
}

# HTTP Request Configuration
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
TIMEOUT_SECONDS = 8

# Reading Time Calculations
WORDS_PER_MINUTE = 200
LONG_FORM_MIN_READ_TIME = 7  # minutes
LONG_FORM_MIN_WORDS = LONG_FORM_MIN_READ_TIME * WORDS_PER_MINUTE  # 1400 words

# Filtering Lists
# Keywords in title or URL that imply short-form/brief/media content
EXCLUDED_KEYWORDS = [
    "podcast", "video", "audio", "multimedia", "watch", "listen", "event",
    "briefing", "newsletter", "daily brief", "south asia brief", "china brief",
    "latin america brief", "situation report", "sitrep", "briefs", "q&a",
    "interview", "net assessment", "in the news"
]

# Keywords in RSS categories to filter out
EXCLUDED_CATEGORIES = [
    "situation report", "brief", "briefs", "podcast", "podcasts", "audio", "video", 
    "multimedia", "event", "events", "q&a", "interview", "newsletter", "newsletters",
    "latin america brief", "world brief", "china brief", "south asia brief",
    "audio embed", "in the news"
]
