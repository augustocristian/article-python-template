"""Master color palette — every figure/table script imports its colors from here.

Do not define hex color literals locally in a generator script; add the
color here first, then import it. Keeping a single source of truth means
a palette change (e.g. a reviewer asking for colorblind-safe colors) is a
one-file edit instead of a hunt through every figure.

Replace ``CATEGORY_ORDER``/``CATEGORY_COLORS`` with whatever categorical
axis your paper actually uses (e.g. research trends, techniques, RQs) —
they're placeholders wired up to the sample ``input/corpus.csv`` shipped
with this template.
"""

# ── Categorical axis (edit to match your paper's own taxonomy) ─────────────
CATEGORY_ORDER = [
    "Category A",
    "Category B",
    "Category C",
]

CATEGORY_COLORS = {
    "Category A": "#6366f1",  # indigo
    "Category B": "#10b981",  # emerald
    "Category C": "#f59e0b",  # amber
}

# ── Shared neutrals ──────────────────────────────────────────────────────────
BG_TRANSPARENT = "#00000000"
GRID_COLOR = "#E8E4DF"
TITLE_COLOR = "#1E293B"
SUBTITLE_COLOR = "#64748B"
AXIS_COLOR = "#475569"
