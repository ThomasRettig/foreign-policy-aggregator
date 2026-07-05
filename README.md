# Global Perspectives - Foreign Policy TUI Aggregator

`Global Perspectives` is a visually striking, keyboard-navigable Windows CLI tool built in Python 3.11+. It automatically aggregates, filters, and summarizes the top 2-3 long-form foreign policy essays and analyses published yesterday or today.

## Sources
* **Foreign Affairs** (Published by the Council on Foreign Relations)
* **Foreign Policy Magazine**
* **War on the Rocks**

---

## Prerequisites
* **Python 3.11+** installed and added to your System PATH.
* Active Internet Connection (to fetch feeds and scrape articles).

---

## Quick Start (Windows)
Double-click the **`run.bat`** file in the root directory. 

This batch script will automatically:
1. Initialize a Python virtual environment (`.venv`).
2. Upgrade `pip` and install all required libraries (`rich`, `questionary`, `requests`, `beautifulsoup4`).
3. Boot up the TUI menu.

---

## Keyboard Controls
The interface is built with `questionary` and is fully interactive:
* **Arrow Keys ($\uparrow$ / $\downarrow$)** to move between selections.
* **Enter** to confirm choice or drill down.
* **Ctrl+C** to exit the application immediately at any point.

---

## How It Works Under the Hood

### 1. Date Validation
* Feeds are parsed dynamically using standard RFC 822 parser (`email.utils.parsedate_to_datetime`).
* Dates are converted into timezone-aware objects and matched strictly against the local reader's **yesterday** and **today**.
* **Quiet News Day Handling**: If fewer than 2 articles are published in this 24-48h window (e.g. over weekends/holidays), the tool automatically expands the search range to the past 7 days to guarantee you always have analysis to read.

### 2. "Long-Form" Heuristic Filtering
* First, articles matching short-form categories (like *Podcast, Sitrep, Brief, Event, Newsletter*) or URL slug keywords are filtered out.
* The script crawls the article's web page body to count words:
  * A reading time of $\ge 7$ minutes is defined as $\ge 1,400$ words (calculated at an average reading speed of 200 words per minute).
  * If a paywall blocks crawling (returning preview text < 500 words), but the source category is verified as an essay or analysis, the tool applies a default read time fallback (e.g. 10 minutes) and preserves the item.

### 3. Editorially-Grounded Summarization
Instead of using latency-prone or cost-heavy LLM APIs, the tool creates a clean 2-sentence summary:
* **Sentence 1**: Extracted from the RSS feed's editorially written deck/description tag (HTML cleaned).
* **Sentence 2**: The first narrative sentence of the article body, obtained by scraping the first body paragraph that is long enough and filtering out author/copyright metadata.
* This results in highly informative, professional 2-sentence summaries.
