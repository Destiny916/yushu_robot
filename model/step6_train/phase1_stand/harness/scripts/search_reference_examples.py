"""Search declared project and IsaacLab reference roots for examples."""

from __future__ import annotations

import argparse
from pathlib import Path


HARNESS_DIR = Path(__file__).resolve().parents[1]
PHASE_DIR = HARNESS_DIR.parent
PROJECT_ROOT = PHASE_DIR.parents[2]
ISAACLAB_SCRIPTS_ROOT = PROJECT_ROOT.parent
ISAACLAB_ROOT = ISAACLAB_SCRIPTS_ROOT.parent

SEARCH_ROOTS = (
    PROJECT_ROOT,
    ISAACLAB_SCRIPTS_ROOT / "demos",
    ISAACLAB_SCRIPTS_ROOT / "tutorials",
    ISAACLAB_SCRIPTS_ROOT / "reinforcement_learning",
    ISAACLAB_SCRIPTS_ROOT / "environments",
    ISAACLAB_ROOT / "source",
)

SKIP_DIRS = {".git", ".gitnexus", "__pycache__", "logs", "runs", "outputs"}
TEXT_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".toml", ".json", ".txt"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search yushu_robot and IsaacLab reference examples.")
    parser.add_argument("pattern", help="Case-sensitive text to search for.")
    parser.add_argument("--max-results", type=int, default=20, help="Stop after this many matches.")
    return parser.parse_args()


def iter_text_files(root: Path):
    if not root.exists():
        return
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def main() -> int:
    args = parse_args()
    matches = 0
    print("search roots:")
    for root in SEARCH_ROOTS:
        if root.exists():
            print(f"- {root.as_posix()}")

    for root in SEARCH_ROOTS:
        for path in iter_text_files(root):
            try:
                lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue
            for line_number, line in enumerate(lines, start=1):
                if args.pattern in line:
                    print(f"{path}:{line_number}: {line.strip()}")
                    matches += 1
                    if matches >= args.max_results:
                        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
