"""Master color palette — every figure/table script imports its colors from here.

Do not define hex color literals locally in a generator script; add the
color here first, then import it. Keeping a single source of truth means
a palette change (e.g. a reviewer asking for colorblind-safe colors) is a
one-file edit instead of a hunt through every figure.

The sample data shipped with this template (``input/corpus.csv``,
``input/taxonomy.csv``, ``input/failure_observations.csv``) tells one
coherent, fully invented story — a literature review of empirical studies
that mine software failures (memory-safety bugs, concurrency bugs,
dependency/build failures) out of GitHub repositories. Replace every
constant below with your own paper's real taxonomy; nothing here is
special beyond being the single place every figure/table script reads
colors from.
"""

import matplotlib.pyplot as plt

# ── Paper-level category axis (shared by Fig1-4; matches taxonomy.CATEGORY) ──
CATEGORY_ORDER = [
    "Memory Safety",
    "Concurrency",
    "Dependency Management",
]

CATEGORY_COLORS = {
    "Memory Safety": "#dc2626",           # red
    "Concurrency": "#2563eb",             # blue
    "Dependency Management": "#16a34a",   # green
}

# ── Taxonomy Focus axis (Fig5 tree chart; taxonomy.FOCUS) ───────────────────
FOCUS_ORDER = ["Runtime Failures", "Build Failures"]

FOCUS_COLORS = {
    "Runtime Failures": "#7c3aed",   # violet
    "Build Failures": "#0891b2",     # cyan
}

# ── Severity axis (Fig6 crosstab; failure_observations.SEVERITY) ────────────
SEVERITY_ORDER = ["Low", "Medium", "High"]

SEVERITY_COLORS = {
    "Low": "#fde68a",       # amber-200
    "Medium": "#f59e0b",    # amber-500
    "High": "#b45309",      # amber-700
}

# ── Venue-type axis (Fig4 distribution) ─────────────────────────────────────
VENUE_CONF = "#0ea5e9"      # sky
VENUE_JOURNAL = "#10b981"   # emerald
VENUE_OTHER = "#94a3b8"     # slate

# Graduated palettes for the per-venue donuts (cycled if more venues than colors)
CONF_PALETTE = ["#0ea5e9", "#38bdf8", "#7dd3fc", "#0284c7"]
JOUR_PALETTE = ["#10b981", "#34d399", "#6ee7b7", "#059669"]

# ── Shared neutrals ──────────────────────────────────────────────────────────
WHITE = "#ffffff"
GRAY = "#9ca3af"
NEUTRAL_DARK = "#1E293B"
NEUTRAL_MUTED = "#64748B"
NEUTRAL_FALLBACK = "#94a3b8"
CONNECTOR_COLOR = "#94a3b8"

BG_TRANSPARENT = "rgba(0,0,0,0)"   # Plotly paper_bgcolor/plot_bgcolor
GRID_COLOR = "#E8E4DF"
TITLE_COLOR = NEUTRAL_DARK
SUBTITLE_COLOR = NEUTRAL_MUTED
AXIS_COLOR = "#475569"

# Shared title/panel-heading font size, used across every matplotlib figure.
ALL_TITLES = 16


def lighten(hex_color: str, factor: float) -> str:
    """Blend a hex color toward white by `factor` (0 = unchanged, 1 = white).

    Used to derive lighter tints of a category color for nested tree/donut
    nodes without hardcoding a second color per level.
    """
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def apply_style() -> None:
    """Shared matplotlib rcParams so every figure has the same look.
    Call once at the top of a figure script, before creating any Figure."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "axes.edgecolor": AXIS_COLOR,
        "axes.labelcolor": AXIS_COLOR,
        "xtick.color": AXIS_COLOR,
        "ytick.color": AXIS_COLOR,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    })
