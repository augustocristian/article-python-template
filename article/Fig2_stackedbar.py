"""
Fig2_stackedbar.py
Stacked bar chart: articles per year, stacked by category.

Data via data_loader only. All visual parameters in the header.
"""
import matplotlib.pyplot as plt
from palette import apply_style; apply_style()

from data_loader import load_corpus, split_values
from figutils import save_figure
from palette import ALL_TITLES

# ── Output / config ────────────────────────────────────────────────────────────
OUT_FILENAME = "Fig2_stackedbar"
TITLE_TEXT = "Articles per Year, by Category"

# ── Colors (imported from master palette) ─────────────────────────────────────
from palette import (
    CATEGORY_ORDER, CATEGORY_COLORS,
    NEUTRAL_FALLBACK, GRID_COLOR, TITLE_COLOR, AXIS_COLOR,
)

BAR_EDGE_COLOR = "none"

# ── Fonts (all font sizes, in points) ─────────────────────────────────────────
FS_TITLE = ALL_TITLES
FS_AXIS_LABEL = 11
FS_AXIS_TICKS = 10
FS_LEGEND = 9

# ── Layout ────────────────────────────────────────────────────────────────────
FIG_W = 8
FIG_H = 5
TITLE_PAD = 12

# ── Style (line widths / alphas) ──────────────────────────────────────────────
BAR_EDGE_LW = 0.0
GRID_LINEWIDTH = 0.8
LEGEND_LOC = "upper left"
LEGEND_FRAME_ALPHA = 0.9


def main() -> None:
    df = load_corpus()
    years = sorted(df["YEAR"].unique())
    year_index = {year: i for i, year in enumerate(years)}

    counts = {cat: [0] * len(years) for cat in CATEGORY_ORDER}
    for _, row in df.iterrows():
        for category in split_values(row["CATEGORY"]):
            counts.setdefault(category, [0] * len(years))
            counts[category][year_index[row["YEAR"]]] += 1

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    bottoms = [0] * len(years)
    for category in CATEGORY_ORDER:
        values = counts[category]
        ax.bar(years, values, bottom=bottoms,
               color=CATEGORY_COLORS.get(category, NEUTRAL_FALLBACK),
               edgecolor=BAR_EDGE_COLOR, linewidth=BAR_EDGE_LW, label=category)
        bottoms = [b + v for b, v in zip(bottoms, values)]

    ax.set_xlabel("Year", fontsize=FS_AXIS_LABEL, color=AXIS_COLOR)
    ax.set_ylabel("Number of articles", fontsize=FS_AXIS_LABEL, color=AXIS_COLOR)
    ax.set_title(TITLE_TEXT, fontsize=FS_TITLE, color=TITLE_COLOR,
                 fontweight="bold", pad=TITLE_PAD)
    ax.set_xticks(years)
    ax.tick_params(labelsize=FS_AXIS_TICKS)
    ax.legend(fontsize=FS_LEGEND, loc=LEGEND_LOC, framealpha=LEGEND_FRAME_ALPHA)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=GRID_LINEWIDTH)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()

    save_figure(fig, OUT_FILENAME)


if __name__ == "__main__":
    main()
