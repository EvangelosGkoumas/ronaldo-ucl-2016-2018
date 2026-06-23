# 🧭 GUIDE — how to run this, and how to build your own sports projects

This guide is for **you** (Evangelos), so you can re-run this project, understand every
part, and build similar ones on your own later — even without any AI helping you.

---

## Part 1 — Running this project on your PC

### One-time setup
1. **Install Python 3.10+** (https://www.python.org/downloads/ — on Windows tick *"Add
   Python to PATH"* during install).
2. Open a terminal (PowerShell on Windows) **in this folder**.
3. (Recommended) create an isolated environment so projects don't clash:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows   (use: source .venv/bin/activate on Mac/Linux)
   ```
4. Install the libraries:
   ```bash
   pip install -r requirements.txt
   ```

### Run it
```bash
python run_all.py
```
- Charts appear in `outputs/`, data tables in `data/processed/`.
- The **first** run downloads data from the internet and caches it in `data/raw/`.
  After that it runs **offline**.
- To force fresh data, delete the files in `data/raw/` and run again.

### Run just one part
```bash
python src/build_dataset.py   # rebuild the dataset only
python src/analyze_sql.py     # just the SQL tables (prints them)
python src/viz_campaign.py    # just the campaign charts
python src/viz_finals.py      # just the StatsBomb finals visuals
```

---

## Part 2 — The reusable recipe (this is the important bit)

**Every** data project — football, basketball, sales, anything — follows the same four
steps. This repo is just one example of the pattern:

```
1. GET     →  download / read the raw data            (build_dataset.py: fetch)
2. CLEAN   →  parse into one tidy table (CSV)          (build_dataset.py: parse + join)
3. ANALYZE →  ask questions with SQL or pandas          (analyze_sql.py)
4. SHOW    →  turn answers into charts + a README        (viz_*.py + README.md)
```

Two habits that make a project look professional:
- **A correctness gate.** Before trusting any chart, check a number you already know is
  true (here: Ronaldo's 16/12/15 goal totals). If it doesn't match, stop and fix.
- **Write down your sources** (`SOURCES.md`) so anyone — a recruiter, a professor — can
  trust the numbers.

### To build a *new* project, copy this folder and change three things:
1. **The data source** in `build_dataset.py` (a new URL / dataset).
2. **The questions** in `analyze_sql.py` (new SQL queries).
3. **The charts** in `viz_*.py` (what you want to show).
The structure, the README format, and the "validate then visualize" habit stay the same.

---

## Part 3 — Free data sources catalog

### ⚽ Football
| Source | What you get | How to access |
|---|---|---|
| [StatsBomb open data](https://github.com/statsbomb/open-data) | Event data (shots, xG, passes, positions) for World Cups, CL finals, Messi's Barça career | `pip install statsbombpy` |
| [openfootball](https://github.com/openfootball) | Match results & fixtures for most leagues/competitions | Plain text files on GitHub |
| [Wikipedia](https://en.wikipedia.org) | Goalscorers, squads, history | `?action=raw` for clean wikitext |
| [Understat](https://understat.com) | xG for the top-5 leagues | `pip install understatapi` |
| [football-data.co.uk](https://www.football-data.co.uk) | Results + betting odds, CSV | Direct CSV download |

### 🏀 Basketball  (used in your Westbrook project)
| Source | What you get | How to access |
|---|---|---|
| [Basketball-Reference](https://www.basketball-reference.com) | Career/season stats, game logs | `pandas.read_html` (works from a normal PC) |
| [nba_api](https://github.com/swar/nba_api) | Official NBA stats, shot charts | `pip install nba_api` (best from a home PC — NBA blocks cloud servers) |
| [Kaggle NBA datasets](https://www.kaggle.com/datasets?search=nba) | Ready-made CSVs | Free Kaggle account |

> ⚠️ Note: some sites (FBref, stats.nba.com) block automated access from cloud servers
> but work fine from your **own computer**. If a download is blocked, try it from your PC.

---

## Part 4 — Using AI to help build future projects (without me)

You won't have this exact setup forever, but you can use **any** AI assistant
(Claude.ai, ChatGPT, Claude Code, GitHub Copilot) to help. The skill is **how you ask**.

A prompt template that works well:
> *"I want to build a football/basketball data analysis project about **[player/team/season]**.
> I have data from **[source]** with these columns: **[list]**. Help me:
> 1) load and clean it into one table, 2) write SQL/pandas to answer **[your questions]**,
> 3) make clear charts. I know basic Python. Explain each step."*

Tips that make AI far more useful:
- **Show it your data** — paste the first few rows / column names. AI guesses badly without it.
- **Ask for one step at a time** ("first just load and print the data"), then build up.
- **Always sanity-check** a number you already know (your correctness-gate habit).
- **Ask "why"** — "explain what this line does" — so you actually learn, not just copy.
- When something breaks, paste the **full error message**; that's usually enough to fix it.

---

## Part 5 — Your next projects (ideas)
- **Westbrook 2016–17 MVP** *(planned)*: triple-double tracker, the chase of Oscar
  Robertson's record, scoring/efficiency by month — data from Basketball-Reference.
- **Olympiacos — UEFA Conference League 2024** *(planned)*: the title-winning run,
  El Kaabi's goals, round-by-round xG — check openfootball/FBref for the data.
- **Extensions here**: add assists, compare Ronaldo vs another forward, or pull a full
  competition from StatsBomb (e.g. a World Cup) to train your own xG model.

---

## Part 6 — Learn more
- *mplsoccer* docs (football pitch charts): https://mplsoccer.readthedocs.io
- *StatsBomb* open-data docs: https://github.com/statsbomb/open-data
- "Friends of Tracking" (football analytics, YouTube) — great free course
- DuckDB SQL docs: https://duckdb.org/docs
- pandas 10-minute intro: https://pandas.pydata.org/docs/user_guide/10min.html

You already do SQL, Python and dashboards at work — this is the **same toolkit** pointed
at the sport you love. Keep one repo per project, keep the README clean, and your GitHub
becomes your football-analyst portfolio. Good luck! 🚀
