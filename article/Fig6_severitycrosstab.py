"""
Fig6_severitycrosstab.py
Stacked vertical bar chart: each failure type's observation count split
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

import config
import palette
from palette import apply_style
from crosstab import build_crosstab

apply_style()

# ── Output / config ────────────────────────────────────────────────────────
PANEL_CONFIGS = [
    {"focus": "Runtime Failures", "title": "RUNTIME FAILURES BY SEVERITY", "out_filename": "Fig6_severitycrosstab_runtime"},
    {"focus": "Build Failures", "title": "BUILD FAILURES BY SEVERITY", "out_filename": "Fig6_severitycrosstab_build"},
]

# ── Fonts (points) ───────────────────────────────────────────────────────
FS_PANEL_TITLE = palette.ALL_TITLES
FS_AXIS_LABEL = 11
FS_Y_TICKS = 9
FS_CATEGORY = 10
FS_FAILURE_TICKS = 10
FS_TOTAL_LABEL = 9
FS_LEGEND = 9

# ── Layout ────────────────────────────────────────────────────────────────
BAR_SLOT_W = 1.1     # inches per failure-type bar
FIG_MARGIN_W = 2.2   # inches reserved for the y-axis label/ticks
FIG_H = 6
BAR_WIDTH = 0.75
BAND_ALPHA_EVEN = 0.14
BAND_ALPHA_ODD = 0.05
BRACKET_LW = 2.0
Y_CEIL_PAD_FRAC = 0.25
Y_CEIL_PAD_MIN = 2
TOTAL_LABEL_OFFSET = 0.6


def _category_bands(cats: list[str]) -> list[tuple[str, int, int]]:
    bands, prev_cat, start = [], None, 0
    for i, cat in enumerate(cats):
        if cat != prev_cat:
            if prev_cat is not None:
                bands.append((prev_cat, start, i - 1))
            start, prev_cat = i, cat
    bands.append((prev_cat, start, len(cats) - 1))
    return bands


def _plot_panel(ax, panel_rows: list[str], info: dict, col_order: list[str], matrix, y_ceil: float, title: str) -> None:
    # matrix is aligned to the *full* rows list; build an index lookup once.
    all_rows = list(info)
    panel_matrix = np.array([matrix[all_rows.index(r)] for r in panel_rows])

    cats = [info[r][2] for r in panel_rows]
    n = len(panel_rows)
    x = np.arange(n)

    bands = _category_bands(cats)
    for band_idx, (cat, lo, hi) in enumerate(bands):
        alpha = BAND_ALPHA_EVEN if band_idx % 2 == 0 else BAND_ALPHA_ODD
        ax.axvspan(lo - 0.5, hi + 0.5, facecolor=palette.CATEGORY_COLORS.get(cat, palette.NEUTRAL_FALLBACK),
                   alpha=alpha, zorder=0)
    for _, _, hi in bands[:-1]:
        ax.axvline(hi + 0.5, color=palette.NEUTRAL_MUTED, linewidth=0.9, linestyle="--", zorder=1)

    bottom = np.zeros(n)
    for j, severity in enumerate(col_order):
        vals = panel_matrix[:, j]
        ax.bar(x, vals, BAR_WIDTH, bottom=bottom,
               color=palette.SEVERITY_COLORS.get(severity, palette.NEUTRAL_FALLBACK),
               edgecolor="white", linewidth=0.8, zorder=3)
        bottom += vals

    totals = panel_matrix.sum(axis=1)
    for xi, tot in zip(x, totals):
        if tot > 0:
            ax.text(xi, tot + TOTAL_LABEL_OFFSET, str(int(tot)), ha="center", va="bottom",
                    fontsize=FS_TOTAL_LABEL, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(panel_rows, fontsize=FS_FAILURE_TICKS, rotation=30, ha="right")

    y_bracket = y_ceil * 0.97
    y_label = y_ceil * 1.01
    for cat, lo, hi in bands:
        color = palette.CATEGORY_COLORS.get(cat, palette.NEUTRAL_FALLBACK)
        mid = (lo + hi) / 2
        ax.annotate("", xy=(lo - 0.45, y_bracket), xytext=(hi + 0.45, y_bracket),
                    arrowprops={"arrowstyle": "-", "color": color, "lw": BRACKET_LW})
        ax.text(mid, y_label, cat, ha="center", va="bottom",
                fontsize=FS_CATEGORY, fontweight="bold", color=color, clip_on=False)

    ax.set_ylabel("Number of Observations", fontsize=FS_AXIS_LABEL)
    ax.tick_params(axis="y", labelsize=FS_Y_TICKS)
    ax.set_title(title, fontsize=FS_PANEL_TITLE, fontweight="bold", pad=36)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(0, y_ceil)

    handles = [mpatches.Patch(color=palette.SEVERITY_COLORS[s], label=s) for s in col_order]
    ax.legend(handles=handles, title="Severity", fontsize=FS_LEGEND, title_fontsize=FS_LEGEND,
              loc="upper left", bbox_to_anchor=(1.01, 1.0), framealpha=0.85)


def main() -> None:
    rows, info, col_order, matrix = build_crosstab(palette.SEVERITY_ORDER)

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
        _plot_panel(ax, panel_rows, info, col_order, matrix, y_ceil, cfg["title"])
        fig.tight_layout()

        pdf_path = config.FIGURES_DIR / f"{cfg['out_filename']}.pdf"
        png_path = config.OUTPUT_BASE_DIR / f"{cfg['out_filename']}.png"
        fig.savefig(pdf_path, bbox_inches="tight")
        fig.savefig(png_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Saved {pdf_path}")
        print(f"Saved {png_path} (debug preview)")


if __name__ == "__main__":
    main()
