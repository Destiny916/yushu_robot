"""Summarize a phase1_stand run directory without loading checkpoints."""

from __future__ import annotations

import argparse
from pathlib import Path


HARNESS_DIR = Path(__file__).resolve().parents[1]
PHASE_DIR = HARNESS_DIR.parent
PROJECT_ROOT = PHASE_DIR.parents[2]
DEFAULT_LOG_ROOT = PROJECT_ROOT / "logs" / "rsl_rl" / "g1_stand"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize a G1 standing run directory.")
    parser.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT)
    parser.add_argument("--run", default="", help="Run directory name. Empty means latest by name.")
    return parser.parse_args()


def resolve_run(log_root: Path, run_name: str) -> Path | None:
    if run_name:
        candidate = log_root / run_name
        return candidate if candidate.is_dir() else None
    runs = sorted(path for path in log_root.glob("*") if path.is_dir())
    return runs[-1] if runs else None


def main() -> int:
    args = parse_args()
    run_dir = resolve_run(args.log_root, args.run)
    if run_dir is None:
        print(f"no run directory found under {args.log_root}")
        return 1

    checkpoints = sorted(run_dir.glob("model_*.pt"))
    alias = run_dir / "checkpoint_stand.pt"
    print(f"run: {run_dir}")
    print(f"checkpoints: {len(checkpoints)}")
    print(f"latest_checkpoint: {checkpoints[-1].name if checkpoints else ''}")
    print(f"stable_alias_exists: {alias.is_file()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
