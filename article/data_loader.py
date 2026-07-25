"""Single data access layer — every generator script loads data from here.

If your real corpus lives in a hand-curated Excel/Google Sheet, add one
script (following the pattern of ``paper_corpora_to_csv.py`` in the
``llmroadmap`` project this template is derived from) that is the *only*
thing allowed to read that source, and have it write the CSVs below.
Every other script — figures, tables, BibTeX — should keep loading through
this module rather than reading a source file directly, so there is
exactly one place that knows the source format.

Three input files back this template's sample data:
  - ``corpus.csv``               one row per article (title, year, venue,
                                  category, BibTeX key/entry)
  - ``taxonomy.csv``              the failure-type taxonomy used by the tree
                                  chart: FOCUS -> CATEGORY -> SUBCATEGORY ->
                                  FAILURE_TYPE
  - ``failure_observations.csv``  which article observed which failure type,
                                  and at what severity — the join table the
                                  crosstab figure aggregates over
"""

import pandas as pd

import config


def load_corpus() -> pd.DataFrame:
    """Load the canonical corpus from ``INPUT_DIR/corpus.csv``."""
    return pd.read_csv(config.CORPUS_CSV, sep=";")


def load_taxonomy() -> pd.DataFrame:
    """Load the failure-type taxonomy from ``INPUT_DIR/taxonomy.csv``."""
    return pd.read_csv(config.TAXONOMY_CSV, sep=";")


def load_failure_observations() -> pd.DataFrame:
    """Load the article-to-failure-type join table, one row per observation."""
    return pd.read_csv(config.FAILURE_OBSERVATIONS_CSV, sep=";")


def split_values(cell) -> list[str]:
    """Split a comma-separated cell (e.g. a multi-valued category column)
    into a list of trimmed values. Returns [] for missing/blank cells."""
    if pd.isna(cell):
        return []
    return [v.strip() for v in str(cell).split(",") if v.strip()]


def clean_venue_name(name) -> str:
    """Normalize a venue string for grouping/display (trim, collapse
    internal whitespace). Returns "Unknown" for missing venues."""
    if pd.isna(name):
        return "Unknown"
    return " ".join(str(name).split())


def build_hierarchy_lookups() -> dict:
    """Build the FOCUS -> CATEGORY -> SUBCATEGORY -> FAILURE_TYPE lookups
    the tree chart (Fig5_treechart.py) walks to build its node tree.

    Returns a dict with:
      - "focus_cats":  {focus: [categories]}       (taxonomy order)
      - "cat_to_focus": {category: focus}
      - "cat_subs":    {category: [subcategories]} (taxonomy order)
      - "sub_to_cat":  {subcategory: category}
      - "sub_items":   {subcategory: [failure types]} (taxonomy order)
    """
    df = load_taxonomy()

    focus_cats: dict[str, list[str]] = {}
    cat_to_focus: dict[str, str] = {}
    cat_subs: dict[str, list[str]] = {}
    sub_to_cat: dict[str, str] = {}
    sub_items: dict[str, list[str]] = {}

    for _, row in df.iterrows():
        focus, category, subcategory, item = (
            row["FOCUS"], row["CATEGORY"], row["SUBCATEGORY"], row["FAILURE_TYPE"],
        )
        if category not in focus_cats.setdefault(focus, []):
            focus_cats[focus].append(category)
        cat_to_focus[category] = focus

        if subcategory not in cat_subs.setdefault(category, []):
            cat_subs[category].append(subcategory)
        sub_to_cat[subcategory] = category

        sub_items.setdefault(subcategory, []).append(item)

    return {
        "focus_cats": focus_cats,
        "cat_to_focus": cat_to_focus,
        "cat_subs": cat_subs,
        "sub_to_cat": sub_to_cat,
        "sub_items": sub_items,
    }
