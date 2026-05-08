"""Tests for the Phase 1 standing PPO training entry point."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
import sys
import unittest


PHASE1_STAND_DIR = Path(__file__).resolve().parent
if str(PHASE1_STAND_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE1_STAND_DIR))


class StandPpoTrainingTests(unittest.TestCase):
    def load_module(self, name: str):
        """Import a Phase 1 stand module with a clear assertion failure."""
        if importlib.util.find_spec(name) is None:
            self.fail(f"{name} module should exist for Phase 1 standing PPO training")
        return importlib.import_module(name)

    def test_ppo_runner_config_matches_phase1_stand_plan(self):
        stand_ppo_cfg = self.load_module("stand_ppo_cfg")

        cfg = stand_ppo_cfg.create_g1_stand_ppo_runner_cfg()
        self.assertEqual("g1_stand", cfg.experiment_name)
        self.assertEqual("OnPolicyRunner", cfg.class_name)
        self.assertEqual(24, cfg.num_steps_per_env)
        self.assertEqual(1500, cfg.max_iterations)
        self.assertEqual(50, cfg.save_interval)
        self.assertEqual([512, 256, 128], cfg.policy.actor_hidden_dims)
        self.assertEqual([512, 256, 128], cfg.policy.critic_hidden_dims)
        self.assertEqual("elu", cfg.policy.activation)

    def test_resume_cli_values_update_runner_config(self):
        stand_ppo_cfg = self.load_module("stand_ppo_cfg")

        cfg = stand_ppo_cfg.create_g1_stand_ppo_runner_cfg(
            resume=True,
            load_run="2026-05-08_15-30-00",
            checkpoint="model_100.pt",
            max_iterations=25,
            save_interval=5,
        )
        self.assertTrue(cfg.resume)
        self.assertEqual("2026-05-08_15-30-00", cfg.load_run)
        self.assertEqual("model_100.pt", cfg.load_checkpoint)
        self.assertEqual(25, cfg.max_iterations)
        self.assertEqual(5, cfg.save_interval)

    def test_training_entry_exports_resume_and_checkpoint_contract(self):
        train_stand = self.load_module("train_stand")

        self.assertEqual(Path("logs") / "rsl_rl" / "g1_stand", train_stand.DEFAULT_LOG_ROOT)
        self.assertEqual("model_*.pt", train_stand.DEFAULT_LOAD_CHECKPOINT)
        self.assertEqual("checkpoint_stand.pt", train_stand.FINAL_CHECKPOINT_ALIAS)
        self.assertTrue(callable(train_stand.resolve_resume_checkpoint))
        self.assertTrue(callable(train_stand.preload_rsl_rl))

    def test_latest_checkpoint_alias_points_to_newest_model_file(self):
        train_stand = self.load_module("train_stand")

        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir)
            older = log_dir / "model_1.pt"
            newer = log_dir / "model_10.pt"
            older.write_text("old", encoding="utf-8")
            newer.write_text("new", encoding="utf-8")

            alias = train_stand.copy_latest_checkpoint_alias(log_dir)

            self.assertEqual(log_dir / "checkpoint_stand.pt", alias)
            self.assertEqual("new", alias.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
