"""
generate_tables.py
Generates the LaTeX table sheets written into SHEETS_DIR.

Outputs:
  sheet_articles_per_category.tex — one row per category, listing its articles
                                    as \\cite{} keys

Replace ``build_table`` with your article's real table(s) once you have a real
corpus; keep writing to SHEETS_DIR and \\input-ing the result from the
article's LaTeX source. All configurable parameters are in the header below.
"""
from config import SHEETS_DIR
from data_loader import load_corpus, split_values
from palette import CATEGORY_ORDER

# ── Output / config ────────────────────────────────────────────────────────────
OUT_FILENAME = "sheet_articles_per_category.tex"
CAPTION = "Distribution of Articles by Category"
LABEL = "tab:articles_per_category"
COL_SPEC = "l p{25em} r"
EMPTY_CELL = "---"

OUTPUT = SHEETS_DIR / OUT_FILENAME


def article_ref(row) -> str:
    return f"\\cite{{{row['KEY']}}}"


def build_table(df) -> str:
    lines = [
        r"\begin{table}",
        f"    \\caption{{{CAPTION}}}",
        f"    \\label{{{LABEL}}}",
        r"    \centering",
        f"    \\begin{{tabular}}{{{COL_SPEC}}}",
        r"        \hline",
        r"        \textbf{Category} & \textbf{Articles} & \textbf{Total} \\ \hline",
    ]

    for category in CATEGORY_ORDER:
        mask = df["CATEGORY"].apply(lambda cell, category=category: category in split_values(cell))
        rows = df[mask].sort_values("ID")
        refs = ", ".join(article_ref(row) for _, row in rows.iterrows()) or EMPTY_CELL
        lines.append(f"        {category} & {refs} & {len(rows)} \\\\ \\hline")

    lines += [
        r"    \end{tabular}",
        r"\end{table}",
    ]
    return "\n".join(lines)


def main() -> None:
    df = load_corpus()
    latex = build_table(df)
    print(latex)
    OUTPUT.write_text(latex, encoding="utf-8")
    print(f"\nSaved to {OUTPUT}")


if __name__ == "__main__":
    main()
