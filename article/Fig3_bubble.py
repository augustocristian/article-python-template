"""
Fig3_bubble.py
Bubble diagram: Category x Year, bubble size proportional to paper count.
"""
import matplotlib.pyplot as plt

import config
import palette
from palette import apply_style
from data_loader import load_corpus, split_values

apply_style()

OUT_FILENAME = "Fig3_bubble"
MIN_BUBBLE_SIZE = 200
SIZE_SCALE = 350


def main() -> None:
    df = load_corpus()
    years = sorted(df["YEAR"].unique())
    categories = palette.CATEGORY_ORDER

    counts: dict[tuple[int, str], int] = {}
    for _, row in df.iterrows():
        for category in split_values(row["CATEGORY"]):
            key = (row["YEAR"], category)
            counts[key] = counts.get(key, 0) + 1

    fig, ax = plt.subplots(figsize=(9, 4.5))
    for category in categories:
        xs, ys, sizes, labels = [], [], [], []
        for year in years:
            count = counts.get((year, category), 0)
            if count:
                xs.append(year)
                ys.append(category)
                sizes.append(MIN_BUBBLE_SIZE + count * SIZE_SCALE)
                labels.append(count)
        ax.scatter(xs, ys, s=sizes,
                   color=palette.CATEGORY_COLORS.get(category, palette.NEUTRAL_FALLBACK),
                   alpha=0.75, edgecolors="white", linewidths=1.5, zorder=3)
        for x, y, count in zip(xs, ys, labels):
            ax.annotate(str(count), (x, y), ha="center", va="center",
                        fontsize=9, fontweight="bold", color="white", zorder=4)

    ax.set_xlabel("Year", color=palette.AXIS_COLOR)
    ax.set_title("Papers by Category and Year", fontsize=palette.ALL_TITLES,
                 color=palette.TITLE_COLOR, fontweight="bold")
    ax.set_xticks(years)
    ax.margins(y=0.3)
    ax.grid(color=palette.GRID_COLOR, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()

    pdf_path = config.FIGURES_DIR / f"{OUT_FILENAME}.pdf"
    png_path = config.OUTPUT_BASE_DIR / f"{OUT_FILENAME}.png"
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    print(f"Saved {pdf_path}")
    print(f"Saved {png_path} (debug preview)")
    plt.close(fig)


if __name__ == "__main__":
    main()
