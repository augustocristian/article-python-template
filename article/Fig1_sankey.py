"""
Fig1_sankey.py
Sankey diagram: Category -> Venue flow, link width proportional to the
number of papers. Uses Plotly (kaleido) for static PDF export, since
matplotlib has no good multi-column Sankey primitive.
"""
import plotly.graph_objects as go

import config
import palette
from data_loader import load_corpus, split_values, clean_venue_name

OUT_FILENAME = "Fig1_sankey"


def build_flows(df) -> dict:
    flows: dict[tuple[str, str], int] = {}
    for _, row in df.iterrows():
        venue = clean_venue_name(row["VENUE"])
        for category in split_values(row["CATEGORY"]):
            key = (category, venue)
            flows[key] = flows.get(key, 0) + 1
    return flows


def main() -> None:
    df = load_corpus()
    flows = build_flows(df)

    categories = palette.CATEGORY_ORDER
    venues = sorted({venue for _, venue in flows})
    labels = categories + venues
    index = {label: i for i, label in enumerate(labels)}

    sources, targets, values, link_colors = [], [], [], []
    for (category, venue), count in flows.items():
        sources.append(index[category])
        targets.append(index[venue])
        values.append(count)
        link_colors.append(palette.CATEGORY_COLORS.get(category, palette.NEUTRAL_FALLBACK))

    node_colors = (
        [palette.CATEGORY_COLORS.get(c, palette.NEUTRAL_FALLBACK) for c in categories]
        + [palette.GRAY] * len(venues)
    )

    fig = go.Figure(go.Sankey(
        node=dict(label=labels, color=node_colors, pad=20, thickness=18,
                  line=dict(color="white", width=0.5)),
        link=dict(source=sources, target=targets, value=values, color=link_colors),
    ))
    fig.update_layout(
        title_text="Papers by Category and Venue",
        font=dict(size=14, color=palette.TITLE_COLOR),
        paper_bgcolor=palette.BG_TRANSPARENT,
    )

    pdf_path = config.FIGURES_DIR / f"{OUT_FILENAME}.pdf"
    svg_path = config.OUTPUT_BASE_DIR / f"{OUT_FILENAME}.svg"
    fig.write_image(str(pdf_path))
    fig.write_image(str(svg_path))
    print(f"Saved {pdf_path}")
    print(f"Saved {svg_path} (debug preview)")


if __name__ == "__main__":
    main()
