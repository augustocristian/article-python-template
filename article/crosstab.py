"""
crosstab.py
Shared *data* helper for the cross-tabulation figure (Fig6): failure-type
observation counts split by severity.

Only data preparation lives here — the figure does its own plotting. All
access is through data_loader; no direct CSV reads. Walks the taxonomy in
the same order ``data_loader.build_hierarchy_lookups()`` uses, so the tree
chart and the crosstab bar chart always agree on ordering/grouping.
"""
import numpy as np

from data_loader import load_taxonomy, load_failure_observations


def build_crosstab(severity_order: list[str]):
    """Return (rows, info, col_order, matrix):
      - rows: failure types, in taxonomy order
      - info: {failure_type: (failure_type, subcategory, category, focus)}
      - col_order: severity_order, unchanged (returned for symmetry with rows/info)
      - matrix: len(rows) x len(severity_order) array of observation counts
    """
    # Sort so every category's rows are contiguous (and alphabetical within
    # it, matching Fig5's tree ordering) regardless of the order new failure
    # types were appended to taxonomy.csv — Fig6's _category_bands() groups
    # by *contiguous* equal category, so an unsorted, interleaved row order
    # would silently split one category into several bands.
    taxonomy = load_taxonomy().sort_values(
        ["FOCUS", "CATEGORY", "SUBCATEGORY", "FAILURE_TYPE"]
    ).reset_index(drop=True)
    observations = load_failure_observations()

    rows = list(taxonomy["FAILURE_TYPE"])
    info = {
        row["FAILURE_TYPE"]: (row["FAILURE_TYPE"], row["SUBCATEGORY"], row["CATEGORY"], row["FOCUS"])
        for _, row in taxonomy.iterrows()
    }

    counts = observations.groupby(["FAILURE_TYPE", "SEVERITY"]).size()

    matrix = np.zeros((len(rows), len(severity_order)))
    for i, failure_type in enumerate(rows):
        for j, severity in enumerate(severity_order):
            matrix[i, j] = counts.get((failure_type, severity), 0)

    return rows, info, severity_order, matrix
