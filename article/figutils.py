"""
figutils.py
Shared matplotlib figure-saving helper, used by every Fig*.py script so the
save-as-PDF / save-debug-PNG / print / close sequence isn't repeated verbatim
in each one.
"""
import matplotlib.pyplot as plt

from config import FIGURES_DIR, OUTPUT_BASE_DIR
from palette import DEBUG_DPI


def save_figure(fig, out_filename: str) -> None:
    """Save `fig` as `{out_filename}.pdf` in FIGURES_DIR (camera-ready) and a
    PNG debug preview in OUTPUT_BASE_DIR, print both paths, then close it."""
    pdf_path = FIGURES_DIR / f"{out_filename}.pdf"
    png_path = OUTPUT_BASE_DIR / f"{out_filename}.png"
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=DEBUG_DPI, bbox_inches="tight")
    print(f"Saved {pdf_path}")
    print(f"Saved {png_path} (debug preview)")
    plt.close(fig)
