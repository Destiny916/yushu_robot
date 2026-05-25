"""Validate the Phase 1 standing harness contracts against current code."""

from __future__ import annotations

from pathlib import Path
import sys


HARNESS_DIR = Path(__file__).resolve().parents[1]
PHASE_DIR = HARNESS_DIR.parent
PROJECT_ROOT = PHASE_DIR.parents[2]


REQUIRED_FILES = (
    "stand_env_cfg.py",
    "stand_rewards.py",
    "stand_ppo_cfg.py",
    "train_stand.py",
    "play_stand.py",
    "stand_actions.py",
    "stand_action_limits.py",
)

REQUIRED_CODE_MARKERS = (
    "ClampedJointPositionActionCfg",
    "ACTION_TARGET_LIMIT_MARGIN",
    "ACTION_SCALE",
    "COLLAPSE_GROUND_CONTACT_MIN_LIMBS = 3",
    "JOINT_LIMIT_TERMINATION_PENALTY_WEIGHT = -500.0",
    "COLLAPSE_GROUND_CONTACT_PENALTY_WEIGHT = -500.0",
    "SHOULDER_POSTURE_JOINTS",
    "root_height_below_minimum_fn",
)


def load_simple_yaml_list(path: Path, key: str) -> list[str]:
    """Load a top-level nested list from the harness YAML files.

    The harness YAML intentionally stays simple so this script can remain
    stdlib-only and runnable without IsaacLab or PyYAML installed.
    """

    lines = path.read_text(encoding="utf-8").splitlines()
    target = f"{key}:"
    collecting = False
    key_indent = 0
    values: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        if stripped == target:
            collecting = True
            key_indent = indent
            continue

        if collecting:
            if indent <= key_indent and not stripped.startswith("- "):
                break
            if stripped.startswith("- "):
                values.append(stripped[2:].strip().strip('"').strip("'"))

    return values


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    env_cfg_path = PHASE_DIR / "stand_env_cfg.py"
    rewards_path = PHASE_DIR / "stand_rewards.py"
    reward_contract_path = HARNESS_DIR / "constraints" / "reward_contract.yaml"
    termination_contract_path = HARNESS_DIR / "constraints" / "termination_contract.yaml"

    for file_name in REQUIRED_FILES:
        require((PHASE_DIR / file_name).is_file(), f"missing phase file: {file_name}", failures)

    require(env_cfg_path.is_file(), "missing stand_env_cfg.py", failures)
    require(rewards_path.is_file(), "missing stand_rewards.py", failures)
    require(reward_contract_path.is_file(), "missing reward_contract.yaml", failures)
    require(termination_contract_path.is_file(), "missing termination_contract.yaml", failures)

    env_source = env_cfg_path.read_text(encoding="utf-8") if env_cfg_path.is_file() else ""
    reward_source = rewards_path.read_text(encoding="utf-8") if rewards_path.is_file() else ""
    combined_source = env_source + "\n" + reward_source
    required_reward_terms = load_simple_yaml_list(reward_contract_path, "required_reward_terms")
    required_termination_terms = load_simple_yaml_list(termination_contract_path, "required_termination_terms")

    for term in required_reward_terms:
        require(f'"{term}"' in env_source, f"missing reward term declaration: {term}", failures)

    for term in required_termination_terms:
        require(f'"{term}"' in env_source, f"missing termination term declaration: {term}", failures)

    for marker in REQUIRED_CODE_MARKERS:
        require(marker in combined_source, f"missing required code marker: {marker}", failures)

    require("func=mdp.root_height_below_minimum" not in env_source, "uses flat-terrain root height reset", failures)

    for context_file in (
        "context/search_scope.yaml",
        "constraints/reward_contract.yaml",
        "constraints/termination_contract.yaml",
        "entropy/entropy_budget.yaml",
        "feedback/feedback_loop.yaml",
    ):
        require((HARNESS_DIR / context_file).is_file(), f"missing harness contract file: {context_file}", failures)

    if failures:
        print("harness contracts failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("harness contracts ok")
    print(f"project_root={PROJECT_ROOT}")
    print(f"phase_dir={PHASE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
