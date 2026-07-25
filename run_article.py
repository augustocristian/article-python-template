"""
run_article.py
Single entry point that regenerates every article artifact in the correct order.

Usage (from project root):
  python run_article.py              # run all phases
  python run_article.py bibtex       # BibTeX only
  python run_article.py tables       # LaTeX tables only
  python run_article.py figures      # figures only
  python run_article.py tables figures   # multiple phases

MPLBACKEND is forced to "Agg" so no matplotlib windows are opened during batch runs.
"""
import os
import sys
import time
import subprocess
from pathlib import Path

# ── Phase toggles (all True = run everything) ─────────────────────────────────
RUN_BIBTEX = True
RUN_TABLES = True
RUN_FIGURES = True

# ── Scripts per phase (executed in listed order) ───────────────────────────────
PHASES: dict[str, list[str]] = {
    "bibtex": [
        "generate_bibtex.py",
    ],
    "tables": [
        "generate_tables.py",
    ],
    "figures": [
        "Fig1_sankey.py",
        "Fig2_stackedbar.py",
        "Fig3_bubble.py",
        "Fig4_distribution.py",
        "Fig5_treechart.py",
        "Fig6_severitycrosstab.py",
    ],
}

PHASE_FLAGS: dict[str, bool] = {
    "bibtex": RUN_BIBTEX,
    "tables": RUN_TABLES,
    "figures": RUN_FIGURES,
}

# ── Environment: suppress matplotlib popup windows, force UTF-8 subprocess I/O ─
ENV = {**os.environ, "MPLBACKEND": "Agg", "PYTHONIOENCODING": "utf-8"}

SCRIPTS_DIR = Path(__file__).parent / "article"

# ── Colours for terminal output ───────────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _run(script: str) -> tuple[bool, float, str]:
    path = SCRIPTS_DIR / script
    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, str(path)],
        env=ENV,
        cwd=str(SCRIPTS_DIR),   # scripts expect CWD = article/ (input/ lives there)
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - start
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, elapsed, output


def _run_phase(phase: str, scripts: list[str]) -> tuple[int, int]:
    print(f"\n{BOLD}-- {phase.upper()} {'-' * (50 - len(phase))}{RESET}")
    ok_count = fail_count = 0
    for script in scripts:
        ok, elapsed, output = _run(script)
        status = f"{GREEN}OK{RESET}" if ok else f"{RED}FAIL{RESET}"
        print(f"  {status}  {script:<48}  {elapsed:5.1f}s")
        if not ok:
            fail_count += 1
            for line in output.splitlines()[-6:]:   # show last 6 lines of error
                print(f"       {YELLOW}{line}{RESET}")
        else:
            ok_count += 1
    return ok_count, fail_count


def main() -> None:
    # Determine which phases to run (CLI args override header flags)
    requested = {a.lower() for a in sys.argv[1:]}
    if requested:
        active_phases = {k: v for k, v in PHASES.items() if k in requested}
        if not active_phases:
            valid = ", ".join(PHASES)
            print(f"Unknown phase(s): {sys.argv[1:]}. Valid: {valid}")
            sys.exit(1)
    else:
        active_phases = {k: v for k, v in PHASES.items() if PHASE_FLAGS.get(k, True)}

    print(f"{BOLD}Regenerating article artifacts — phases: {', '.join(active_phases)}{RESET}")
    wall_start = time.perf_counter()
    total_ok = total_fail = 0

    for phase, scripts in active_phases.items():
        ok, fail = _run_phase(phase, scripts)
        total_ok += ok
        total_fail += fail

    wall_elapsed = time.perf_counter() - wall_start
    print(f"\n{BOLD}Done in {wall_elapsed:.1f}s — {total_ok} OK, {total_fail} FAILED{RESET}")
    if total_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
