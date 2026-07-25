"""Generates the paper's figures from the corpus.

Writes PDFs to ``FIGURES_DIR`` (the article repo) for LaTeX to \\includegraphics,
and a PNG debug preview of each to ``OUTPUT_BASE_DIR`` (never to the article
repo) so you can eyeball a figure without opening the PDF.

Ships with two placeholder charts built on the sample ``input/corpus.csv``;
replace ``plot_papers_per_category``/``plot_papers_per_year`` with your
paper's real figures once you have a real corpus, keeping the same
save-to-FIGURES_DIR-plus-debug-PNG pattern.
"""

import matplotlib.pyplot as plt

import config
import palette
from data_loader import load_corpus, split_values


def _save(fig, name: str) -> None:
    pdf_path = config.FIGURES_DIR / f"{name}.pdf"
    png_path = config.OUTPUT_BASE_DIR / f"{name}.png"
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    print(f"Saved {pdf_path}")
    print(f"Saved {png_path} (debug preview)")


def plot_papers_per_category(df) -> None:
    counts = {cat: 0 for cat in palette.CATEGORY_ORDER}
    for cell in df["CATEGORY"]:
        for cat in split_values(cell):
            counts[cat] = counts.get(cat, 0) + 1

    categories = list(counts)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(categories, [counts[c] for c in categories],
           color=[palette.CATEGORY_COLORS.get(c, "#94a3b8") for c in categories])
    ax.set_title("Papers per Category", color=palette.TITLE_COLOR)
    ax.set_ylabel("Number of papers", color=palette.AXIS_COLOR)
    ax.tick_params(colors=palette.AXIS_COLOR)
    ax.grid(axis="y", color=palette.GRID_COLOR)
    ax.set_axisbelow(True)
    fig.tight_layout()
    _save(fig, "Fig_papers_per_category")
    plt.close(fig)


def plot_papers_per_year(df) -> None:
    counts = df["YEAR"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(counts.index, counts.values, marker="o", color=palette.CATEGORY_COLORS[palette.CATEGORY_ORDER[0]])
    ax.set_title("Papers per Year", color=palette.TITLE_COLOR)
    ax.set_ylabel("Number of papers", color=palette.AXIS_COLOR)
    ax.tick_params(colors=palette.AXIS_COLOR)
    ax.grid(color=palette.GRID_COLOR)
    ax.set_axisbelow(True)
    fig.tight_layout()
    _save(fig, "Fig_papers_per_year")
    plt.close(fig)


def main() -> None:
    df = load_corpus()
    plot_papers_per_category(df)
    plot_papers_per_year(df)


if __name__ == "__main__":
    main()
