"""Generates the paper's LaTeX tables from the corpus.

Ships with one placeholder table — one row per category, listing the
papers in it as ``\\cite{}`` keys — built on the sample
``input/corpus.csv``. Replace ``build_table`` with your paper's real
table(s) once you have a real corpus; keep writing to ``SHEETS_DIR`` and
``\\input``-ing the result from the paper's LaTeX source.
"""

import config
import palette
from data_loader import load_corpus, split_values

OUTPUT = config.SHEETS_DIR / "sheet_papers_per_category.tex"


def paper_ref(row) -> str:
    return f"\\cite{{{row['KEY']}}}"


def build_table(df) -> str:
    lines = [
        r"\begin{table}",
        r"    \caption{Distribution of Papers by Category}",
        r"    \label{tab:papers_per_category}",
        r"    \centering",
        r"    \begin{tabular}{l p{25em} r}",
        r"        \hline",
        r"        \textbf{Category} & \textbf{Papers} & \textbf{Total} \\ \hline",
    ]

    for category in palette.CATEGORY_ORDER:
        mask = df["CATEGORY"].apply(lambda cell: category in split_values(cell))
        rows = df[mask].sort_values("ID")
        refs = ", ".join(paper_ref(row) for _, row in rows.iterrows()) or "---"
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
