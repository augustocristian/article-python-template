"""
Fig4_distribution.py
Publication distribution: stacked bar chart by year (panel A) + donuts by
venue type (panel B) and by venue name, split conferences (panel C) and
journals (panel D).

Venue type comes from the corpus' VENUE_TYPE column (arXiv / Conference /
Journal); arXiv preprints are excluded from the per-venue donuts, which only
name real conferences and journals.

Data via data_loader only. All visual parameters in the header.
"""
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import pandas as pd
from palette import apply_style; apply_style()

from data_loader import load_corpus, clean_venue_name
from figutils import save_figure
from palette import ALL_TITLES

# ── Output / config ────────────────────────────────────────────────────────────
OUT_FILENAME = "Fig4_distribution"
TITLE_A = "(A) ARTICLES PER YEAR"
TITLE_B = "(B) ARTICLE TYPE DISTRIBUTION"
TITLE_C = "(C) DISTRIBUTION OF CONFERENCES"
TITLE_D = "(D) DISTRIBUTION OF JOURNALS"

# Number of individually-named venues shown in the donuts (panels C & D).
TOP_N_CONFERENCES = 8
TOP_N_JOURNALS = 8
# When False, the aggregated "Others" wedge is dropped entirely — only the
# top-N named venues above are shown.
INCLUDE_OTHERS = True
OTHERS_LABEL = "Others"

COL_VENUE = "VENUE"
COL_VENUE_TYPE = "VENUE_TYPE"

# Panel A stacking order, bottom -> top. Deliberately its own constant rather
# than reusing palette.VENUE_TYPE_ORDER: that order also drives panel B's
# donut (wedge order/colors), which keeps its own arXiv/Conference/Journal
# order independent of how the bars stack.
BAR_STACK_ORDER = ["Journal", "Conference", "arXiv"]

# ── Colors (imported from master palette) ─────────────────────────────────────
from palette import (
    VENUE_TYPE_ORDER, VENUE_TYPE_COLORS,
    CONF_PALETTE, JOUR_PALETTE, NEUTRAL_MUTED as OTHERS_COLOR,
)

TOP_PIE_COLORS = [VENUE_TYPE_COLORS[t] for t in VENUE_TYPE_ORDER]
# Graduated palettes for the top-N venue donuts (conferences = blues, journals = teals)
CONF_TINTS = CONF_PALETTE * 3   # cycle if more venues than palette entries
JOUR_TINTS = JOUR_PALETTE * 3
WEDGE_EDGE_COLOR = "white"

# ── Fonts (all font sizes, in points) ─────────────────────────────────────────
# Bar chart (panel A)
FS_BAR_AXIS_LABEL = 13
FS_BAR_AXIS_NUMBERS = 11
FS_BAR_COUNT_LABELS = 11   # totals on top of bars
FS_BAR_LEGEND = 11

# Top-level donut (panel B)
FS_PIE_LABELS = 12   # category labels on wedges
FS_PIE_PCT = 11      # percentage + count inside wedges

# Venue donuts (panels C & D)
FS_DONUT_LABELS = 9
FS_DONUT_PCT = 9

# ── Wrap widths (characters per line) ─────────────────────────────────────────
DONUT_LABEL_WRAP = 18   # long venue-name labels

# ── Layout ────────────────────────────────────────────────────────────────────
FIG_W = 15
FIG_H = 12
GRIDSPEC_HEIGHT = [1.0, 1.0]   # height ratios of the two rows
GRIDSPEC_HSPACE = 0.35
GRIDSPEC_WSPACE = 0.25

BAR_LABEL_OFFSET = 0.15   # vertical gap between bar top and count label
BAR_X_ROTATION = 45
BAR_LEGEND_LOC = "upper left"

PIE_START_ANGLE = 90
PIE_PCT_DISTANCE = 0.75
PIE_LABEL_DISTANCE = 1.14
PIE_HOLE_RADIUS = 0.60    # inner white circle radius

DONUT_START_ANGLE = 140
DONUT_PCT_DISTANCE = 0.75
DONUT_LABEL_DIST = 1.1
DONUT_HOLE_RADIUS = 0.60

# Shared by all four panels (A-D), so every title sits the same distance from
# its plot and the top row (A, B) stays vertically aligned.
TITLE_PAD = 10

# ── Style (line widths / alphas) ──────────────────────────────────────────────
BAR_LEGEND_ALPHA = 0.85
PIE_WEDGE_LINEWIDTH = 3
DONUT_WEDGE_LW = 2


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_top_counts(series: pd.Series, top_n: int) -> pd.Series:
    """Top-N venue counts, optionally folding the tail into an 'Others' wedge."""
    counts = series.value_counts()
    if not INCLUDE_OTHERS or len(counts) <= top_n:
        return counts.iloc[:top_n]
    top = counts.iloc[:top_n]
    others = counts.iloc[top_n:].sum()
    return pd.concat([top, pd.Series([others], index=[OTHERS_LABEL])])


def make_colors(index, tints: list) -> list:
    return [
        OTHERS_COLOR if str(name).lower() in ("others", "other")
        else tints[i % len(tints)]
        for i, name in enumerate(index)
    ]


def wrap_labels(index) -> list:
    from textwrap import fill
    return [fill(str(name), DONUT_LABEL_WRAP) for name in index]


def draw_donut(ax, data: pd.Series, title: str, colors: list) -> None:
    if data.empty:
        ax.set_axis_off()
        ax.set_title(title, fontsize=ALL_TITLES, fontweight="bold", pad=TITLE_PAD)
        return
    wedges, _, autotexts = ax.pie(
        data,
        labels=wrap_labels(data.index),
        autopct=lambda p: f"{p:.1f}%",
        startangle=DONUT_START_ANGLE,
        colors=colors,
        pctdistance=DONUT_PCT_DISTANCE,
        labeldistance=DONUT_LABEL_DIST,
        textprops={"fontsize": FS_DONUT_LABELS, "fontweight": "bold"},
        wedgeprops={"edgecolor": WEDGE_EDGE_COLOR, "linewidth": DONUT_WEDGE_LW},
    )
    for i, a in enumerate(autotexts):
        angle = (wedges[i].theta2 + wedges[i].theta1) / 2
        a.set_rotation(angle + 180 if 90 < angle < 270 else angle)
        a.set_fontsize(FS_DONUT_PCT)
        a.set_va("center")
        a.set_ha("center")
    ax.set_title(title, fontsize=ALL_TITLES, fontweight="bold", pad=TITLE_PAD)
    ax.add_artist(plt.Circle((0, 0), DONUT_HOLE_RADIUS, fc="white"))


# ── Data loading ──────────────────────────────────────────────────────────────
def load_panels():
    df = load_corpus().copy()
    df["CleanName"] = df[COL_VENUE].apply(clean_venue_name)

    conf_df = df[df[COL_VENUE_TYPE] == "Conference"]
    jour_df = df[df[COL_VENUE_TYPE] == "Journal"]

    type_counts = df[COL_VENUE_TYPE].value_counts().reindex(VENUE_TYPE_ORDER, fill_value=0)
    conf_counts = get_top_counts(conf_df["CleanName"], TOP_N_CONFERENCES)
    jour_counts = get_top_counts(jour_df["CleanName"], TOP_N_JOURNALS)

    df["Year"] = pd.to_numeric(df["YEAR"], errors="coerce")
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    by_year = df.groupby(["Year", COL_VENUE_TYPE]).size().unstack(fill_value=0)

    return by_year, type_counts, conf_counts, jour_counts


def main() -> None:
    by_year, type_counts, conf_counts, jour_counts = load_panels()
    years = list(by_year.index)

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    gs = gridspec.GridSpec(2, 2, figure=fig, height_ratios=GRIDSPEC_HEIGHT,
                           hspace=GRIDSPEC_HSPACE, wspace=GRIDSPEC_WSPACE)
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_pie = fig.add_subplot(gs[0, 1])
    ax_conf = fig.add_subplot(gs[1, 0])
    ax_jour = fig.add_subplot(gs[1, 1])

    # Panel A — Articles per Year, stacked bottom-to-top per BAR_STACK_ORDER
    bottoms = pd.Series(0, index=years)
    for venue_type in BAR_STACK_ORDER:
        values = by_year.get(venue_type, pd.Series(0, index=years)).reindex(years, fill_value=0)
        ax_bar.bar(years, values, bottom=bottoms,
                   color=VENUE_TYPE_COLORS[venue_type], label=venue_type)
        bottoms = bottoms + values

    for year, total in zip(years, bottoms):
        ax_bar.text(year, total + BAR_LABEL_OFFSET, str(int(total)),
                    ha="center", va="bottom",
                    fontsize=FS_BAR_COUNT_LABELS, fontweight="bold")

    ax_bar.set_xlabel("Year", fontsize=FS_BAR_AXIS_LABEL, fontweight="bold")
    ax_bar.set_ylabel("Nº Articles", fontsize=FS_BAR_AXIS_LABEL, fontweight="bold")
    ax_bar.set_xticks(years)
    ax_bar.set_xticklabels([str(y) for y in years])
    ax_bar.tick_params(axis="x", rotation=BAR_X_ROTATION, labelsize=FS_BAR_AXIS_NUMBERS)
    ax_bar.tick_params(axis="y", labelsize=FS_BAR_AXIS_NUMBERS)
    ax_bar.set_title(TITLE_A, fontsize=ALL_TITLES, fontweight="bold", pad=TITLE_PAD)
    ax_bar.legend(fontsize=FS_BAR_LEGEND, loc=BAR_LEGEND_LOC, framealpha=BAR_LEGEND_ALPHA)
    ax_bar.spines[["top", "right"]].set_visible(False)

    # Panel B — Article type distribution (top-level donut)
    total = type_counts.sum()
    _, _, autotexts = ax_pie.pie(
        type_counts,
        labels=list(type_counts.index),
        autopct=lambda p: f"{p:.1f}%\n({int(round(p * total / 100))})",
        startangle=PIE_START_ANGLE,
        colors=TOP_PIE_COLORS,
        pctdistance=PIE_PCT_DISTANCE,
        labeldistance=PIE_LABEL_DISTANCE,
        textprops={"fontsize": FS_PIE_LABELS, "fontweight": "bold"},
        wedgeprops={"edgecolor": WEDGE_EDGE_COLOR, "linewidth": PIE_WEDGE_LINEWIDTH},
    )
    for a in autotexts:
        a.set_fontsize(FS_PIE_PCT)
        a.set_fontweight("bold")
    ax_pie.set_title(TITLE_B, fontsize=ALL_TITLES, fontweight="bold", pad=TITLE_PAD)
    ax_pie.add_artist(plt.Circle((0, 0), PIE_HOLE_RADIUS, fc="white"))

    # Panels C & D — Venue donuts
    draw_donut(ax_conf, conf_counts, TITLE_C, make_colors(conf_counts.index, CONF_TINTS))
    draw_donut(ax_jour, jour_counts, TITLE_D, make_colors(jour_counts.index, JOUR_TINTS))

    save_figure(fig, OUT_FILENAME)


if __name__ == "__main__":
    main()
