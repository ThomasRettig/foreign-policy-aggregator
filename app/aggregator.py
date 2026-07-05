import email.utils
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

from app.config import FEEDS, HEADERS, TIMEOUT_SECONDS
from app.ai_service import curate_briefing_with_ai

@dataclass
class Article:
    title: str
    source: str
    pub_date: datetime
    url: str
    reading_time: int
    summary: str
    category_list: list

def parse_date(date_str: str) -> datetime:
    """Parse RFC 822 or ISO dates into timezone-aware datetime objects."""
    if not date_str:
        return None
    try:
        return email.utils.parsedate_to_datetime(date_str)
    except Exception:
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None

def is_published_in_window(pub_date: datetime, days_limit: int = 2) -> bool:
    """Check if the article was published within a target rolling days window."""
    if not pub_date:
        return False
    now = datetime.now(timezone.utc)
    pub_date_utc = pub_date.astimezone(timezone.utc)
    return (now - pub_date_utc) <= timedelta(days=days_limit)

def fetch_feed_items(source_key: str) -> list:
    """Fetch raw items from target RSS feed URL using modern lxml engine."""
    url = FEEDS[source_key]["url"]
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'xml')
        items = []
        for item in soup.find_all('item'):
            title = item.find('title')
            link = item.find('link')
            pub_date = item.find('pubDate')
            desc = item.find('description')
            
            categories = [cat.get_text() for cat in item.find_all('category')]
            
            items.append({
                'title': title.get_text().strip() if title else 'Untitled Article',
                'link': link.get_text().strip() if link else '',
                'pubDate': pub_date.get_text().strip() if pub_date else '',
                'description': desc.get_text().strip() if desc else '',
                'categories': categories
            })
        return items
    except Exception:
        return []

def get_top_articles(days_window: int = 2) -> list:
    """Collect candidate metadata directly from all feeds without slow content scraping."""
    all_articles = []
    for source_key, config in FEEDS.items():
        items = fetch_feed_items(source_key)
        for item in items:
            pub_date = parse_date(item.get("pubDate"))
            if pub_date and is_published_in_window(pub_date, days_limit=days_window):
                # Sanitize summary HTML descriptions
                clean_desc = BeautifulSoup(item.get("description", ""), "html.parser").get_text().strip()
                # Use standard configuration fallbacks for reading time initially
                default_time = config.get("default_read_time", 8)
                
                all_articles.append(Article(
                    title=item.get("title"),
                    source=config.get("name"),
                    pub_date=pub_date,
                    url=item.get("link"),
                    reading_time=default_time,
                    summary=clean_desc[:300] + "..." if len(clean_desc) > 300 else clean_desc,
                    category_list=item.get("categories", [])
                ))
                
    all_articles.sort(key=lambda a: a.pub_date, reverse=True)
    return all_articles

def enforce_local_diversity(articles: list, max_total: int = 3) -> list:
    """Algorithmic backup filter to guarantee source balancing if AI features are offline."""
    if not articles:
        return []
    grouped = defaultdict(list)
    for a in articles:
        grouped[a.source].append(a)
    for source in grouped:
        grouped[source].sort(key=lambda a: a.pub_date, reverse=True)
        
    sorted_sources = sorted(grouped.keys(), key=lambda s: grouped[s][0].pub_date, reverse=True)
    selected = []
    idx = 0
    while len(selected) < max_total:
        added_any = False
        for source in sorted_sources:
            if idx < len(grouped[source]):
                selected.append(grouped[source][idx])
                added_any = True
                if len(selected) == max_total:
                    break
        if not added_any:
            break
        idx += 1
    selected.sort(key=lambda a: a.pub_date, reverse=True)
    return selected

def get_briefing() -> tuple[list, bool]:
    """Generates the main intelligence briefing, prioritizing Gemini AI orchestration."""
    # Step 1: Scan for target window articles
    was_expanded = False
    candidates = get_top_articles(days_window=2)
    
    # Step 2: Quiet Day Handling fallback
    if len(candidates) < 2:
        candidates = get_top_articles(days_window=7)
        was_expanded = True
        
    if not candidates:
        return [], was_expanded

    # Step 3: Run Batch AI Curation
    ai_briefing = curate_briefing_with_ai(candidates)
    if ai_briefing:
        print("[DIAGNOSTIC] Success! Briefing generated via Gemini 1.5 Flash.")
        return ai_briefing, was_expanded
        
    print("[DIAGNOSTIC] Fallback Triggered: Using local round-robin balancing.")
    return enforce_local_diversity(candidates, max_total=3), was_expanded
        
    # Step 4: Resilient Local Fallback if API keys are missing or rate limits hit
    return enforce_local_diversity(candidates, max_total=3), was_expanded
    