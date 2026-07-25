# CLAUDE.md — article-python-template

## Project Overview

This repository is a **template** for a paper's data-analysis / artifact-generation
pipeline: the small Python project that turns a hand-curated corpus (papers,
survey responses, benchmark results — whatever your empirical study is built
on) into the **figures**, **LaTeX tables**, and **BibTeX** a paper's LaTeX
source consumes.

It ships with a complete, runnable example: a fictional literature review of
empirical studies that mine software failures (memory-safety bugs,
concurrency bugs, dependency/build failures) out of GitHub repositories.
Every paper, title, author, venue, and taxonomy entry in `article/input/` is
invented for demonstration purposes — replace it with your own real corpus
when you start a new article from this template, following the "Adapting
this template" section of [README.md](README.md).

This file documents the conventions the example pipeline follows, so a new
article built from this template can either keep following them (recommended)
or explicitly deviate with the reasons noted here updated.

---

## Iron Rule — Single Data Loader

**Every figure/table/BibTeX script loads data via `data_loader.py`** —
`load_corpus()`, `load_taxonomy()`, `load_failure_observations()`. None of
them read a CSV (or Excel, if you add one) directly.

If your real corpus lives in a hand-curated Excel/Google Sheet rather than a
plain CSV, add **one** script that is the *only* thing allowed to read that
source, and have it write the CSVs `data_loader.py` expects (mirroring
`paper_corpora_to_csv.py` in the `llmroadmap` project this template is
derived from). Every other script keeps loading through `data_loader.py`
rather than the raw source, so there is exactly one place that knows the
source format and exactly one place to fix when that format changes.

## Iron Rule — Unified Color Palette

Every figure/table script **must** import its colors from `article/palette.py`.
Do not define hex color literals locally in a generator script — add the
color to `palette.py` first, then import it.

`palette.py` is organized by the semantically distinct axes the example
figures actually use:

| Symbol | Used for |
|---|---|
| `CATEGORY_ORDER` / `CATEGORY_COLORS` | Paper-level failure category (Memory Safety / Concurrency / Dependency Management) — shared by Fig1 (Sankey), Fig2 (stacked bar), Fig3 (bubble), and reused as the taxonomy's Category level in Fig5/Fig6 |
| `FOCUS_ORDER` / `FOCUS_COLORS` | Taxonomy's top Focus split (Runtime vs. Build Failures) — Fig5 (tree chart), Fig6 (crosstab) |
| `SEVERITY_ORDER` / `SEVERITY_COLORS` | Observation severity (Low/Medium/High) — Fig6 (crosstab) |
| `VENUE_CONF` / `VENUE_JOURNAL` / `VENUE_OTHER`, `CONF_PALETTE` / `JOUR_PALETTE` | Venue-type split and per-venue donut tints — Fig4 (distribution) |
| `lighten()` | Derives a lighter tint of a category color per tree/donut nesting level, instead of hardcoding a second color per level |
| `apply_style()` | Shared matplotlib rcParams (call once per script, before creating any Figure) |
| `BG_TRANSPARENT`, `GRID_COLOR`, `TITLE_COLOR`, `SUBTITLE_COLOR`, `AXIS_COLOR`, `ALL_TITLES` | Shared structural neutrals and the common title font size |

Note that `CATEGORY_ORDER`/`CATEGORY_COLORS` is deliberately reused for both
the paper-level axis (Fig1-4) *and* the taxonomy's Category level (Fig5-6) —
in the example data these are the same three values by design, so the whole
demo tells one coherent story instead of two disconnected vocabularies. If
your real paper's per-paper category and taxonomy category are genuinely
different axes, split them into two palette symbols instead of forcing reuse.

## Iron Rule — Dynamic Output Folders

Nothing needs to exist up front. `config.py` creates `input/`, `outputs/`,
`outputs/figures/`, and `outputs/sheets/` the moment it's imported. Figures
write their real, camera-ready output (PDF, or SVG for the Plotly Sankey) to
`FIGURES_DIR` (the article repo), and a PNG/SVG debug preview to
`OUTPUT_BASE_DIR` (local, gitignored) — never the other way around.

---

## Repository Structure

```
article/
├── input/
│   ├── corpus.csv                # one row per paper (title, year, venue, category, BibTeX)
│   ├── taxonomy.csv              # FOCUS -> CATEGORY -> SUBCATEGORY -> FAILURE_TYPE
│   └── failure_observations.csv  # paper x failure-type x severity join table
├── config.py                     # central path config; reads .env, creates output dirs on import
├── palette.py                    # single source of truth for every color + apply_style()/lighten()
├── data_loader.py                # the only place that reads the three CSVs above
├── crosstab.py                   # failure-type x severity crosstab helper, shared by Fig6
├── generate_bibtex.py            # injects BibTeX entries into the article's biblio.bib
├── generate_tables.py            # renders the paper's LaTeX tables
├── Fig1_sankey.py                # Category -> Venue Sankey (Plotly + kaleido)
├── Fig2_stackedbar.py            # papers per year, stacked by category (matplotlib)
├── Fig3_bubble.py                # Category x Year bubble chart (matplotlib)
├── Fig4_distribution.py          # stacked bar + donuts: venue-type/venue distribution (matplotlib)
├── Fig5_treechart.py             # hierarchical Focus->Category->Subcategory->FailureType tree (matplotlib)
└── Fig6_severitycrosstab.py      # banded stacked bar: failure type usage by severity (matplotlib)
run_pipeline.py                    # entry point — runs bibtex/tables/figures in order
```

### Import convention

Scripts in `article/` use **bare sibling-file imports** (`import config`,
`from data_loader import load_corpus`, `from palette import ...`), not
`from article import ...`. This works because `run_pipeline.py` invokes each
script as a subprocess with `cwd` set to `article/` — Python then puts that
directory (not the project root) at the front of `sys.path`. Do not "fix"
these to absolute-package imports; it will break when run this way.

### One script per figure

Each `Fig*.py` script is independently runnable (`python article/FigN_x.py`)
and owns exactly one figure's visual parameters — no shared "generate all
figures" mega-script. This keeps each figure's header fully self-contained
and configurable, and means a single figure can be regenerated or debugged
in isolation. `run_pipeline.py`'s `figures` phase just runs each in sequence.

---

## Configuration

Paths resolve in [article/config.py](article/config.py) from environment
variables in `.env` (gitignored, see [.env.example](.env.example)):

| Variable | Default | Purpose |
|---|---|---|
| `OUTPUT_BASE_DIR` | `article/outputs/` | Local debug outputs (PNG/SVG figure previews, `citations.txt`) |
| `ARTICLE_OUTPUT_BASE_DIR` | `OUTPUT_BASE_DIR` | Paper artifacts: figures (`figures/`), LaTeX tables (`sheets/`), `biblio.bib` |
| `RP_OUTPUT_BASE_DIR` | `OUTPUT_BASE_DIR` | Companion replication-package repo's `data/` subfolder, if you publish one |
| `INPUT_DIR` | `article/input/` | Where the corpus/taxonomy/observations CSVs are read from |

A default [.env](.env) (gitignored) ships in this checkout with all three
output variables pointed at the local `article/outputs/` folder, so a fresh
checkout runs with zero configuration.

---

## Entry Point

`run_pipeline.py` (project root) regenerates artifacts in dependency order:

```bash
python run_pipeline.py              # all phases: bibtex, tables, figures
python run_pipeline.py figures       # figures only
python run_pipeline.py tables figures  # multiple phases
```

Each phase script runs as `python <script>.py` with `cwd=article/`, matching
the bare sibling-file import convention above. `MPLBACKEND=Agg` is forced so
no matplotlib windows pop up during a batch run.

---

## Adapting this template for a new article

See the "Adapting this template for a new article" section of
[README.md](README.md) for the concrete steps (replacing the CSVs, updating
`palette.py`, swapping in your paper's real figures/tables). Keep this file
updated as you do — if you introduce a genuinely different data source (e.g.
Excel instead of CSV) or split an axis that was reused here, note it here the
same way the Iron Rules above are documented, so future-you (or a future
contributor) knows the rule was a deliberate choice and not an oversight.
