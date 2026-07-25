"""
Fig6_severitycrosstab.py
Stacked VERTICAL bar chart: each failure type's observation count split
across Severity (Low / Medium / High). One bar per failure type, grouped
by category with background bands, dividers, and category brackets —
rendered as TWO separate figures, one for "Runtime Failures" and one for
"Build Failures" (the two Focus groups in taxonomy.csv). Both figures
share the same Y-axis ceiling so they remain directly comparable.

Data via data_loader / crosstab only. All visual parameters in the header.
"""
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from palette import apply_style; apply_style()

from crosstab import build_crosstab
from figutils import save_figure
from palette import ALL_TITLES

# ── Output / config ────────────────────────────────────────────────────────────
# One figure per entry, each saved as its own file.
PANEL_CONFIGS = [
    {"focus": "Runtime Failures", "title": "RUNTIME FAILURES BY SEVERITY", "out_filename": "Fig6_severitycrosstab_runtime"},
    {"focus": "Build Failures", "title": "BUILD FAILURES BY SEVERITY", "out_filename": "Fig6_severitycrosstab_build"},
]

# ── Cross-tab field ───────────────────────────────────────────────────────────
COL_FIELD = "SEVERITY"

# ── Colors (imported from master palette) ─────────────────────────────────────
from palette import (
    TAXONOMY_CATEGORY_COLORS, SEVERITY_ORDER, severity_palette,
    NEUTRAL_MUTED, NEUTRAL_FALLBACK,
)

# Warm ramp (palette.severity_palette) for the stacked segments — a distinct
# hue family so severity segments are never confused with the category colors
# used for grouping (bands, brackets).
COL_ORDER = SEVERITY_ORDER
SEVERITY_COLORS = dict(zip(COL_ORDER, severity_palette(len(COL_ORDER))))
BAR_EDGE_COLOR = "white"
DIVIDER_COLOR = NEUTRAL_MUTED
LEGEND_FACECOLOR = "white"

# ── Fonts (all font sizes, in points) ─────────────────────────────────────────
FS_PANEL_TITLE = ALL_TITLES
FS_AXIS_LABEL = 11
FS_Y_TICKS = 9
FS_CATEGORIES = 10          # category bracket label above the bars
FS_FAILURE_TICKS = 10       # failure-type (x-tick) labels
FS_TOTAL_LABEL = 9          # total-count label above each stacked bar
FS_LEGEND = 9

# ── Layout ────────────────────────────────────────────────────────────────────
BAR_SLOT_W = 1.1     # inches per failure-type bar (sets FIG_W = FIG_MARGIN_W + BAR_SLOT_W * n_bars)
FIG_MARGIN_W = 2.2   # inches reserved for the y-axis label/ticks
FIG_H = 6
BAR_WIDTH = 0.75
TITLE_PAD = 36
LABEL_ROTATION = 30           # x-tick (failure-type) label rotation, degrees
TOTAL_LABEL_OFFSET = 0.6
Y_CEIL_PAD_FRAC = 0.25
Y_CEIL_PAD_MIN = 2
Y_BRACKET_FRACTION = 0.97     # category bracket y-position, as a fraction of y_ceil
Y_LABEL_FRACTION = 1.01       # category label y-position, as a fraction of y_ceil
LEGEND_LOC = "upper left"
LEGEND_BBOX = (1.01, 1.0)     # axes-fraction anchor, placed just outside the plot

# ── Style (line widths / dash styles / alphas) ────────────────────────────────
BAND_ALPHA_EVEN = 0.14
BAND_ALPHA_ODD = 0.05
BAR_EDGE_LINEWIDTH = 0.8
DIVIDER_LINEWIDTH = 0.9
DIVIDER_LINESTYLE = "--"
BRACKET_LW = 2.0
GRID_LINESTYLE = "--"
GRID_ALPHA = 0.5
LEGEND_FRAME_ALPHA = 0.85


def _category_bands(cats: list) -> list:
    """Group contiguous equal categories into (category, lo_index, hi_index)."""
    bands, prev_cat, start = [], None, 0
    for i, cat in enumerate(cats):
        if cat != prev_cat:
            if prev_cat is not None:
                bands.append((prev_cat, start, i - 1))
            start, prev_cat = i, cat
    bands.append((prev_cat, start, len(cats) - 1))
    return bands


def _plot_panel(ax, panel_rows: list, info: dict, matrix, y_ceil: float, title: str) -> None:
    # matrix is aligned to the *full* rows list; build an index lookup once.
    all_rows = list(info)
    panel_matrix = np.array([matrix[all_rows.index(r)] for r in panel_rows])

    cats = [info[r][2] for r in panel_rows]
    n = len(panel_rows)
    x = np.arange(n)

    bands = _category_bands(cats)
    for band_idx, (cat, lo, hi) in enumerate(bands):
        alpha = BAND_ALPHA_EVEN if band_idx % 2 == 0 else BAND_ALPHA_ODD
        ax.axvspan(lo - 0.5, hi + 0.5, facecolor=TAXONOMY_CATEGORY_COLORS.get(cat, NEUTRAL_FALLBACK),
                   alpha=alpha, zorder=0)
    for _, _, hi in bands[:-1]:
        ax.axvline(hi + 0.5, color=DIVIDER_COLOR, linewidth=DIVIDER_LINEWIDTH,
                   linestyle=DIVIDER_LINESTYLE, zorder=1)

    bottom = np.zeros(n)
    for j, severity in enumerate(COL_ORDER):
        vals = panel_matrix[:, j]
        ax.bar(x, vals, BAR_WIDTH, bottom=bottom,
               color=SEVERITY_COLORS.get(severity, NEUTRAL_FALLBACK),
               edgecolor=BAR_EDGE_COLOR, linewidth=BAR_EDGE_LINEWIDTH, zorder=3)
        bottom += vals

    totals = panel_matrix.sum(axis=1)
    for xi, tot in zip(x, totals):
        if tot > 0:
            ax.text(xi, tot + TOTAL_LABEL_OFFSET, str(int(tot)), ha="center", va="bottom",
                    fontsize=FS_TOTAL_LABEL, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(panel_rows, fontsize=FS_FAILURE_TICKS, rotation=LABEL_ROTATION, ha="right")

    y_bracket = y_ceil * Y_BRACKET_FRACTION
    y_label = y_ceil * Y_LABEL_FRACTION
    for cat, lo, hi in bands:
        color = TAXONOMY_CATEGORY_COLORS.get(cat, NEUTRAL_FALLBACK)
        mid = (lo + hi) / 2
        ax.annotate("", xy=(lo - 0.45, y_bracket), xytext=(hi + 0.45, y_bracket),
                    arrowprops={"arrowstyle": "-", "color": color, "lw": BRACKET_LW})
        ax.text(mid, y_label, cat, ha="center", va="bottom",
                fontsize=FS_CATEGORIES, fontweight="bold", color=color, clip_on=False)

    ax.set_ylabel("Number of Observations", fontsize=FS_AXIS_LABEL)
    ax.tick_params(axis="y", labelsize=FS_Y_TICKS)
    ax.set_title(title, fontsize=FS_PANEL_TITLE, fontweight="bold", pad=TITLE_PAD)
    ax.yaxis.grid(True, linestyle=GRID_LINESTYLE, alpha=GRID_ALPHA, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(0, y_ceil)

    handles = [mpatches.Patch(color=SEVERITY_COLORS[s], label=s) for s in COL_ORDER]
    ax.legend(handles=handles, title="Severity", fontsize=FS_LEGEND, title_fontsize=FS_LEGEND,
              loc=LEGEND_LOC, bbox_to_anchor=LEGEND_BBOX, frameon=True,
              facecolor=LEGEND_FACECOLOR, framealpha=LEGEND_FRAME_ALPHA)


def main() -> None:
    rows, info, _, matrix = build_crosstab(COL_ORDER)

    for cfg in PANEL_CONFIGS:
        cfg["rows"] = [r for r in rows if info[r][3] == cfg["focus"]]

    all_totals = [matrix[rows.index(r)].sum() for cfg in PANEL_CONFIGS for r in cfg["rows"]]
    y_max = max(all_totals) if all_totals else 1
    y_ceil = y_max + max(Y_CEIL_PAD_MIN, round(y_max * Y_CEIL_PAD_FRAC))

    for cfg in PANEL_CONFIGS:
        panel_rows = cfg["rows"]
        if not panel_rows:
            print(f"[{cfg['out_filename']}] No rows for focus={cfg['focus']!r} — skipping.")
            continue

        fig_w = FIG_MARGIN_W + BAR_SLOT_W * len(panel_rows)
        fig, ax = plt.subplots(figsize=(fig_w, FIG_H))
        _plot_panel(ax, panel_rows, info, matrix, y_ceil, cfg["title"])
        fig.tight_layout()

        save_figure(fig, cfg["out_filename"])


if __name__ == "__main__":
    main()
