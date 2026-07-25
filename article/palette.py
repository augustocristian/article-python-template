"""Master color palette and typography for every figure and table.

Do not define hex color literals locally in a generator script; add the
color here first, then import it. A single source of truth means a palette
change (a reviewer asking for softer colors, a colorblind-safe pass) is a
one-file edit instead of a hunt through every figure.

The base colors are a soft, Pantone-style family: muted, low-glare hues
that stay legible side by side in print and never fight each other on a
page. Each hue has a lighter primary and a `_DEEP` variant for when a
figure needs a stronger anchor of the same color.

The semantic axes at the bottom (CATEGORY / FOCUS / SEVERITY / VENUE) are
placeholders wired to this template's sample data — replace them with your
article's real taxonomy.
"""

import matplotlib as mpl

# ── Typography ─────────────────────────────────────────────────────────────
FONT_FAMILY = "Corbel"   # humanist sans-serif; works in both matplotlib and Plotly
TEXT_COLOR = "#434A54"   # soft near-black, from the neutral family below
TEXT_STROKE = 2.5         # white halo width in points, for text over saturated fills

# Shared title/panel-heading font size. Scale up together with FIG_W/FIG_H
# when a figure is enlarged for a full article page.
ALL_TITLES = 16

# Shared resolution for the local PNG/SVG debug preview every Fig*.py saves
# alongside its real PDF — one place to raise/lower it for every figure.
DEBUG_DPI = 150


def apply_style() -> None:
    """Set global matplotlib rcParams. Call once at the top of each figure
    script, before creating any Figure."""
    mpl.rcParams.update({
        "font.family": FONT_FAMILY,
        "text.color": TEXT_COLOR,
        "axes.labelcolor": TEXT_COLOR,
        "xtick.color": TEXT_COLOR,
        "ytick.color": TEXT_COLOR,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    })


def text_effects() -> list:
    """Path-effects for text with a white halo, for labels drawn over a
    saturated fill (a tree-chart node, a donut wedge).

    Usage: ``ax.text(..., color=TEXT_COLOR, path_effects=text_effects())``
    """
    import matplotlib.patheffects as pe
    return [pe.withStroke(linewidth=TEXT_STROKE, foreground="white"), pe.Normal()]


# ── Base colors — soft Pantone-style family ────────────────────────────────
# Primary (softer) hue first, `_DEEP` variant second for stronger anchors.
RED = "#ED5565"
RED_DEEP = "#DA4453"
ORANGE = "#FC6E51"
ORANGE_DEEP = "#E9573F"
YELLOW = "#FFCE54"
YELLOW_DEEP = "#F6BB42"
GREEN = "#A0D468"
GREEN_DEEP = "#8CC152"
TEAL = "#48CFAD"
TEAL_DEEP = "#37BC9B"
CYAN = "#4FC1E9"
CYAN_DEEP = "#3BAFDA"
BLUE = "#5D9CEC"
BLUE_DEEP = "#4A89DC"
PURPLE = "#AC92EC"
PURPLE_DEEP = "#967ADC"
PINK = "#EC87C0"
PINK_DEEP = "#D770AD"

# ── Structural neutrals (non-semantic grays used by figure scaffolding) ────
WHITE = "#FFFFFF"
NEUTRAL_LIGHT = "#E6E9ED"     # band fills, grid lines
NEUTRAL_FALLBACK = "#CCD1D9"  # missing-category fill
NEUTRAL_MUTED = "#AAB2BD"     # soft label / divider line
NEUTRAL_MID = "#656D78"       # secondary label text
NEUTRAL_DARK = "#434A54"      # primary label text
GRAY = NEUTRAL_MUTED

CONNECTOR_COLOR = NEUTRAL_FALLBACK
GRID_COLOR = NEUTRAL_LIGHT
TITLE_COLOR = TEXT_COLOR
SUBTITLE_COLOR = NEUTRAL_MID
AXIS_COLOR = TEXT_COLOR
BG_TRANSPARENT = "rgba(0,0,0,0)"   # Plotly paper_bgcolor/plot_bgcolor


def _interp_hex(c_from: str, c_to: str, t: float) -> str:
    a, b = c_from.lstrip("#"), c_to.lstrip("#")
    ar, ag, ab = (int(a[i:i + 2], 16) for i in (0, 2, 4))
    br, bg, bb = (int(b[i:i + 2], 16) for i in (0, 2, 4))
    return "#{:02x}{:02x}{:02x}".format(
        int(ar + (br - ar) * t), int(ag + (bg - ag) * t), int(ab + (bb - ab) * t))


def graduated_palette(c_from: str, c_to: str, n: int) -> list:
    """Return n hex colors evenly interpolated from c_from to c_to."""
    if n <= 1:
        return [c_from]
    return [_interp_hex(c_from, c_to, i / (n - 1)) for i in range(n)]


def lighten(hex_color: str, factor: float) -> str:
    """Blend a hex color toward white (0 = unchanged, 1 = white).

    Used to tint nested tree/donut levels from their parent's color instead
    of hardcoding a separate color per level.
    """
    return _interp_hex(hex_color, WHITE, factor)


def rgba(hex_color: str, alpha: float) -> str:
    """Return a semi-transparent `rgba(r,g,b,a)` string for a hex color.

    Plotly link ribbons need rgba rather than hex+opacity, so this keeps
    figures from hand-writing rgba literals (which would bypass the palette).
    """
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def subcategory_colors(
    cat_order: list,
    sub_order: dict,
    shade_factors: list,
) -> dict:
    """Map each subcategory to a lighter tint of its parent category color
    (blended toward white — never darker than, or equal to, the parent, so a
    subcategory swatch is never confused with its category's own swatch).

    Args:
        cat_order: Categories to process, in display order.
        sub_order: Maps category name -> subcategory names (taxonomy order).
        shade_factors: Per-index blend-toward-white amounts in (0, 1] —
            0 would equal the parent color (never used), 1 is white; cycles
            when len(subs) > len(factors).

    Returns:
        Dict mapping subcategory name -> hex color string.
    """
    colors: dict = {}
    for cat in cat_order:
        base = CATEGORY_COLORS.get(cat, NEUTRAL_FALLBACK)
        for idx, sub in enumerate(sub_order.get(cat, [])):
            f = shade_factors[idx % len(shade_factors)]
            colors[sub] = lighten(base, f)
    return colors


# ── Sankey flow axes (Fig1: Source -> Detection phase -> Detected by) ──────
# These node colors are the anchors for the whole article: the same entity
# carries the same color everywhere, and the semantic axes below reuse them
# so a reader learns each hue once.
SOURCE_ORDER = ["ACM", "IEEE", "DBLP", "arXiv"]

SOURCE_COLORS = {
    "ACM": ORANGE,
    "IEEE": BLUE,
    "DBLP": YELLOW,
    "arXiv": RED,
}

# When in the lifecycle the failure surfaces — earliest to latest.
DETECTION_ORDER = ["Static", "Build", "Runtime"]

DETECTION_COLORS = {
    "Static": CYAN,
    "Build": TEAL,
    "Runtime": GREEN,
}

# Who/what found it.
DETECTOR_ORDER = ["Human", "LLM"]

DETECTOR_COLORS = {
    "Human": BLUE_DEEP,
    "LLM": PURPLE,
}

# ── Article-level category axis (Fig2-4; matches taxonomy.CATEGORY) ────────
# Named constants (rather than repeating the string literals) because these
# three category names are shared with TAXONOMY_CATEGORY_COLORS below — see
# the "one entity, one color" note there.
CATEGORY_MEMORY_SAFETY = "Memory Safety"
CATEGORY_CONCURRENCY = "Concurrency"
CATEGORY_DEPENDENCY_MANAGEMENT = "Dependency Management"

CATEGORY_ORDER = [
    CATEGORY_MEMORY_SAFETY,
    CATEGORY_CONCURRENCY,
    CATEGORY_DEPENDENCY_MANAGEMENT,
]

CATEGORY_COLORS = {
    CATEGORY_MEMORY_SAFETY: RED,           # anchored to the arXiv / Excluded node
    CATEGORY_CONCURRENCY: BLUE,            # anchored to the IEEE / Stage 1 node
    CATEGORY_DEPENDENCY_MANAGEMENT: GREEN,  # anchored to the Final Corpus node
}

# ── Taxonomy Focus axis (Fig5 tree chart; taxonomy.FOCUS) ──────────────────
FOCUS_ORDER = ["Runtime Failures", "Build Failures"]

FOCUS_COLORS = {
    "Runtime Failures": PURPLE,
    "Build Failures": CYAN,
}

# ── Taxonomy Category axis (Fig5 tree chart, Fig6 crosstab; taxonomy.CATEGORY) ──
# Deliberately a *separate* dict from the article-level CATEGORY_COLORS above:
# the taxonomy has far more categories (one tree per Focus group) than the
# three broad buckets corpus.csv's own CATEGORY column uses, so the two axes
# are genuinely different things reusing shared base hues, not the same
# axis — see the "Unified Color Palette" Iron Rule in CLAUDE.md. Categories
# that share a name with an article-level category (CATEGORY_MEMORY_SAFETY,
# CATEGORY_CONCURRENCY, CATEGORY_DEPENDENCY_MANAGEMENT) keep that category's
# color; the rest get a fresh hue, chosen so no two categories under the same
# Focus collide and neither collides with that Focus's own FOCUS_COLORS entry.
TAXONOMY_CATEGORY_COLORS = {
    # Runtime Failures (FOCUS_COLORS["Runtime Failures"] = PURPLE)
    CATEGORY_MEMORY_SAFETY: RED,
    CATEGORY_CONCURRENCY: BLUE,
    "Resource Exhaustion": ORANGE,
    "Input Handling": PINK,
    # Build Failures (FOCUS_COLORS["Build Failures"] = CYAN)
    CATEGORY_DEPENDENCY_MANAGEMENT: GREEN,
    "Build Configuration": YELLOW,
    "Compilation Failures": ORANGE_DEEP,
    "Packaging Failures": PURPLE_DEEP,
}

# ── Severity axis (Fig6 crosstab; failure_observations.SEVERITY) ───────────
SEVERITY_ORDER = ["Low", "Medium", "High"]


def severity_palette(n: int) -> list:
    """n graduated warm tints (soft yellow -> soft orange) for the Severity
    axis — a hue family deliberately distinct from CATEGORY_COLORS, so
    stacked severity segments never read as a category color."""
    return graduated_palette(YELLOW, ORANGE_DEEP, n)


SEVERITY_COLORS = dict(zip(SEVERITY_ORDER, severity_palette(len(SEVERITY_ORDER))))

# ── Venue-type axis (Fig4 distribution) ────────────────────────────────────
# Taken straight from Fig1's source nodes, so a venue type carries the same
# color it has in the flow diagram.
VENUE_TYPE_ORDER = ["arXiv", "Conference", "Journal"]

VENUE_ARXIV = RED        # anchored to the arXiv node in Fig1
VENUE_CONF = BLUE        # anchored to the IEEE node in Fig1
VENUE_JOURNAL = TEAL     # anchored to the Build/Runtime phase nodes in Fig1
VENUE_OTHER = NEUTRAL_MUTED

VENUE_TYPE_COLORS = {
    "arXiv": VENUE_ARXIV,
    "Conference": VENUE_CONF,
    "Journal": VENUE_JOURNAL,
}

# Graduated tints for the per-venue donuts (cycled if more venues than colors)
CONF_PALETTE = graduated_palette(BLUE_DEEP, "#D6E6FB", 8)
JOUR_PALETTE = graduated_palette(TEAL_DEEP, "#D3F2E8", 8)
