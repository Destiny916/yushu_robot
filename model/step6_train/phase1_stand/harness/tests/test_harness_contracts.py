"""Contract tests for the Phase 1 standing harness."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import unittest
import importlib.util


HARNESS_DIR = Path(__file__).resolve().parents[1]
PHASE_DIR = HARNESS_DIR.parent
PROJECT_ROOT = PHASE_DIR.parents[2]
ISAACLAB_SCRIPTS_ROOT = PROJECT_ROOT.parent


def load_checker_module():
    checker_path = HARNESS_DIR / "scripts" / "check_harness_contracts.py"
    spec = importlib.util.spec_from_file_location("check_harness_contracts", checker_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Phase1StandHarnessTests(unittest.TestCase):
    def test_harness_structure_exists(self):
        expected_files = (
            "README.md",
            "context/project_context.yaml",
            "context/search_scope.yaml",
            "context/phase1_stand_context.yaml",
            "context/isaacsim_reference_roots.yaml",
            "constraints/architecture_constraints.yaml",
            "constraints/reward_contract.yaml",
            "constraints/termination_contract.yaml",
            "constraints/training_contract.yaml",
            "constraints/future_extension_space.yaml",
            "feedback/feedback_loop.yaml",
            "feedback/run_review_template.md",
            "feedback/failure_triage.md",
            "feedback/metric_expectations.yaml",
            "entropy/entropy_budget.yaml",
            "entropy/randomness_policy.yaml",
            "entropy/run_lineage_template.yaml",
            "scripts/check_harness_contracts.py",
            "scripts/collect_context.py",
            "scripts/search_reference_examples.py",
            "scripts/summarize_run.py",
        )
        for relative_path in expected_files:
            self.assertTrue((HARNESS_DIR / relative_path).is_file(), relative_path)

    def test_search_scope_allows_project_and_isaaclab_examples(self):
        search_scope = (HARNESS_DIR / "context" / "search_scope.yaml").read_text(encoding="utf-8")

        self.assertIn("yushu_robot", search_scope)
        self.assertIn("phase1_stand", search_scope)
        self.assertIn("D:/il/IsaacLab/scripts/demos", search_scope)
        self.assertIn("D:/il/IsaacLab/scripts/tutorials", search_scope)
        self.assertIn("D:/il/IsaacLab/scripts/reinforcement_learning", search_scope)
        self.assertIn("D:/il/IsaacLab/source", search_scope)

    def test_constraints_reserve_future_extension_space(self):
        future_space = (HARNESS_DIR / "constraints" / "future_extension_space.yaml").read_text(encoding="utf-8")

        self.assertIn("phase1_walk", future_space)
        self.assertIn("phase2_dagger", future_space)
        self.assertIn("phase3_pcgrad", future_space)
        self.assertIn("common", future_space)

    def test_harness_update_requires_user_confirmation_rule(self):
        architecture_constraints = (HARNESS_DIR / "constraints" / "architecture_constraints.yaml").read_text(
            encoding="utf-8"
        )
        readme = (HARNESS_DIR / "README.md").read_text(encoding="utf-8")
        combined = architecture_constraints + "\n" + readme

        self.assertIn("phase1_stand change requires harness review", combined)
        self.assertIn("confirm before writing harness changes", combined)
        self.assertIn("user confirmation", combined)

    def test_phase1_stand_conversation_requires_harness_read_rule(self):
        architecture_constraints = (HARNESS_DIR / "constraints" / "architecture_constraints.yaml").read_text(
            encoding="utf-8"
        )
        readme = (HARNESS_DIR / "README.md").read_text(encoding="utf-8")
        combined = architecture_constraints + "\n" + readme

        self.assertIn("phase1_stand conversation requires harness read", combined)
        self.assertIn("harness/README.md", combined)
        self.assertIn("constraints/reward_contract.yaml", combined)
        self.assertIn("constraints/termination_contract.yaml", combined)

    def test_phase1_stand_changes_require_readme_update_rule(self):
        architecture_constraints = (HARNESS_DIR / "constraints" / "architecture_constraints.yaml").read_text(
            encoding="utf-8"
        )
        readme = (HARNESS_DIR / "README.md").read_text(encoding="utf-8")
        combined = architecture_constraints + "\n" + readme

        self.assertIn("must update the relevant README", combined)
        self.assertIn("commands", combined)
        self.assertIn("harness rules", combined)

    def test_contract_checker_covers_every_reward_contract_term(self):
        checker = load_checker_module()
        reward_terms = checker.load_simple_yaml_list(
            HARNESS_DIR / "constraints" / "reward_contract.yaml",
            "required_reward_terms",
        )
        env_source = (PHASE_DIR / "stand_env_cfg.py").read_text(encoding="utf-8")

        self.assertGreaterEqual(len(reward_terms), 24)
        for term in reward_terms:
            self.assertIn(f'"{term}"', env_source, term)

    def test_contract_checker_validates_current_phase1_stand(self):
        checker = HARNESS_DIR / "scripts" / "check_harness_contracts.py"

        result = subprocess.run(
            [sys.executable, "-B", str(checker)],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("harness contracts ok", result.stdout)

    def test_reference_search_is_limited_to_declared_roots(self):
        searcher = HARNESS_DIR / "scripts" / "search_reference_examples.py"

        result = subprocess.run(
            [sys.executable, "-B", str(searcher), "TerrainImporterCfg", "--max-results", "3"],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("search roots:", result.stdout)
        self.assertNotIn(".git", result.stdout)


if __name__ == "__main__":
    unittest.main()
