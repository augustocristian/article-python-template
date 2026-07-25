# CLAUDE.md — article-python-template

## Project Overview

This is a **template** for an article's data-analysis / artifact-generation
pipeline: the small Python project that turns a hand-curated corpus (articles,
survey responses, benchmark results — whatever the study is built on) into the
**figures**, **LaTeX tables**, and **BibTeX** the article's LaTeX source consumes.

Everything under `article/input/` is invented sample data — a fictional review of
empirical studies that mine software failures out of GitHub repositories — so a
fresh clone runs end-to-end before any real data exists. See
[README.md](README.md) for setup and the step-by-step adaptation checklist.

**Starting a new article from this template?** Keep the Iron Rules below. Replace
the sample data, the palette's semantic axes, and the figures themselves. If you
deliberately break a rule, update it here so the deviation reads as a decision
rather than an oversight.

---

## Iron Rule — Single Data Loader

**Every figure/table/BibTeX script loads data through `data_loader.py`** —
`load_corpus()`, `load_taxonomy()`, `load_failure_observations()`,
`build_hierarchy_lookups()`. Nothing else opens a CSV.

If the real corpus lives in a hand-curated Excel/Google Sheet, add **one**
converter script that is the only thing allowed to read that source and have it
write the CSVs `data_loader.py` expects. Everything else keeps loading through
`data_loader.py`, so exactly one file knows the source format.

Shared *data* preparation used by more than one figure goes in its own helper
module (`crosstab.py` is the example) — data only, no plotting.

## Iron Rule — Unified Color Palette

Every figure/table script **must** import its colors from `article/palette.py`.
Never write a hex literal, an `rgba(...)` string, or a font name in a generator
script — add it to `palette.py` first, then import it.

**Import by name, never by attribute.** Use `from palette import CATEGORY_COLORS,
ALL_TITLES`, not `import palette` + `palette.CATEGORY_COLORS`. Two placements
are conventional:

```python
from palette import apply_style; apply_style()   # top of file, before any Figure
...
# ── Colors (imported from master palette) ─────────────────────────────────────
from palette import (
    CATEGORY_ORDER, CATEGORY_COLORS, NEUTRAL_FALLBACK,
)
BAR_EDGE_COLOR = "white"        # figure-local constants derived from them
```

The colour import block lives *inside* the header's `# ── Colors ──` section,
next to the constants derived from it. `apply_style()` is called on its import
line so the style is set before any Figure exists. Both trip `E402`/`E702`,
which [.flake8](.flake8) ignores deliberately.

What `palette.py` provides:

| Symbol | Used for |
|---|---|
| `FONT_FAMILY` / `TEXT_COLOR` / `TEXT_STROKE` / `apply_style()` / `text_effects()` | Shared typography. `apply_style()` sets matplotlib's global font + text color; Plotly scripts import `FONT_FAMILY` and pass it to `fig.update_layout(font=...)`, since Plotly ignores matplotlib rcParams |
| `RED`/`ORANGE`/`YELLOW`/`GREEN`/`TEAL`/`CYAN`/`BLUE`/`PURPLE`/`PINK` (+ `_DEEP` variants) | The soft Pantone-style base hues every semantic axis draws from |
| `SOURCE_*` / `DETECTION_*` / `DETECTOR_*` | Fig1's three Sankey columns — the **color anchors** for the article |
| `CATEGORY_*` (article-level), `TAXONOMY_CATEGORY_COLORS`, `FOCUS_*`, `SEVERITY_*`, `VENUE_*` | Semantic axes for Fig2-6, deliberately reusing the anchor hues |
| `lighten()` / `graduated_palette()` / `subcategory_colors()` / `severity_palette()` | Derive tints and n-step ramps instead of hardcoding a color per level |
| `rgba()` | Semi-transparent link ribbons for Plotly, so figures never hand-write rgba literals |
| `NEUTRAL_*`, `GRID_COLOR`, `TITLE_COLOR`, `AXIS_COLOR`, `CONNECTOR_COLOR`, `BG_TRANSPARENT` | Structural neutrals |
| `ALL_TITLES` / `DEBUG_DPI` | Cross-figure knobs: shared title size and debug-preview resolution |

**One entity, one color.** The same value carries the same hue in every figure —
Fig1's node colors are the anchors, and `CATEGORY_COLORS` / `VENUE_TYPE_COLORS`
reuse them so a reader learns each hue once. Keep that property when you swap in
a real taxonomy: if two axes are genuinely unrelated, give them distinct hue
families rather than repeating one arbitrarily.

**`CATEGORY_COLORS` vs. `TAXONOMY_CATEGORY_COLORS` — a worked example of
splitting, not reusing.** `corpus.csv`'s own `CATEGORY` column only ever has
the three broad, article-level values (`CATEGORY_ORDER`, used by Fig1-4). But
`taxonomy.csv`'s `CATEGORY` level has many more, finer-grained values — one
whole subtree per Focus group (used by Fig5's tree chart and Fig6's crosstab
bands). These are genuinely different axes that happen to share three names
(Memory Safety, Concurrency, Dependency Management), so `TAXONOMY_CATEGORY_COLORS`
is its own dict: entries that share a name with an article-level category keep
that category's color (still "one entity, one color"); the rest get a fresh
hue, chosen so the categories under one Focus never collide with each other
or with that Focus's own `FOCUS_COLORS` entry. Follow this pattern — a
separate `TAXONOMY_*` dict, not a bigger shared one — whenever you outgrow a
shared axis instead of forcing the reuse further.

## Iron Rule — Header-Configurable Figures

Every `Fig*.py` declares **all** visual parameters as named constants in
banner-commented header sections, before any plotting logic — never as a bare
literal inside a `plt.subplots(...)`, `ax.bar(...)`, or Plotly call. Re-tuning a
figure must always be a one-line header edit.

Conventional sections, in order, using whichever a figure needs:

```
# ── Output / config ──   filenames, titles, panel configs, toggles
# ── Colors ──            palette imports + derived color constants
# ── Fonts (all font sizes, in points) ──   FS_* constants
# ── Wrap widths (characters per line) ──   text wrapping
# ── Layout ──            FIG_W/FIG_H, margins, padding, gaps, positions, rotations
# ── Style (line widths / dash styles / alphas) ──
```

**Must be a constant:** every font size, dimension, margin, gap, line width,
alpha, marker size, rotation, dash style, legend location/anchor, output
filename and title string.

**May stay inline:** qualitative structure that isn't a tunable magnitude —
which spines to hide, whether a title exists, the shape of a data transform.
If someone might plausibly want to tune the number without touching logic, it
is a header constant.

**Cross-figure knobs belong in `palette.py`**, not duplicated per script —
`ALL_TITLES` and `DEBUG_DPI` are the current examples.

## Iron Rule — One Script Per Figure

Each `Fig*.py` is independently runnable (`python article/FigN_x.py`) and owns
exactly one figure — no shared "generate all figures" module. A figure can be
regenerated or debugged in isolation; `run_article.py` just runs them in
sequence. A script may emit several *files* when it renders the same design per
group (Fig5 and Fig6 each produce one PDF per Focus group).

## Iron Rule — Dynamic Output Folders

Nothing needs to exist up front: `config.py` creates every output directory on
import. Camera-ready output (PDF, or SVG for Plotly) goes to `FIGURES_DIR` /
`SHEETS_DIR` — the article repo. Debug previews (PNG, SVG) go to
`OUTPUT_BASE_DIR`, which is local and gitignored. Never the other way around.

## Iron Rule — Import Convention

Scripts in `article/` use **bare sibling-file imports** (`from config import
FIGURES_DIR`, `from data_loader import load_corpus`, `from palette import ...`),
not `from article import ...`. `run_article.py` runs each script as a subprocess
with `cwd=article/`, which puts that directory at the front of `sys.path`. Do not
"fix" these to package-absolute imports — it breaks the pipeline.

## Iron Rule — BibTeX Formatting

Every `BIBTEX` cell in `corpus.csv` — and anything `generate_bibtex.py` writes
into `biblio.bib` — follows one fixed structure. This is also the standard to
apply when a user pastes a raw entry (DBLP, ACM/IEEE export, arXiv, RIS) for
conversion.

**General rules**
- Replace every `""` quote with `{}` braces.
- Field order must match the applicable template exactly — don't add fields the
  template omits, don't drop fields it lists (use `{}` when the value is unknown).
- Title is always **single**-braced (`title = {...}`) — never `{{...}}`, in any
  template.
- Citation key: `{FirstAuthorLastName}{VenueOrJournalAbbreviation}{Year}`, no
  spaces or punctuation. On a collision append `a`/`b`/… to the later entries.
  Corporate/standards authors get a short tag instead of a surname (`ISO247652017`).
- **ASCII-only keys.** A citation key must never contain a non-ASCII character,
  even when the author's name does (ç, ë, ö, ü, …). Transliterate for the key
  only (Müller → `Muller…`); the `author` field keeps the real UTF-8 spelling.
- Author names: `Last, First`, joined with ` and `. Keep accented characters as
  literal UTF-8 in `author`/`title` — no LaTeX escapes like `\"{o}`.
- Corporate authors are double-braced: `author = {{ISO/IEC/IEEE}}`.
- **Escape LaTeX special characters** in every value: `$ % & # _ ~ ^ \` become
  `\$ \% \& \# \_ \textasciitilde{} \textasciicircum{} \textbackslash{}`.
- Pages use double-dash ranges (`103--110`). Article-number-only entries use the
  bare number (`pages = {230}`).
- `doi`: bare DOI, no `https://doi.org/` prefix; lowercase unless case is
  semantically part of the identifier.
- `url`: `https://doi.org/{doi}` when a DOI exists, else the source URL. Never
  let the two fields disagree on casing.
- Always strip: `number` (unless needed to derive the series abbreviation),
  `month` (except where a template lists it), `editor`, `collection`, `note`,
  `organization`, `abstract`, `keywords`, `isbn`, `numpages`, `issue`,
  `articleno` (fold into `pages`), `issue_date`, `location` (use as `address`),
  `lccn`.
- Expand abbreviated venue names ("ACM Comput. Surv." → "ACM Computing Surveys").
- Fix title typos and lowercase acronyms (`bleu` → `BLEU`, `llms` → `LLMs`)
  without otherwise rewording the title.
- Standardize `publisher` by venue family: IEEE → IEEE Computer Society, ACM →
  Association for Computing Machinery, Elsevier → Elsevier BV, Springer →
  Springer Science and Business Media LLC, Nature → Nature Publishing Group,
  AAAS → American Association for the Advancement of Science, NeurIPS → Curran
  Associates Inc., Wiley → Wiley, SAGE → SAGE Publications, ACL/NAACL/EMNLP →
  Association for Computational Linguistics. Leave `{}` rather than invent a
  publisher for a venue that has none.
- Fix geographic typos in `address` ("Freemont" → "Fremont").
- `series` (InProceedings only): `{VenueAbbreviation} '{YY}` (e.g. `FSE '24`),
  inferred from `booktitle` when missing.

**`@article`**
```
@article{AuthorJournalYear, author = {...}, journal = {...}, title = {...}, year = {...}, volume = {}, ISSN = {}, pages = {}, doi = {}, url = {}, publisher = {}}
```

**`@InProceedings`** (`@inproceedings`/`@INPROCEEDINGS`/any casing map here)
```
@InProceedings{AuthorVenueYear, author = {...}, booktitle = {...}, series = {}, title = {...}, year = {}, volume = {}, ISSN = {}, pages = {}, doi = {}, url = {}, publisher = {}, address = {}, month = {}}
```
`series` follows `booktitle`; `address`/`month` come last.

**`@misc`** (arXiv preprints, datasets, repositories, standards)
```
@misc{AuthorArXivYear, title = {...}, author = {...}, archivePrefix = {arXiv}, year = {...}, publisher = {arXiv}, doi = {}, url = {}}
```
For arXiv: `doi = {10.48550/arXiv.XXXX.XXXXX}` built from the eprint ID, `url`
mirroring it, and drop `eprint`/`primaryClass`. For other sources swap
`archivePrefix`/`publisher` to the real one (`GitHub`, `UCI`, `SSRN`, …).

**`@book` / `@inbook` — no locked template; ask first.** For `@book`: fix quotes,
add an `AuthorShortTitleYear` key, reformat authors, strip `isbn`/`lccn`, and ask
whether to formalize a template. For `@inbook`: ask before formatting at all.

**Uncovered types or missing data.** Never force `@phdthesis`, a bare
`@techreport`, etc. into an existing template — offer 2-3 concrete options. If
`author` or another required field is missing, ask rather than fabricate.

When converting an entry in chat: a one-line intro, the entry in a `bibtex` code
fence, a "Changes made" bullet list, then "Ready for more!" — nothing else unless
clarification is genuinely needed.

---

## Repository Structure

```
article/
├── input/
│   ├── corpus.csv                # one row per article: venue/type, source, category,
│   │                             #   detection phase, detector, BibTeX
│   ├── taxonomy.csv              # FOCUS -> CATEGORY -> SUBCATEGORY -> FAILURE_TYPE
│   └── failure_observations.csv  # article x failure-type x severity join table
├── config.py                     # path config from .env; creates output dirs on import
├── palette.py                    # every color + typography + ramp helpers
├── data_loader.py                # the only module that reads the CSVs
├── crosstab.py                   # failure-type x severity aggregation (data only)
├── generate_bibtex.py            # injects BibTeX between markers in biblio.bib
├── generate_tables.py            # LaTeX tables -> SHEETS_DIR
├── Fig1_sankey.py                # Source -> Detection phase -> Detector (Plotly)
├── Fig2_stackedbar.py            # articles per year, stacked by category
├── Fig3_bubble.py                # Category x Year bubble chart
├── Fig4_distribution.py          # per-year bar + venue-type/venue donuts
├── Fig5_treechart.py             # taxonomy tree (one PDF per Focus group)
└── Fig6_severitycrosstab.py      # failure type x severity (one PDF per Focus group)
run_article.py                    # entry point — bibtex, tables, figures
```

## Configuration

Paths resolve in [article/config.py](article/config.py) from `.env` (gitignored;
see [.env.example](.env.example)). A default `.env` points every output at the
local `article/outputs/`, so a fresh clone runs with zero configuration.

| Variable | Default | Purpose |
|---|---|---|
| `OUTPUT_BASE_DIR` | `article/outputs/` | Local debug previews, `citations.txt` |
| `ARTICLE_OUTPUT_BASE_DIR` | `OUTPUT_BASE_DIR` | Article artifacts: `figures/`, `sheets/`, `biblio.bib` |
| `RP_OUTPUT_BASE_DIR` | `OUTPUT_BASE_DIR` | Companion replication-package repo's `data/`, if any |
| `INPUT_DIR` | `article/input/` | Where the CSVs are read from |

## Entry Point

```bash
python run_article.py                 # all phases: bibtex, tables, figures
python run_article.py figures         # one phase
python run_article.py tables figures  # several
```

Each script runs as `python <script>.py` with `cwd=article/`. `MPLBACKEND=Agg`
is forced so no matplotlib windows open during a batch run.
