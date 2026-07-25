"""
Fig2_stackedbar.py
Stacked bar chart: papers per year, stacked by category.
"""
import matplotlib.pyplot as plt

import config
import palette
from palette import apply_style
from data_loader import load_corpus, split_values

apply_style()

OUT_FILENAME = "Fig2_stackedbar"


def main() -> None:
    df = load_corpus()
    years = sorted(df["YEAR"].unique())
    year_index = {year: i for i, year in enumerate(years)}

    counts = {cat: [0] * len(years) for cat in palette.CATEGORY_ORDER}
    for _, row in df.iterrows():
        for category in split_values(row["CATEGORY"]):
            counts.setdefault(category, [0] * len(years))
            counts[category][year_index[row["YEAR"]]] += 1

    fig, ax = plt.subplots(figsize=(8, 5))
    bottoms = [0] * len(years)
    for category in palette.CATEGORY_ORDER:
        values = counts[category]
        ax.bar(years, values, bottom=bottoms,
               color=palette.CATEGORY_COLORS.get(category, palette.NEUTRAL_FALLBACK),
               label=category)
        bottoms = [b + v for b, v in zip(bottoms, values)]

    ax.set_xlabel("Year", color=palette.AXIS_COLOR)
    ax.set_ylabel("Number of papers", color=palette.AXIS_COLOR)
    ax.set_title("Papers per Year, by Category", fontsize=palette.ALL_TITLES,
                 color=palette.TITLE_COLOR, fontweight="bold")
    ax.set_xticks(years)
    ax.legend(fontsize=9)
    ax.grid(axis="y", color=palette.GRID_COLOR)
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
