"""Central path configuration — reads overrides from .env.

Every data-loading and artifact-generation script resolves its input/output
paths through this module instead of hardcoding relative paths, so the
pipeline can run from any working directory and target an external
article repo (e.g. an Overleaf git bridge) directly.

By default everything reads from and writes to this package's own
``input/``/``outputs/`` folders, which keeps a fresh checkout runnable with
zero configuration. Point ``ARTICLE_OUTPUT_BASE_DIR`` at the actual paper
repo (e.g. an Overleaf git bridge checkout) and ``RP_OUTPUT_BASE_DIR`` at
its companion replication-package repo once you have them.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")


def _resolve(val) -> Path:
    """Resolve a .env value against PROJECT_ROOT if relative (scripts run with
    cwd=PACKAGE_DIR, so a bare relative path in .env would otherwise resolve
    against the wrong directory)."""
    p = Path(val)
    return p if p.is_absolute() else PROJECT_ROOT / p


OUTPUT_BASE_DIR = _resolve(os.environ.get("OUTPUT_BASE_DIR", PACKAGE_DIR / "outputs"))
ARTICLE_OUTPUT_BASE_DIR = _resolve(os.environ.get("ARTICLE_OUTPUT_BASE_DIR", OUTPUT_BASE_DIR))
RP_OUTPUT_BASE_DIR = _resolve(os.environ.get("RP_OUTPUT_BASE_DIR", OUTPUT_BASE_DIR))
INPUT_DIR = _resolve(os.environ.get("INPUT_DIR", PACKAGE_DIR / "input"))

FIGURES_DIR = ARTICLE_OUTPUT_BASE_DIR / "figures"
SHEETS_DIR = ARTICLE_OUTPUT_BASE_DIR / "sheets"
RP_DATA_DIR = RP_OUTPUT_BASE_DIR / "data"

CORPUS_CSV = INPUT_DIR / "corpus.csv"
TAXONOMY_CSV = INPUT_DIR / "taxonomy.csv"
FAILURE_OBSERVATIONS_CSV = INPUT_DIR / "failure_observations.csv"
BIBLIO_BIB = ARTICLE_OUTPUT_BASE_DIR / "biblio.bib"

# Output folders are created dynamically — nothing needs to exist up front.
for _dir in (OUTPUT_BASE_DIR, FIGURES_DIR, SHEETS_DIR, RP_DATA_DIR, INPUT_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
