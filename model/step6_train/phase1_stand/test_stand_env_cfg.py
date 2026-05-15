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
        self.assertEqual("soft", stand_env_cfg.ACTION_TARGET_LIMIT_KIND)
        self.assertEqual(0.005, stand_env_cfg.ACTION_TARGET_LIMIT_MARGIN)
        self.assertEqual(0.005, stand_env_cfg.JOINT_POS_LIMIT_TOLERANCE)
        self.assertEqual(
            ("base_ang_vel", "projected_gravity", "joint_pos_rel", "joint_vel_rel", "last_action"),
            stand_env_cfg.POLICY_OBSERVATION_TERMS,
        )

    def test_factory_is_available(self):
        stand_env_cfg = self.load_module()

        self.assertTrue(callable(stand_env_cfg.create_g1_stand_no_external_force_env_cfg))

    def test_rl_training_terms_are_declared(self):
        stand_env_cfg = self.load_module()

        self.assertEqual(60.0, stand_env_cfg.EPISODE_LENGTH_S)
        self.assertEqual(5.0, stand_env_cfg.ALIVE_REWARD_WEIGHT)
        self.assertEqual(-1.5, stand_env_cfg.ANG_VEL_XY_WEIGHT)
        self.assertEqual(-5.0e-3, stand_env_cfg.JOINT_VEL_L2_WEIGHT)
        self.assertEqual(-0.05, stand_env_cfg.ACTION_RATE_L2_WEIGHT)
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
                "joint_pos_hard_limits_l1",
                "joint_vel_usd_limits_l1",
                "feet_slide",
                "feet_contact_presence",
                "feet_contact_balance",
                "arm_swing_l2",
                "arm_swing_asymmetry_l2",
                "joint_acc_l2",
                "action_rate_l2",
                "joint_deviation_waist",
                "joint_deviation_shoulders",
                "joint_deviation_arms",
                "joint_symmetry_arms",
                "termination_penalty",
                "joint_limit_violation_penalty",
                "collapse_ground_contact_penalty",
            ),
            stand_env_cfg.REWARD_TERMS,
        )
        self.assertEqual(
            (
                "time_out",
                "root_height_below_minimum",
                "joint_pos_out_of_limit",
                "joint_vel_out_of_limit",
                "collapse_ground_contact",
            ),
            stand_env_cfg.TERMINATION_TERMS,
        )

    def test_training_resets_on_full_fall_timeout_or_hard_joint_limits(self):
        stand_env_cfg = self.load_module()

        self.assertEqual(0.45, stand_env_cfg.FALLEN_ROOT_HEIGHT_THRESHOLD)
        source = Path(stand_env_cfg.__file__).read_text(encoding="utf-8")
        self.assertIn("self.episode_length_s = EPISODE_LENGTH_S", source)
        self.assertIn('"minimum_height": FALLEN_ROOT_HEIGHT_THRESHOLD', source)
        self.assertIn("root_height_below_minimum_fn", source)
        self.assertNotIn("func=mdp.root_height_below_minimum", source)
        self.assertNotIn("bad_orientation = DoneTerm", source)
        self.assertIn("joint_pos_out_of_limit = DoneTerm", source)
        self.assertIn('"tolerance": JOINT_POS_LIMIT_TOLERANCE', source)
        self.assertIn("joint_vel_out_of_limit = DoneTerm", source)
        self.assertIn("collapse_ground_contact = DoneTerm", source)

    def test_standing_penalties_are_strong_enough_to_avoid_joint_limit_deaths(self):
        stand_env_cfg = self.load_module()

        self.assertEqual(-12.0, stand_env_cfg.JOINT_POS_SOFT_LIMIT_WEIGHT)
        self.assertEqual(-50.0, stand_env_cfg.JOINT_POS_HARD_LIMIT_WEIGHT)
        self.assertEqual(-8.0, stand_env_cfg.JOINT_VEL_USD_LIMIT_WEIGHT)
        self.assertEqual(-200.0, stand_env_cfg.TERMINATION_PENALTY_WEIGHT)
        self.assertEqual(-500.0, stand_env_cfg.JOINT_LIMIT_TERMINATION_PENALTY_WEIGHT)
        self.assertEqual(3, stand_env_cfg.COLLAPSE_GROUND_CONTACT_MIN_LIMBS)
        self.assertEqual(-500.0, stand_env_cfg.COLLAPSE_GROUND_CONTACT_PENALTY_WEIGHT)

        source = Path(stand_env_cfg.__file__).read_text(encoding="utf-8")
        self.assertIn("is_alive = RewTerm(func=mdp.is_alive, weight=ALIVE_REWARD_WEIGHT)", source)
        self.assertIn("ang_vel_xy_l2 = RewTerm(func=mdp.ang_vel_xy_l2, weight=ANG_VEL_XY_WEIGHT)", source)
        self.assertIn("joint_vel_l2 = RewTerm(func=mdp.joint_vel_l2, weight=JOINT_VEL_L2_WEIGHT)", source)
        self.assertIn("action_rate_l2 = RewTerm(func=mdp.action_rate_l2, weight=ACTION_RATE_L2_WEIGHT)", source)
        self.assertIn("ClampedJointPositionActionCfg", source)
        self.assertIn("scale=ACTION_SCALE", source)
        self.assertIn("limit_kind=ACTION_TARGET_LIMIT_KIND", source)
        self.assertIn("limit_margin=ACTION_TARGET_LIMIT_MARGIN", source)
        self.assertIn("weight=JOINT_POS_SOFT_LIMIT_WEIGHT", source)
        self.assertIn("weight=JOINT_POS_HARD_LIMIT_WEIGHT", source)
        self.assertIn("weight=JOINT_VEL_USD_LIMIT_WEIGHT", source)
        self.assertIn("weight=TERMINATION_PENALTY_WEIGHT", source)
        self.assertIn("weight=JOINT_LIMIT_TERMINATION_PENALTY_WEIGHT", source)
        self.assertIn("root_height_below_minimum_event_fn", source)
        self.assertIn('"minimum_height": FALLEN_ROOT_HEIGHT_THRESHOLD', source)
        self.assertIn("joint_pos_hard_limits_l1_fn", source)
        self.assertIn("joint_limit_violation_event_fn", source)
        self.assertIn("joint_vel_out_of_limit_fn", source)
        self.assertIn("joint_vel_usd_limits_l1_fn", source)
        self.assertIn("collapse_ground_contact_event_fn", source)
        self.assertIn("weight=COLLAPSE_GROUND_CONTACT_PENALTY_WEIGHT", source)

    def test_phase1_standing_uses_contact_sensor_rewards(self):
        stand_env_cfg = self.load_module()

        self.assertEqual("contact_forces", stand_env_cfg.CONTACT_SENSOR_NAME)
        self.assertEqual(
            "{ENV_REGEX_NS}/Robot/.*(ankle_roll_link|knee_link|elbow_link|wrist_yaw_link|rubber_hand)",
            stand_env_cfg.CONTACT_SENSOR_PRIM_PATH,
        )
        self.assertEqual(6, stand_env_cfg.CONTACT_SENSOR_HISTORY_LENGTH)
        self.assertEqual(-0.5, stand_env_cfg.FEET_SLIDE_WEIGHT)
        self.assertEqual(-1.0, stand_env_cfg.FEET_CONTACT_PRESENCE_WEIGHT)
        self.assertEqual(-0.5, stand_env_cfg.FEET_CONTACT_BALANCE_WEIGHT)
        self.assertEqual(("left_ankle_roll_link", "left_knee_link"), stand_env_cfg.COLLAPSE_LEFT_LEG_BODY_NAMES)
        self.assertEqual(("right_ankle_roll_link", "right_knee_link"), stand_env_cfg.COLLAPSE_RIGHT_LEG_BODY_NAMES)
        self.assertEqual(
            ("left_elbow_link", "left_wrist_yaw_link", "left_rubber_hand"),
            stand_env_cfg.COLLAPSE_LEFT_ARM_BODY_NAMES,
        )
        self.assertEqual(
            ("right_elbow_link", "right_wrist_yaw_link", "right_rubber_hand"),
            stand_env_cfg.COLLAPSE_RIGHT_ARM_BODY_NAMES,
        )

        source = Path(stand_env_cfg.__file__).read_text(encoding="utf-8")
        self.assertIn("ContactSensorCfg", source)
        self.assertIn("activate_contact_sensors = True", source)
        self.assertIn("feet_slide_fn", source)
        self.assertIn("feet_contact_presence_fn", source)
        self.assertIn("feet_contact_balance_fn", source)
        self.assertIn("COLLAPSE_LEFT_LEG_BODY_NAMES", source)

    def test_natural_posture_rewards_do_not_constrain_hips_knees_or_ankles(self):
        stand_env_cfg = self.load_module()

        self.assertEqual(-0.2, stand_env_cfg.JOINT_DEVIATION_WAIST_WEIGHT)
        self.assertEqual(-1.0, stand_env_cfg.JOINT_DEVIATION_ARMS_WEIGHT)
        self.assertEqual(-2.0, stand_env_cfg.JOINT_DEVIATION_SHOULDERS_WEIGHT)
        self.assertEqual(-3.0, stand_env_cfg.ARM_SWING_L2_WEIGHT)
        self.assertEqual(-0.2, stand_env_cfg.JOINT_SYMMETRY_ARMS_WEIGHT)
        self.assertEqual(("waist_.*_joint",), stand_env_cfg.NATURAL_POSTURE_WAIST_JOINTS)
        self.assertEqual(
            (
                ".*_shoulder_pitch_joint",
                ".*_shoulder_roll_joint",
                ".*_shoulder_yaw_joint",
            ),
            stand_env_cfg.SHOULDER_POSTURE_JOINTS,
        )
        self.assertEqual(
            (
                ".*_shoulder_pitch_joint",
                ".*_shoulder_roll_joint",
                ".*_shoulder_yaw_joint",
                ".*_elbow_joint",
                ".*_wrist_.*_joint",
            ),
            stand_env_cfg.NATURAL_POSTURE_ARM_JOINTS,
        )

        configured_joint_patterns = (
            *stand_env_cfg.NATURAL_POSTURE_WAIST_JOINTS,
            *stand_env_cfg.SHOULDER_POSTURE_JOINTS,
            *stand_env_cfg.NATURAL_POSTURE_ARM_JOINTS,
        )
        for excluded_pattern in ("hip", "knee", "ankle"):
            self.assertFalse(any(excluded_pattern in pattern for pattern in configured_joint_patterns))

        source = Path(stand_env_cfg.__file__).read_text(encoding="utf-8")
        self.assertIn("joint_deviation_waist", source)
        self.assertIn("joint_deviation_shoulders", source)
        self.assertIn("joint_deviation_arms", source)
        self.assertIn("joint_symmetry_arms", source)
        self.assertIn("joint_deviation_symmetry_l1_fn", source)
        self.assertIn("weight=JOINT_DEVIATION_SHOULDERS_WEIGHT", source)
        self.assertIn("weight=ARM_SWING_L2_WEIGHT", source)


if __name__ == "__main__":
    unittest.main()
