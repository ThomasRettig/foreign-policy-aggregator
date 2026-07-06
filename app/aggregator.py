import re
import email.utils
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from collections import defaultdict
import requests
from bs4 import BeautifulSoup

from app.config import FEEDS, HEADERS, TIMEOUT_SECONDS, EXCLUDED_KEYWORDS, EXCLUDED_CATEGORIES
from app.ai_service import generate_synthesis_and_briefing

@dataclass
class Article:
    title: str
    source: str
    pub_date: datetime
    url: str
    reading_time: int
    summary: str
    category_list: list
    full_text: str = ""  # Enhanced to carry full contextual text payload

def parse_date(date_str: str) -> datetime:
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

def is_published_in_window(pub_date: datetime, days_limit: int = 1) -> bool:
    if not pub_date:
        return False
    now = datetime.now(timezone.utc)
    return (now - pub_date.astimezone(timezone.utc)) <= timedelta(days=days_limit)

def scrape_full_text(url: str) -> str:
    """Scrape article web page to extract raw text content body for AI context compilation."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
        if r.status_code != 200:
            return ""
        
        soup = BeautifulSoup(r.text, 'html.parser')
        article_elem = soup.find('article')
        paras = article_elem.find_all('p') if article_elem else soup.find_all('p')
        
        cleaned_paras = []
        for p in paras:
            text = p.get_text().strip()
            if len(text) < 50:
                continue
            # Filter standard headers/footers
            if text.startswith(("Follow us", "All contents (c)", "By ", "Published ", "Photo by", "Subscribe to")):
                continue
            cleaned_paras.append(text)
            
        return "\n\n".join(cleaned_paras)
    except Exception:
        return ""

def fetch_feed_items(source_key: str) -> list:
    url = FEEDS[source_key]["url"]
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, 'xml')
        items = []
        for item in soup.find_all('item'):
            title = item.find('title')
            link = item.find('link')
            pub_date = item.find('pubDate') or item.find('date')
            desc = item.find('description')
            items.append({
                'title': title.get_text().strip() if title else '',
                'link': link.get_text().strip() if link else '',
                'pubDate': pub_date.get_text().strip() if pub_date else '',
                'description': desc.get_text().strip() if desc else '',
                'categories': [c.get_text() for c in item.find_all('category')]
            })
        return items
    except Exception:
        return []

def get_top_articles(days_window: int = 1) -> list:
    """Collect items across open feeds and bundle full webpage text arrays."""
    all_articles = []
    for source_key, config in FEEDS.items():
        items = fetch_feed_items(source_key)
        for item in items:
            pub_date = parse_date(item.get("pubDate"))
            if pub_date and is_published_in_window(pub_date, days_limit=days_window):
                article = process_feed_item(item, source_key)
                if article:
                    all_articles.append(article)
                
    all_articles.sort(key=lambda a: a.pub_date, reverse=True)
    return all_articles

def process_feed_item(item: dict, source_key: str, scrape: bool = True) -> Article | None:
    """Process a single feed item: check exclusions, parse fields, and return an Article or None."""
    title = item.get("title", "")
    url = item.get("link", "")
    pub_date = parse_date(item.get("pubDate"))
    
    if not title or not url or any(kw in url.lower() or kw in title.lower() for kw in EXCLUDED_KEYWORDS):
        return None
    if any(any(kw in c.lower() for kw in EXCLUDED_CATEGORIES) for c in item.get("categories", [])):
        return None
        
    config = FEEDS.get(source_key, {})
    fallback_snippet = BeautifulSoup(item.get("description", ""), "html.parser").get_text().strip()
    
    body_content = ""
    if scrape:
        body_content = scrape_full_text(url)
        
    return Article(
        title=title,
        source=config.get("name", source_key),
        pub_date=pub_date,
        url=url,
        reading_time=config.get("default_read_time", 8),
        summary=fallback_snippet[:300] + "..." if len(fallback_snippet) > 300 else fallback_snippet,
        category_list=item.get("categories", []),
        full_text=body_content if body_content else fallback_snippet
    )

def enforce_local_diversity(articles: list, max_total: int = 3) -> list:
    if not articles:
        return []
    grouped = defaultdict(list)
    for a in articles:
        grouped[a.source].append(a)
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
    return selected

import os
import json

CACHE_FILE = "cache_briefing.json"
CACHE_TTL_HOURS = 0.3  # How long to reuse the AI output before regenerating

def get_briefing() -> tuple[list, str, bool]:
    """Generates the briefing collection with a resilient local filesystem cache layer."""
    was_expanded = False
    
    # 1. Check Local File Cache first
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                
            cache_time = datetime.fromisoformat(cached_data["timestamp"])
            # If the cache is newer than 4 hours, bypass the API completely and load instantly!
            if datetime.now(timezone.utc) - cache_time < timedelta(hours=CACHE_TTL_HOURS):
                cached_articles = []
                for a_dict in cached_data["articles"]:
                    cached_articles.append(Article(
                        title=a_dict["title"],
                        source=a_dict["source"],
                        pub_date=datetime.fromisoformat(a_dict["pub_date"]),
                        url=a_dict["url"],
                        reading_time=a_dict["reading_time"],
                        summary=a_dict["summary"]
                    ))
                return cached_articles, cached_data["synthesis_report"], cached_data["was_expanded"]
        except Exception:
            pass # If the cache file is corrupted, silently pass through and rebuild it

    # 2. Cache Miss: Run the normal pipeline
    candidates = get_top_articles(days_window=1)
    if len(candidates) < 2:
        candidates = get_top_articles(days_window=7)
        was_expanded = True
        
    if not candidates:
        return [], "# Zero Intelligence Metrics Found\nNo new updates across RSS source registries.", was_expanded

    candidate_pool = candidates[:8]
    articles, synthesis_report = generate_synthesis_and_briefing(candidate_pool)
    
    if articles:
        # 3. Save to local cache on a successful Gemini run
        try:
            cache_payload = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "was_expanded": was_expanded,
                "synthesis_report": synthesis_report,
                "articles": [
                    {
                        "title": a.title,
                        "source": a.source,
                        "pub_date": a.pub_date.isoformat(),
                        "url": a.url,
                        "reading_time": a.reading_time,
                        "summary": a.summary
                    } for a in articles
                ]
            }
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache_payload, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
            
        return articles, synthesis_report, was_expanded
        
    # Local fallback array matrix if AI elements are unreachable
    fallback_curation = enforce_local_diversity(candidates, max_total=3)
    fallback_report = f"# Local Balancer Mode Active\n\n{synthesis_report}"
    return fallback_curation, fallback_report, was_expanded
    