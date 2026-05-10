"""Tests for the Phase 1 standing policy playback entry point."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest


PHASE1_STAND_DIR = Path(__file__).resolve().parent
if str(PHASE1_STAND_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE1_STAND_DIR))


class StandPolicyPlaybackTests(unittest.TestCase):
    def load_module(self):
        """Import the playback module with a clear assertion failure."""
        if importlib.util.find_spec("play_stand") is None:
            self.fail("play_stand module should exist for Phase 1 standing policy playback")
        return importlib.import_module("play_stand")

    def test_playback_entry_exports_checkpoint_contract(self):
        play_stand = self.load_module()

        self.assertEqual(Path("logs") / "rsl_rl" / "g1_stand", play_stand.DEFAULT_LOG_ROOT)
        self.assertEqual("checkpoint_stand.pt", play_stand.DEFAULT_PLAY_CHECKPOINT)
        self.assertEqual("model_*.pt", play_stand.DEFAULT_FALLBACK_CHECKPOINT)
        self.assertEqual("error", play_stand.PLAYBACK_ERROR_MESSAGE)
        self.assertTrue(callable(play_stand.resolve_play_checkpoint))
        self.assertTrue(callable(play_stand.preload_rsl_rl))
        self.assertTrue(callable(play_stand.is_policy_error))

    def test_policy_error_is_reported_when_any_env_is_done(self):
        play_stand = self.load_module()

        self.assertFalse(play_stand.is_policy_error(0))
        self.assertTrue(play_stand.is_policy_error(1))
        self.assertTrue(play_stand.is_policy_error(2))

    def test_resolve_checkpoint_prefers_run_alias(self):
        play_stand = self.load_module()

        with TemporaryDirectory() as temp_dir:
            log_root = Path(temp_dir)
            run_dir = log_root / "2026-05-09_13-40-12_T0_stand_stable"
            run_dir.mkdir()
            alias = run_dir / "checkpoint_stand.pt"
            alias.write_text("alias", encoding="utf-8")

            resolved = play_stand.resolve_play_checkpoint(
                log_root,
                "2026-05-09_13-40-12_T0_stand_stable",
                "checkpoint_stand.pt",
            )

            self.assertEqual(alias, resolved)

    def test_resolve_checkpoint_can_select_latest_model_glob(self):
        play_stand = self.load_module()

        with TemporaryDirectory() as temp_dir:
            log_root = Path(temp_dir)
            run_dir = log_root / "run"
            run_dir.mkdir()
            (run_dir / "model_25.pt").write_text("old", encoding="utf-8")
            latest = run_dir / "model_100.pt"
            latest.write_text("latest", encoding="utf-8")

            resolved = play_stand.resolve_play_checkpoint(log_root, "run", "model_*.pt")

            self.assertEqual(latest, resolved)


if __name__ == "__main__":
    unittest.main()
