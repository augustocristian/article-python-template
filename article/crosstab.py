"""Crosstab helper: failure-type observation counts split by severity.

Shared by Fig6_severitycrosstab.py. Walks the taxonomy in the same order
``data_loader.build_hierarchy_lookups()`` uses, so the tree chart and the
crosstab bar chart always agree on ordering/grouping.
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
    taxonomy = load_taxonomy()
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
