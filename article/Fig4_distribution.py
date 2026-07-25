"""
Fig4_distribution.py
Publication distribution: stacked bar by year (panel A) + a top-level donut
of venue-type share (panel B) + two per-venue donuts, one for conferences
and one for journals (panels C & D). Venue type is inferred from the venue
name ("conference"/"journal" substring) — replace `classify_venue` with a
real Publication-Type column if your corpus already has one.

All visual parameters are defined in the header and are fully configurable.
"""
import textwrap

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import pandas as pd

import config
import palette
from palette import apply_style
from data_loader import load_corpus, clean_venue_name

apply_style()

# ── Output / config ────────────────────────────────────────────────────────
OUT_FILENAME = "Fig4_distribution"
TOP_N_CONFERENCES = 5
TOP_N_JOURNALS = 5

VENUE_TYPE_ORDER = ["Conferences", "Journals", "Other"]
VENUE_TYPE_COLORS = {
    "Conferences": palette.VENUE_CONF,
    "Journals": palette.VENUE_JOURNAL,
    "Other": palette.VENUE_OTHER,
}

FS_TITLE = palette.ALL_TITLES
FS_AXIS_LABEL = 12
FS_AXIS_TICKS = 10
FS_PIE_LABELS = 11
FS_PIE_PCT = 10
DONUT_LABEL_WRAP = 18   # characters per line for long venue-name labels


# ── Helpers ───────────────────────────────────────────────────────────────
def classify_venue(venue: str) -> str:
    v = venue.lower()
    if "conf" in v or "symposium" in v or "workshop" in v:
        return "Conferences"
    if "journal" in v or "transactions" in v:
        return "Journals"
    return "Other"


def top_counts(series: pd.Series, top_n: int) -> pd.Series:
    return series.value_counts().iloc[:top_n]


def draw_donut(ax, data: pd.Series, title: str, color_map: dict, fallback=palette.NEUTRAL_FALLBACK) -> None:
    data = data[data > 0]
    if data.empty:
        ax.set_axis_off()
        ax.set_title(title, fontsize=FS_TITLE, fontweight="bold")
        return
    colors = [color_map.get(name, fallback) for name in data.index]
    wrapped_labels = [textwrap.fill(str(name), DONUT_LABEL_WRAP) for name in data.index]
    wedges, _, autotexts = ax.pie(
        data, labels=wrapped_labels, autopct=lambda p: f"{p:.0f}%",
        startangle=140, colors=colors, pctdistance=0.75, labeldistance=1.1,
        textprops={"fontsize": FS_PIE_LABELS, "fontweight": "bold"},
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    for a in autotexts:
        a.set_fontsize(FS_PIE_PCT)
    ax.set_title(title, fontsize=FS_TITLE, fontweight="bold", pad=20)
    ax.add_artist(plt.Circle((0, 0), 0.6, fc="white"))


def main() -> None:
    df = load_corpus()
    df = df.copy()
    df["CleanVenue"] = df["VENUE"].apply(clean_venue_name)
    df["VenueType"] = df["CleanVenue"].apply(classify_venue)

    by_year = df.groupby(["YEAR", "VenueType"]).size().unstack(fill_value=0)
    years = sorted(by_year.index)

    conf_counts = top_counts(df[df["VenueType"] == "Conferences"]["CleanVenue"], TOP_N_CONFERENCES)
    jour_counts = top_counts(df[df["VenueType"] == "Journals"]["CleanVenue"], TOP_N_JOURNALS)
    conf_color_map = {v: palette.CONF_PALETTE[i % len(palette.CONF_PALETTE)] for i, v in enumerate(conf_counts.index)}
    jour_color_map = {v: palette.JOUR_PALETTE[i % len(palette.JOUR_PALETTE)] for i, v in enumerate(jour_counts.index)}

    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.3)
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_pie = fig.add_subplot(gs[0, 1])
    ax_conf = fig.add_subplot(gs[1, 0])
    ax_jour = fig.add_subplot(gs[1, 1])

    bottoms = pd.Series(0, index=years)
    for venue_type in VENUE_TYPE_ORDER:
        values = by_year.get(venue_type, pd.Series(0, index=years)).reindex(years, fill_value=0)
        ax_bar.bar(years, values, bottom=bottoms, color=VENUE_TYPE_COLORS[venue_type], label=venue_type)
        bottoms = bottoms + values

    ax_bar.set_xlabel("Year", fontsize=FS_AXIS_LABEL, fontweight="bold")
    ax_bar.set_ylabel("Nº Papers", fontsize=FS_AXIS_LABEL, fontweight="bold")
    ax_bar.set_xticks(years)
    ax_bar.tick_params(labelsize=FS_AXIS_TICKS, rotation=45)
    ax_bar.set_title("(A) PAPERS PER YEAR", fontsize=FS_TITLE, fontweight="bold")
    ax_bar.legend(fontsize=9)
    ax_bar.spines[["top", "right"]].set_visible(False)

    type_counts = df["VenueType"].value_counts().reindex(VENUE_TYPE_ORDER, fill_value=0)
    draw_donut(ax_pie, type_counts, "(B) VENUE TYPE", VENUE_TYPE_COLORS)
    draw_donut(ax_conf, conf_counts, "(C) CONFERENCES", conf_color_map)
    draw_donut(ax_jour, jour_counts, "(D) JOURNALS", jour_color_map)

    pdf_path = config.FIGURES_DIR / f"{OUT_FILENAME}.pdf"
    png_path = config.OUTPUT_BASE_DIR / f"{OUT_FILENAME}.png"
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    print(f"Saved {pdf_path}")
    print(f"Saved {png_path} (debug preview)")
    plt.close(fig)


if __name__ == "__main__":
    main()
