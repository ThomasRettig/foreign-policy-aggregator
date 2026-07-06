# Foreign Policy Aggregator

A terminal-based interactive tool that automatically aggregates long-form research, creates cross-cutting macroeconomic and geopolitical intelligence reports using advanced AI models, and provides an adversarial interrogation sandbox to stress-test authorial claims.

---

## ✨ Core Operational Features

* **Cross-Cutting AI Synthesis:** Moves beyond simple chronological summaries. The intelligence engine reads full-text articles and maps macro-strategic vectors, analytical tensions, and structural points of convergence or disagreement across publications.
* **Adversarial Interrogation Deck (New):** Spin up a live, multi-turn, persistent chat session with an elite AI Intelligence Critic to challenge and stress-test the underlying assumptions, omitted evidence, and institutional slants of any single article.
* **Guaranteed Schema Fidelity:** Powered by native **Pydantic Structured Outputs** via the Google GenAI SDK. Eliminates wire-level JSON parsing and delimiter failures.
* **Uncapped Token Buffering:** Configured with a max output capacity of **8,192 tokens**, providing deep analytical essays without premature truncation or cut-offs.
* **Resilient Intelligent Caching:** A highly optimized local filesystem cache layer prevents duplicate API requests. Identical workloads load instantly ($<0.01$ seconds) while remaining valid for a rolling 4-hour Time-To-Live (TTL) window.

---

## 📋 Registry of Supported Data Sources

The aggregator targets high-fidelity, long-form institutional policy research, recently expanded to capture deep-dive European and trans-Atlantic insights:

| Source Registry | Focus Arena | Analytical Vector |
| --- | --- | --- |
| **Chatham House** | Global Governance & Security | Grand Strategy, Regional Architectures |
| **Project Syndicate** | Macroeconomics & Development | Global Finance, Structural Shifts |
| **European Council on Foreign Relations (ECFR)** | European Foreign Policy | Transatlantic Ties, Sovereignty Dynamics |
| **RAND Corporation** | Security & Defense Policy | Military AI, Quantitative Risk Frameworks |
| **Brookings Institution** | Domestic & Foreign Policy | Trade Vectors, Tech Supply Chain Resilience |

---

## 🛠️ Architecture & Tech Stack

* **Intelligence Core:** `gemini-2.5-flash` — Selected for its massive 1-million token context window, structured JSON enforcement alignment, and exceptional blended-token cost efficiency.
* **Data Validation Canvas:** `pydantic` (v2) — Guarantees strict serialization schema validation across the API wire.
* **Terminal User Interface:** `rich` and `questionary` — Renders highly scannable, stylized UI panels, clean markdown trees, dynamic status spinners, and interactive prompt blocks inside standard terminal layouts.

---

## 🚀 Quick Start & Installation

### 1. Environment Configuration

Clone this repository to your target directory and ensure you have Python 3.11+ available. Set your API credentials in your environment layout:

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-api-key-here"

# Linux / macOS Bash
export GEMINI_API_KEY="your-api-key-here"

```

### 2. Initialization

Execute the main bootstrap automated command sequence package script to assemble virtual dependencies and boot the application workspace:

```bash
run.bat

```

---

## 🕹️ Operational Workflow Map

```
                     [ run.bat Launcher ]
                              │
                              ▼
               [ Check cache_briefing.json ]
               ╱                           ╲
     (Cache Hit)        (Cache Miss / Manual Refresh)
           ╱                                       ╲
          ▼                                         ▼
[ Load Instantly from Disk ]             [ Scrape OSINT RSS Channels ]
          │                                         │
          │                                         ▼
          │                            [ Pipe Full-Text to Gemini ]
          │                                         │
          ▼                                         ▼
 ───────────────────────────────────────────────────────────────
                      MAIN DASHBOARD WINDOW
 ───────────────────────────────────────────────────────────────
  ├── 1. View AI Cross-Cutting Synthesis Report (Full Markdown)
  ├── 2. Read Curated Deep Dives (Selected Source Articles)
  │       └── 💬 Interrogate This Analysis (Adversarial Q&A Deck)
  ├── 3. Refresh Feed (Bypasses & forces cache overwrite)
  └── 4. Exit

```

> **Adversarial Q&A Prompt Tip:** When entering the Interrogation Cockpit, push past simple summaries. Challenge the engine with prompts like: *"Identify three systemic dependencies or unstated geographic vulnerabilities the author downplayed in this piece."*

---

## 🧪 Automated Regression Validation

To ensure structural parser components, date normalization matrices, local balancing algorithms, and mockup system integration contexts remain stable, run the integrated testing module:

```bash
.venv\Scripts\python -m unittest tests/test_parser.py

```
