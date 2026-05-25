"""Print a compact context summary for phase1_stand work."""

from __future__ import annotations

from pathlib import Path


HARNESS_DIR = Path(__file__).resolve().parents[1]
PHASE_DIR = HARNESS_DIR.parent
PROJECT_ROOT = PHASE_DIR.parents[2]
ISAACLAB_SCRIPTS_ROOT = PROJECT_ROOT.parent


def main() -> int:
    print("phase1_stand context")
    print(f"project_root: {PROJECT_ROOT}")
    print(f"phase_dir: {PHASE_DIR}")
    print(f"isaaclab_scripts_root: {ISAACLAB_SCRIPTS_ROOT}")
    print("phase files:")
    for path in sorted(PHASE_DIR.glob("*.py")):
        print(f"- {path.relative_to(PROJECT_ROOT)}")
    print("harness contracts:")
    for path in sorted((HARNESS_DIR / "constraints").glob("*.yaml")):
        print(f"- {path.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
