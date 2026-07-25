[![CI](https://github.com/augustocristian/article-python-template/actions/workflows/ci.yml/badge.svg)](https://github.com/augustocristian/article-python-template/actions)
[![Quality gate status](https://sonarcloud.io/api/project_badges/measure?project=augustocristian_article-python-template&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=augustocristian_article-python-template)

# article-python-template

Starter template for an article's **data-analysis / artifact-generation pipeline**: the
kind of small Python project that turns a hand-curated corpus of articles (or any
other structured dataset backing a literature review / empirical study) into the
**figures**, **LaTeX tables**, and **BibTeX** an article's LaTeX source consumes.

It's a distillation of the pipeline used for a real JSS submission
(`llmroadmap`), stripped down to the reusable pattern: one **data loader**, one
**color palette**, a handful of small generator scripts (one per figure/table),
all wired together by a single **orchestrator**. Clone this repo to start a new
article's pipeline instead of rebuilding this scaffolding from scratch each time.
See [CLAUDE.md](CLAUDE.md) for the full architecture and the conventions
("Iron Rules") the example pipeline follows.

## The example dataset

Everything in `article/input/` is **invented** for demonstration — a fictional
literature review of empirical studies that mine software failures (memory
bugs, concurrency bugs, dependency/build failures) out of GitHub repositories:

| File                       | Content                                                                                                        |
|----------------------------|----------------------------------------------------------------------------------------------------------------|
| `corpus.csv`               | 48 articles across 17 venues (conferences, journals, and arXiv preprints) — title, year, venue + venue type, source database, failure category, detection phase, detector, BibTeX key/entry |
| `taxonomy.csv`             | The failure-type taxonomy: `FOCUS -> CATEGORY -> SUBCATEGORY -> FAILURE_TYPE`                                  |
| `failure_observations.csv` | Which article observed which failure type, at what severity — the join table the crosstab figure aggregates over |

## What's in here

```
article/
├── input/
│   ├── corpus.csv                # sample corpus — replace with your real articles
│   ├── taxonomy.csv               # sample taxonomy — replace with your real one
│   └── failure_observations.csv   # sample article<->taxonomy join table
├── config.py                      # central path config; reads .env, creates output dirs on the fly
├── palette.py                     # single source of truth for every color + apply_style()/lighten()
├── data_loader.py                  # the only place that reads the CSVs above
├── crosstab.py                     # failure-type x severity crosstab helper (used by Fig6)
├── generate_bibtex.py               # injects BibTeX entries into the article's biblio.bib
├── generate_tables.py               # renders the article's LaTeX tables
├── Fig1_sankey.py                   # Sankey (Plotly): Source -> Detection phase -> Detector
├── Fig2_stackedbar.py               # Stacked bar: articles per year, by category
├── Fig3_bubble.py                   # Bubble chart: Category x Year, bubble size = count
├── Fig4_distribution.py             # Bar + donuts: articles per year, venue-type/venue distribution
├── Fig5_treechart.py                # Hierarchical tree chart of the failure taxonomy (2 PDFs)
└── Fig6_severitycrosstab.py         # Banded stacked bar: failure-type usage by severity (2 PDFs)
run_article.py                      # entry point — runs bibtex/tables/figures in order
CLAUDE.md                            # architecture + conventions ("Iron Rules") this pipeline follows
.github/workflows/                   # CI (lint + SonarCloud)
```

## Setup

```bash
# Install Poetry if you don't have it: https://python-poetry.org/docs/#installation
poetry install

# Or, without Poetry:
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
pip install -e .
```

### Configuring paths (`.env`)

A default [.env](.env) (gitignored) already ships in this checkout, pointing
every output destination at the same local `article/outputs/` folder — so
the pipeline runs end-to-end with zero configuration. When you have a real
article repo (and, optionally, a companion replication-package repo), point
`ARTICLE_OUTPUT_BASE_DIR` / `RP_OUTPUT_BASE_DIR` at them instead; see
[.env.example](.env.example) for the full variable reference and commented-out
examples.

| Variable                  | Default            | Purpose                                                                           |
|---------------------------|--------------------|-----------------------------------------------------------------------------------|
| `OUTPUT_BASE_DIR`         | `article/outputs/` | Local debug outputs (PNG/SVG figure previews, `citations.txt`)                    |
| `ARTICLE_OUTPUT_BASE_DIR` | `OUTPUT_BASE_DIR`  | Article artifacts: figures (`figures/`), LaTeX tables (`sheets/`), and `biblio.bib` |
| `RP_OUTPUT_BASE_DIR`      | `OUTPUT_BASE_DIR`  | Companion replication-package repo's `data/` subfolder, if you publish one        |
| `INPUT_DIR`               | `article/input/`   | Where the corpus/taxonomy/observations CSVs are read from                         |

## Running the pipeline

```bash
python run_article.py              # all phases: bibtex, tables, figures
python run_article.py figures       # figures only
python run_article.py tables figures  # multiple phases
```

Run it as-is to see all six example figures, the sample table, and the BibTeX
injection work end-to-end before wiring in your own data.

## Adapting this template for a new article

1. Replace `article/input/corpus.csv`, `taxonomy.csv`, and
   `failure_observations.csv` with your real data (same semicolon-separated
   CSV shape, or point `data_loader.py` at whatever your actual source format
   is — see the "Single Data Loader" Iron Rule in [CLAUDE.md](CLAUDE.md) if
   your real source is Excel/a Google Sheet rather than a CSV).
2. Update the semantic axes in `palette.py` — `SOURCE_*`, `DETECTION_*`,
   `DETECTOR_*`, `CATEGORY_*`, `FOCUS_*`, `SEVERITY_*`, `VENUE_*` (or add new
   ones) — to match your article's actual taxonomy. Keep them drawn from the soft
   base hues at the top of the file so one entity keeps one color across every
   figure.
3. Replace the placeholder chart(s) in `Fig1`–`Fig6` and the placeholder table
   in `generate_tables.py` with your article's real figures and tables — keep
   loading data via `data_loader` and colors via `palette`.
4. Point `ARTICLE_OUTPUT_BASE_DIR` (via `.env`) at your actual article repo once
   one exists, and make sure it has a `biblio.bib` with
   `% AUTOGENERATED-BIBTEX-START` / `% AUTOGENERATED-BIBTEX-END` marker
   comments (created automatically on first run if the file doesn't exist yet).
5. Rename the `article` package (and update `pyproject.toml`'s
   `packages = [{ include = "article" }]` and `run_article.py`'s
   `SCRIPTS_DIR`) to something specific to your article, if you want.
6. Update [CLAUDE.md](CLAUDE.md) if you deviate from any of its conventions
   (e.g. splitting `CATEGORY_COLORS` into two separate axes, or adding an
   Excel-reading script) so the reasoning is documented, not just the code.

## CI and dependency updates

- [.github/workflows/ci.yml](.github/workflows/ci.yml) — lints with flake8
  and runs a SonarCloud scan. No test suite ships with this template (it's
  just data-pipeline scripts that produce figures/tables/BibTeX, not a
  library meant to be packaged or published); if you add tests to a project
  generated from this template, reintroduce a pytest step and uncomment the
  coverage line in [sonar-project.properties](sonar-project.properties).
- [.github/dependabot.yml](.github/dependabot.yml) — monthly PRs for pip and
  GitHub Actions dependency updates.

See the general contribution policies and guidelines for *giis-uniovi* at
[CONTRIBUTING.md](https://github.com/giis-uniovi/.github/blob/main/profile/CONTRIBUTING.md).
