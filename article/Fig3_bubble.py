"""
Fig3_bubble.py
Bubble diagram: Category x Year, bubble size proportional to article count.

Data via data_loader only. All visual parameters in the header.
"""
import matplotlib.pyplot as plt
from palette import apply_style; apply_style()

from data_loader import load_corpus, split_values
from figutils import save_figure
from palette import ALL_TITLES

# ── Output / config ────────────────────────────────────────────────────────────
OUT_FILENAME = "Fig3_bubble"
TITLE_TEXT = "Articles by Category and Year"

# ── Colors (imported from master palette) ─────────────────────────────────────
from palette import (
    CATEGORY_ORDER, CATEGORY_COLORS,
    NEUTRAL_FALLBACK, GRID_COLOR, TITLE_COLOR, AXIS_COLOR,
)

BUBBLE_EDGE_COLOR = "white"
BUBBLE_LABEL_COLOR = "white"

# ── Fonts (all font sizes, in points) ─────────────────────────────────────────
FS_TITLE = ALL_TITLES
FS_AXIS_LABEL = 11
FS_AXIS_TICKS = 10
FS_BUBBLE_LABEL = 9

# ── Layout ────────────────────────────────────────────────────────────────────
FIG_W = 9
FIG_H = 4.5
TITLE_PAD = 12
Y_MARGIN_FRAC = 0.3   # extra vertical padding so the top/bottom bubble rows aren't clipped

# ── Bubble sizing ─────────────────────────────────────────────────────────────
MIN_BUBBLE_SIZE = 200   # marker area (points^2) at count == 1
SIZE_SCALE = 350        # additional marker area per article

# ── Style (line widths / alphas) ──────────────────────────────────────────────
BUBBLE_ALPHA = 0.75
BUBBLE_EDGE_LW = 1.5


def main() -> None:
    df = load_corpus()
    years = sorted(df["YEAR"].unique())

    counts: dict[tuple[int, str], int] = {}
    for _, row in df.iterrows():
        for category in split_values(row["CATEGORY"]):
            key = (row["YEAR"], category)
            counts[key] = counts.get(key, 0) + 1

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    for category in CATEGORY_ORDER:
        xs, ys, sizes, labels = [], [], [], []
        for year in years:
            count = counts.get((year, category), 0)
            if count:
                xs.append(year)
                ys.append(category)
                sizes.append(MIN_BUBBLE_SIZE + count * SIZE_SCALE)
                labels.append(count)
        ax.scatter(xs, ys, s=sizes,
                   color=CATEGORY_COLORS.get(category, NEUTRAL_FALLBACK),
                   alpha=BUBBLE_ALPHA, edgecolors=BUBBLE_EDGE_COLOR,
                   linewidths=BUBBLE_EDGE_LW, zorder=3)
        for x, y, count in zip(xs, ys, labels):
            ax.annotate(str(count), (x, y), ha="center", va="center",
                        fontsize=FS_BUBBLE_LABEL, fontweight="bold",
                        color=BUBBLE_LABEL_COLOR, zorder=4)

    ax.set_xlabel("Year", fontsize=FS_AXIS_LABEL, color=AXIS_COLOR)
    ax.set_title(TITLE_TEXT, fontsize=FS_TITLE, color=TITLE_COLOR,
                 fontweight="bold", pad=TITLE_PAD)
    ax.set_xticks(years)
    ax.tick_params(labelsize=FS_AXIS_TICKS)
    ax.margins(y=Y_MARGIN_FRAC)
    ax.grid(color=GRID_COLOR, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()

    save_figure(fig, OUT_FILENAME)


if __name__ == "__main__":
    main()
