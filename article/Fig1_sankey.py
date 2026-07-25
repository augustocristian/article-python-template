"""
Fig1_sankey.py
Three-column Sankey ("sandbox" flow): where each article was found, when in
the lifecycle the failure it studies is detected, and whether that detection
was performed by a human or by an LLM.

    Source (ACM/IEEE/DBLP/arXiv) -> Detection phase (Static/Build/Runtime)
                                 -> Detected by (Human/LLM)

Ribbon width is proportional to the number of articles; an article listed
under several categories still counts once per flow. Column headers are
drawn as paper-coordinate annotations above their node column (Plotly's
"paper" reference frame — the whole figure area, not this template's articles).

Data via data_loader only. Uses Plotly (kaleido) for static PDF export —
matplotlib has no good multi-column Sankey primitive. All visual parameters
in the header.
"""
import plotly.graph_objects as go

from config import FIGURES_DIR, OUTPUT_BASE_DIR
from data_loader import load_corpus
from palette import FONT_FAMILY   # keep font consistent with the matplotlib figures

# ── Output / config ────────────────────────────────────────────────────────────
OUT_FILENAME = "Fig1_sankey"
TITLE_TEXT = "FAILURE DETECTION: SOURCE, PHASE AND DETECTOR"
IMAGE_SCALE = 2   # PDF export resolution multiplier

# The three Sankey columns, in order: (corpus column, header label)
SANKEY_COLS = [
    ("SOURCE", "SOURCE"),
    ("DETECTION", "DETECTION PHASE"),
    ("DETECTED_BY", "DETECTED BY"),
]

# ── Colors (imported from master palette) ─────────────────────────────────────
from palette import (
    SOURCE_ORDER, SOURCE_COLORS,
    DETECTION_ORDER, DETECTION_COLORS,
    DETECTOR_ORDER, DETECTOR_COLORS,
    NEUTRAL_FALLBACK, NEUTRAL_MID, TITLE_COLOR, BG_TRANSPARENT, rgba,
)

# Node order (top -> bottom) and color per column, keyed by corpus column name.
COLUMN_ORDER = {
    "SOURCE": SOURCE_ORDER,
    "DETECTION": DETECTION_ORDER,
    "DETECTED_BY": DETECTOR_ORDER,
}
COLOR_MAP = {**SOURCE_COLORS, **DETECTION_COLORS, **DETECTOR_COLORS}

LINK_OPACITY = 0.40   # semi-transparent ribbons, colored from their source node

# ── Fonts (all font sizes, in points) ─────────────────────────────────────────
FS_NODES = 15    # node labels
FS_HEADER = 16   # column header labels
FS_TITLE = 20

# ── Layout ────────────────────────────────────────────────────────────────────
FIG_WIDTH = 1150
FIG_HEIGHT = 620
MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B = 30, 30, 105, 30
NODE_PAD = 30         # px gap between stacked nodes in the same column
NODE_THICKNESS = 18    # px node cross-section width
HEADER_Y = 1.06        # column header y-position (paper coordinates)
COLUMN_X = [0.01, 0.5, 0.99]   # header x-positions (paper coordinates)

# ── Style (line widths) ───────────────────────────────────────────────────────
NODE_LINE_WIDTH = 0


def build_nodes() -> tuple[list, dict, list]:
    """Return (labels, {(column, value): node_index}, node_colors)."""
    labels, index, colors = [], {}, []
    for col, _ in SANKEY_COLS:
        for value in COLUMN_ORDER[col]:
            index[(col, value)] = len(labels)
            labels.append(f" {value}")
            colors.append(COLOR_MAP.get(value, NEUTRAL_FALLBACK))
    return labels, index, colors


def build_links(df, index: dict) -> tuple[list, list, list, list]:
    sources, targets, values, colors = [], [], [], []
    for col_a, col_b in zip(SANKEY_COLS[:-1], SANKEY_COLS[1:]):
        key_a, key_b = col_a[0], col_b[0]
        flows: dict[tuple[str, str], int] = {}
        for _, row in df.iterrows():
            a, b = str(row[key_a]).strip(), str(row[key_b]).strip()
            if a and b:
                flows[(a, b)] = flows.get((a, b), 0) + 1
        for (a, b), count in flows.items():
            sources.append(index[(key_a, a)])
            targets.append(index[(key_b, b)])
            values.append(count)
            colors.append(rgba(COLOR_MAP.get(a, NEUTRAL_FALLBACK), LINK_OPACITY))
    return sources, targets, values, colors


def main() -> None:
    df = load_corpus()
    labels, index, node_colors = build_nodes()
    sources, targets, values, link_colors = build_links(df, index)

    fig = go.Figure(go.Sankey(
        node={"pad": NODE_PAD, "thickness": NODE_THICKNESS,
              "line": {"width": NODE_LINE_WIDTH}, "label": labels, "color": node_colors},
        link={"source": sources, "target": targets, "value": values, "color": link_colors},
    ))

    annotations = [
        {
            "x": x, "y": HEADER_Y, "xref": "paper", "yref": "paper",
            "text": f"<b>{header}</b>", "showarrow": False,
            "font": {"family": FONT_FAMILY, "size": FS_HEADER, "color": NEUTRAL_MID},
            "xanchor": anchor, "yanchor": "middle",
        }
        for x, (_, header), anchor in zip(COLUMN_X, SANKEY_COLS, ["left", "center", "right"])
    ]

    fig.update_layout(
        title={"text": TITLE_TEXT, "x": 0.5, "xanchor": "center",
               "font": {"size": FS_TITLE, "color": TITLE_COLOR}},
        font={"family": FONT_FAMILY, "size": FS_NODES, "color": TITLE_COLOR},
        annotations=annotations,
        paper_bgcolor=BG_TRANSPARENT,
        width=FIG_WIDTH, height=FIG_HEIGHT,
        margin={"l": MARGIN_L, "r": MARGIN_R, "t": MARGIN_T, "b": MARGIN_B},
    )

    pdf_path = FIGURES_DIR / f"{OUT_FILENAME}.pdf"
    svg_path = OUTPUT_BASE_DIR / f"{OUT_FILENAME}.svg"
    fig.write_image(str(pdf_path), scale=IMAGE_SCALE)
    fig.write_image(str(svg_path))
    print(f"Saved {pdf_path}")
    print(f"Saved {svg_path} (debug preview)")


if __name__ == "__main__":
    main()
