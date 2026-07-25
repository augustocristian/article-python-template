"""Single data access layer — every generator script loads data from here.

If your real corpus lives in a hand-curated Excel/Google Sheet, add one
script (following the pattern of ``paper_corpora_to_csv.py`` in the
``llmroadmap`` project this template is derived from) that is the *only*
thing allowed to read that source, and have it write ``input/corpus.csv``.
Every other script — figures, tables, BibTeX — should keep loading through
``load_corpus()`` below rather than reading the source file directly, so
there is exactly one place that knows the source format.
"""

import pandas as pd

import config


def load_corpus() -> pd.DataFrame:
    """Load the canonical corpus from ``INPUT_DIR/corpus.csv``."""
    return pd.read_csv(config.CORPUS_CSV, sep=";")


def split_values(cell) -> list[str]:
    """Split a comma-separated cell (e.g. a multi-valued category column)
    into a list of trimmed values. Returns [] for missing/blank cells."""
    if pd.isna(cell):
        return []
    return [v.strip() for v in str(cell).split(",") if v.strip()]
