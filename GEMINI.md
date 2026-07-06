# Project Instructions: Global Perspectives (Foreign Policy TUI Aggregator)

This document serves as the developer guidelines, architectural manual, and team-shared conventions for the `Global Perspectives` project. Gemini CLI agents and human developers must adhere to these patterns.

---

## 1. System & Architecture Overview

`Global Perspectives` is a visually polished, keyboard-navigable Windows terminal-based aggregator. It fetches foreign policy essays, filters them for long-form analysis, and uses Gemini 2.5 Flash to synthesize them into a systemic macro briefing for policymakers.

### Tech Stack
- **Language**: Python 3.11+
- **Terminal UI**: `rich` (for layouts, panels, and markdown rendering), `questionary` (for interactive terminal prompts/menus).
- **Network & Scraping**: `requests` (HTTP requests), `beautifulsoup4` (HTML/XML parsing, RSS feed parsing, article scraping), `lxml` (underlying parser speed).
- **AI Engine**: `google-genai` SDK (model: `gemini-2.5-flash`).
- **Structured Validation**: `pydantic` (for structural schema definition).

---

## 2. Directory Structure & Map

```
C:\Users\frede\Downloads\statistics-sandbox\
├── GEMINI.md                   # This instruction manual
├── README.md                    # User quick-start & overview
├── requirements.txt            # Project dependencies
├── run.bat                     # Windows CLI entry script (sets up virtual env)
├── app/                        # Main codebase module
│   ├── __init__.py
│   ├── config.py               # Central configuration (feeds, keywords, headers)
│   ├── aggregator.py           # Feed fetching, RSS parser, local diversity logic, and caching
│   ├── ai_service.py           # Google GenAI integration and structured extraction
│   └── main.py                 # Rich TUI interface and interactive application loop
└── tests/                      # Unit testing suite
    └── test_parser.py          # Parsers, date windows, and filters unit tests
```

---

## 3. Core Engine Components & Data Flows

### A. RSS Ingestion & Crawling (`app/aggregator.py`, `app/config.py`)
1. **Source Feeds**: Configuration of target RSS feeds is declared in `app/config.py`.
2. **Filtering**:
   - **Date Window**: Standard target is **yesterday and today** (1-day delta window, utilizing `is_published_in_window`).
   - **Quiet Day Fallback**: If fewer than 2 articles are found, the search automatically expands to 7 days (`days_window=7`).
   - **Keyword/Category Exclusions**: Short-form categories (e.g., podcast, video, newsletter, sitrep, q&a, interview) are strictly filtered out using `EXCLUDED_KEYWORDS` and `EXCLUDED_CATEGORIES`.
3. **Scraping Full Text**: For candidate articles, the full body text is parsed/scraped (`scrape_full_text`) to build a high-fidelity context payload for the AI model.

### B. AI Synthesis Pipeline (`app/ai_service.py`)
- **SDK**: Uses the official `google-genai` library (`genai.Client`).
- **Model**: `gemini-2.5-flash`
- **Output Schema Enforcement**: Native structured output via `response_schema` leveraging Pydantic models:
  - `SelectedArticleSchema`: Links curated selections back to source IDs, estimates reading times, and crafts a 2-sentence summary.
  - `IntelligenceBriefingSchema`: Enforces the top-level response structure containing the overarching `synthesis_report` (Markdown string) and `selected_articles` list.
- **Persona & Style**: Systemic persona (Director of National Intelligence writing for Singaporean policymakers). It analyzes macro trends, grand strategy, regional architectures, and analytical convergence/divergence.

### C. Caching & Resilience (`app/aggregator.py`)
- **Cache File**: `cache_briefing.json`
- **Time-to-Live (TTL)**: 4 hours (`CACHE_TTL_HOURS = 4`). If the cache is fresh, RSS crawling and AI generation are bypassed.
- **Fallback Balancer**: If the Gemini API is unreachable, offline, or lacks an API key:
  1. The engine falls back to a locally computed diversity-preserving curation (`enforce_local_diversity`) picking up to 3 articles (max 1 from the same brand, round-robin style).
  2. A local-only fallback report is rendered to the user.

---

## 4. Development Workflows & Developer Commands

### Environment Setup
The project uses a Python virtual environment `.venv`.
- To initialize and run on Windows:
  ```cmd
  run.bat
  ```
- Manual virtual environment activation:
  ```cmd
  .venv\Scripts\activate.bat
  ```

### Running Tests
Unit tests are located in `tests/`. Run them via unittest discover:
```cmd
.venv\Scripts\python.exe -m unittest discover tests
```
*Note: Currently, there is a mismatch in the `tests/test_parser.py` importing `process_feed_item` from `app.aggregator` which has been refactored. When modifying or refactoring aggregator logic, keep tests in sync.*

### Configuration Guidelines
To add new RSS feeds or modify filters, update `app/config.py`. Never hardcode strings, request timeouts, user agents, or crawling rules outside of `app/config.py`.

---

## 5. Architectural Conventions for AI Agents

1. **Keep Fallbacks Intact**: Always maintain the fallback mechanisms in `app/aggregator.py` and `app/ai_service.py` to ensure the TUI works even if the user lacks a valid `GEMINI_API_KEY`.
2. **Type Safety & Validation**: Maintain clean typing. Always use Pydantic schemas with the `google-genai` model client for robust, structured outputs rather than custom regex or JSON parsing.
3. **RSS & Scraping Politeness**: Always respect the configured user agent and timeouts (`TIMEOUT_SECONDS = 8`) when executing requests.
4. **Rich Styling**: Keep the terminal interface consistent. Use the stylized `Console` and custom red/gold/cyan color scheme defined in `app/main.py`.
