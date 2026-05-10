"""Tests for the Phase 1 no-external-force standing environment config."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
import sys
import unittest


PHASE1_STAND_DIR = Path(__file__).resolve().parent
if str(PHASE1_STAND_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE1_STAND_DIR))


class StandEnvCfgTests(unittest.TestCase):
    def load_module(self):
        """Import the environment config module with a clear assertion failure."""
        if importlib.util.find_spec("stand_env_cfg") is None:
            self.fail("stand_env_cfg module should exist for Phase 1 standing environment config")
        return importlib.import_module("stand_env_cfg")

    def test_defaults_match_no_external_force_standing_env(self):
        stand_env_cfg = self.load_module()

        self.assertEqual(1, stand_env_cfg.DEFAULT_NUM_ENVS)
        self.assertEqual(0, stand_env_cfg.DEFAULT_MAX_STEPS)
        self.assertEqual(4.0, stand_env_cfg.DEFAULT_ENV_SPACING)
        self.assertEqual("T0", stand_env_cfg.DEFAULT_TERRAIN)
        self.assertEqual("{ENV_REGEX_NS}/Robot", stand_env_cfg.ROBOT_PRIM_PATH)

    def test_multi_env_training_uses_grid_origins(self):
        stand_env_cfg = self.load_module()

        self.assertFalse(stand_env_cfg.USE_TERRAIN_ORIGINS)
        source = Path(stand_env_cfg.__file__).read_text(encoding="utf-8")
        self.assertIn("use_terrain_origins=USE_TERRAIN_ORIGINS", source)

    def test_standing_terrain_uses_high_foot_contact_friction(self):
        stand_env_cfg = self.load_module()

        self.assertEqual(2.0, stand_env_cfg.STANDING_STATIC_FRICTION)
        self.assertEqual(2.0, stand_env_cfg.STANDING_DYNAMIC_FRICTION)

        source = Path(stand_env_cfg.__file__).read_text(encoding="utf-8")
        self.assertIn("static_friction=STANDING_STATIC_FRICTION", source)
        self.assertIn("dynamic_friction=STANDING_DYNAMIC_FRICTION", source)

    def test_no_external_force_events_are_declared(self):
        stand_env_cfg = self.load_module()

        self.assertEqual((), stand_env_cfg.EXTERNAL_FORCE_EVENT_TERMS)
        self.assertEqual(("reset_base", "reset_joints"), stand_env_cfg.RESET_EVENT_TERMS)

    def test_observation_and_action_contract_stays_step4_compatible(self):
        stand_env_cfg = self.load_module()

        self.assertEqual("joint_pos", stand_env_cfg.ACTION_TERM_NAME)
        self.assertEqual(0.10, stand_env_cfg.ACTION_SCALE)
        self.assertEqual(
            ("base_ang_vel", "projected_gravity", "joint_pos_rel", "joint_vel_rel", "last_action"),
            stand_env_cfg.POLICY_OBSERVATION_TERMS,
        )

    def test_factory_is_available(self):
        stand_env_cfg = self.load_module()

        self.assertTrue(callable(stand_env_cfg.create_g1_stand_no_external_force_env_cfg))

    def test_rl_training_terms_are_declared(self):
        stand_env_cfg = self.load_module()

        self.assertEqual(300.0, stand_env_cfg.EPISODE_LENGTH_S)
        self.assertEqual(
            (
                "is_alive",
                "flat_orientation_l2",
                "base_height_l2",
                "lin_vel_xy_l2",
                "ang_vel_xy_l2",
                "joint_torques_l2",
                "joint_vel_l2",
                "joint_pos_soft_limits_l2",
                "joint_vel_usd_limits_l1",
                "arm_swing_l2",
                "arm_swing_asymmetry_l2",
                "joint_acc_l2",
                "action_rate_l2",
                "joint_deviation_l1",
                "termination_penalty",
            ),
            stand_env_cfg.REWARD_TERMS,
        )
        self.assertEqual(
            ("time_out", "bad_orientation", "root_height_below_minimum", "joint_pos_out_of_limit"),
            stand_env_cfg.TERMINATION_TERMS,
        )

    def test_standing_penalties_are_strong_enough_to_avoid_joint_limit_deaths(self):
        stand_env_cfg = self.load_module()

        self.assertEqual(-12.0, stand_env_cfg.JOINT_POS_SOFT_LIMIT_WEIGHT)
        self.assertEqual(-8.0, stand_env_cfg.JOINT_VEL_USD_LIMIT_WEIGHT)
        self.assertEqual(-200.0, stand_env_cfg.TERMINATION_PENALTY_WEIGHT)

        source = Path(stand_env_cfg.__file__).read_text(encoding="utf-8")
        self.assertIn("scale=ACTION_SCALE", source)
        self.assertIn("weight=JOINT_POS_SOFT_LIMIT_WEIGHT", source)
        self.assertIn("weight=JOINT_VEL_USD_LIMIT_WEIGHT", source)
        self.assertIn("weight=TERMINATION_PENALTY_WEIGHT", source)
        self.assertIn("joint_pos_out_of_limit_fn", source)
        self.assertIn("joint_vel_usd_limits_l1_fn", source)


if __name__ == "__main__":
    unittest.main()
