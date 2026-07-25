"""
Fig5_treechart.py
Hierarchical tree chart of the failure-type taxonomy.
Levels: Focus -> Category -> Subcategory -> Failure Type.

Two figures are generated, one per Focus group:
  - Fig5_treechart_runtime.pdf : the "Runtime Failures" taxonomy
  - Fig5_treechart_build.pdf   : the "Build Failures" taxonomy

All visual parameters are defined in the header below.
"""
import textwrap

import matplotlib.patheffects as mpe
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

import config
import palette
from palette import apply_style
from data_loader import build_hierarchy_lookups

apply_style()

# ── Output ────────────────────────────────────────────────────────────────
# One figure per Focus group. Each entry maps a Focus label to its output stem.
FOCUS_OUTPUTS = {
    "Runtime Failures": "Fig5_treechart_runtime",
    "Build Failures": "Fig5_treechart_build",
}

LEVEL_HEADERS = ["FOCUS", "CATEGORY", "SUBCATEGORY", "FAILURE TYPE"]

# ── Fonts (points) ────────────────────────────────────────────────────────
FS_HEADER = 13
FS = [12, 11, 10, 9]              # per level: Focus, Category, Subcategory, Failure Type
FONTWEIGHT = ["bold", "bold", "bold", "bold"]
TEXT_LINESPACING = 1.15

# ── Text color / stroke ──────────────────────────────────────────────────
LEVEL_TEXT_COLOR = ["white", "white", "white", "white"]
LEVEL_TEXT_STROKE = [None, None, "black", "black"]
LEVEL_TEXT_STROKE_LW = 1.4

# Lightening factor (0 = original color, 1 = white) applied per level, so
# every node under a Category inherits that Category's color as a tint.
LIGHTEN = [0.0, 0.0, 0.35, 0.55]

# ── Wrap widths (characters per line) ────────────────────────────────────
WRAP = [12, 16, 20, 26]

# ── Layout ────────────────────────────────────────────────────────────────
FIG_W = 14
TOP_MARGIN = 0.5
BOTTOM_MARGIN = 0.9
HEADER_Y = -0.55
LEAF_SPACING = 0.42
CAT_GAP = 0.14
LEVEL_X = [1.0, 3.4, 6.2, 9.6]     # column x-centers, in inches
BOX_W = [1.7, 2.3, 2.6, 3.2]
BOX_H = [0.55, 0.34, 0.34, 0.30]
BOXSTYLE = ["round,pad=0.06", "round,pad=0.05", "round,pad=0.04", "round,pad=0.03"]
CONNECTOR_LW = 0.7


# ── Tree node ─────────────────────────────────────────────────────────────
class Node:
    def __init__(self, label: str, level: int, base_color: str):
        self.label = label
        self.level = level
        self.base_color = base_color
        self.children: list["Node"] = []
        self.x = LEVEL_X[level]
        self.y = 0.0
        self.content_h = 0.0

    @property
    def color(self) -> str:
        return palette.lighten(self.base_color, LIGHTEN[self.level])

    @property
    def text_color(self) -> str:
        return LEVEL_TEXT_COLOR[self.level]

    def assign_y(self, counter: list[float]) -> None:
        if not self.children:
            self.y = counter[0]
            counter[0] += LEAF_SPACING
        else:
            for child in self.children:
                child.assign_y(counter)
            self.y = (self.children[0].y + self.children[-1].y) / 2

    def all_nodes(self):
        yield self
        for child in self.children:
            yield from child.all_nodes()

    def all_edges(self):
        for child in self.children:
            yield (self, child)
            yield from child.all_edges()


# ── Build tree for a single Focus group ──────────────────────────────────
def build_focus_node(focus_label: str, lookups: dict) -> Node:
    focus_color = palette.FOCUS_COLORS.get(focus_label, palette.NEUTRAL_MUTED)
    focus_node = Node(focus_label, 0, focus_color)
    counter = [0.0]

    ordered_cats = sorted(lookups["focus_cats"].get(focus_label, []))
    for cat_idx, category in enumerate(ordered_cats):
        cat_color = palette.CATEGORY_COLORS.get(category, palette.NEUTRAL_FALLBACK)
        cat_node = Node(category, 1, cat_color)

        for subcategory in sorted(lookups["cat_subs"].get(category, [])):
            sub_node = Node(subcategory, 2, cat_color)
            for failure_type in sorted(lookups["sub_items"].get(subcategory, [])):
                sub_node.children.append(Node(failure_type, 3, cat_color))
            cat_node.children.append(sub_node)

        cat_node.assign_y(counter)
        focus_node.children.append(cat_node)
        if cat_idx < len(ordered_cats) - 1:
            counter[0] += CAT_GAP

    if focus_node.children:
        focus_node.y = (focus_node.children[0].y + focus_node.children[-1].y) / 2
    focus_node.content_h = counter[0]
    return focus_node


def draw_node(ax, node: Node) -> None:
    bw, bh = BOX_W[node.level], BOX_H[node.level]
    ax.add_patch(FancyBboxPatch(
        (node.x - bw / 2, node.y - bh / 2), bw, bh,
        boxstyle=BOXSTYLE[node.level],
        facecolor=node.color, edgecolor="none", linewidth=0, zorder=3,
    ))
    label = "\n".join(textwrap.wrap(node.label, width=WRAP[node.level]))
    stroke_color = LEVEL_TEXT_STROKE[node.level]
    effects = ([mpe.withStroke(linewidth=LEVEL_TEXT_STROKE_LW, foreground=stroke_color),
                mpe.Normal()] if stroke_color else None)
    ax.text(node.x, node.y, label, ha="center", va="center",
            fontsize=FS[node.level], fontweight=FONTWEIGHT[node.level],
            color=node.text_color, linespacing=TEXT_LINESPACING,
            path_effects=effects, zorder=4)


def draw_connector(ax, parent: Node, child: Node) -> None:
    px = parent.x + BOX_W[parent.level] / 2
    cx = child.x - BOX_W[child.level] / 2
    mid_x = (px + cx) / 2
    ax.plot([px, mid_x, mid_x, cx], [parent.y, parent.y, child.y, child.y],
            color=palette.CONNECTOR_COLOR, linewidth=CONNECTOR_LW,
            solid_capstyle="round", zorder=2)


def render_focus(focus_label: str, out_filename: str, lookups: dict) -> None:
    focus_node = build_focus_node(focus_label, lookups)
    fig_h = focus_node.content_h + TOP_MARGIN + BOTTOM_MARGIN

    fig, ax = plt.subplots(figsize=(FIG_W, fig_h))
    ax.set_xlim(0, FIG_W)
    ax.set_ylim(-BOTTOM_MARGIN, focus_node.content_h + TOP_MARGIN)
    ax.axis("off")
    ax.invert_yaxis()

    for parent, child in focus_node.all_edges():
        draw_connector(ax, parent, child)
    for node in focus_node.all_nodes():
        draw_node(ax, node)

    for x, label in zip(LEVEL_X, LEVEL_HEADERS):
        ax.text(x, HEADER_Y, label, ha="center", va="center",
                fontsize=FS_HEADER, fontweight="bold", color=palette.NEUTRAL_DARK, zorder=5)

    pdf_path = config.FIGURES_DIR / f"{out_filename}.pdf"
    png_path = config.OUTPUT_BASE_DIR / f"{out_filename}.png"
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    print(f"Saved {pdf_path}")
    print(f"Saved {png_path} (debug preview)")
    plt.close(fig)


def main() -> None:
    lookups = build_hierarchy_lookups()
    for focus_label, out_filename in FOCUS_OUTPUTS.items():
        if focus_label not in lookups["focus_cats"]:
            print(f"[{out_filename}] No categories for focus={focus_label!r} — skipping.")
            continue
        render_focus(focus_label, out_filename, lookups)


if __name__ == "__main__":
    main()
