"""Tests for the Phase 1 standing reward helpers."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
import unittest

import torch


PHASE1_STAND_DIR = Path(__file__).resolve().parent
if str(PHASE1_STAND_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE1_STAND_DIR))


class FakeSceneEntityCfg:
    def __init__(self, name: str, joint_names=None, body_names=None, preserve_order: bool = False):
        self.name = name
        self.joint_names = joint_names
        self.body_names = body_names
        self.preserve_order = preserve_order
        self.joint_ids = slice(None)
        self.body_ids = slice(None)


def install_isaaclab_manager_stub() -> None:
    isaaclab_module = sys.modules.setdefault("isaaclab", ModuleType("isaaclab"))
    managers_module = ModuleType("isaaclab.managers")
    managers_module.SceneEntityCfg = FakeSceneEntityCfg
    isaaclab_module.managers = managers_module
    sys.modules["isaaclab.managers"] = managers_module


class StandRewardTests(unittest.TestCase):
    def load_module(self):
        """Import the reward helpers with a clear assertion failure."""
        install_isaaclab_manager_stub()
        if importlib.util.find_spec("stand_rewards") is None:
            self.fail("stand_rewards module should exist for Phase 1 standing reward helpers")
        return importlib.import_module("stand_rewards")

    def test_arm_swing_cfgs_cover_shoulders_elbows_and_wrists(self):
        stand_rewards = self.load_module()

        self.assertEqual(
            [
                "left_shoulder_pitch_joint",
                "left_shoulder_roll_joint",
                "left_shoulder_yaw_joint",
                "left_elbow_joint",
                "left_wrist_roll_joint",
                "left_wrist_pitch_joint",
                "left_wrist_yaw_joint",
            ],
            stand_rewards.LEFT_ARM_SWING_JOINT_NAMES,
        )
        self.assertEqual(
            [
                "right_shoulder_pitch_joint",
                "right_shoulder_roll_joint",
                "right_shoulder_yaw_joint",
                "right_elbow_joint",
                "right_wrist_roll_joint",
                "right_wrist_pitch_joint",
                "right_wrist_yaw_joint",
            ],
            stand_rewards.RIGHT_ARM_SWING_JOINT_NAMES,
        )

    def test_standing_time_reward_keeps_first_30_seconds_at_base_rate_then_increases(self):
        stand_rewards = self.load_module()

        class FakeTerminationManager:
            def __init__(self):
                self.terminated = torch.tensor([False, False, False, False, False, True])

        class FakeEnv:
            def __init__(self):
                self.step_dt = 0.02
                self.episode_length_buf = torch.tensor([0, 750, 1500, 2250, 3000, 3000])
                self.termination_manager = FakeTerminationManager()

        reward = stand_rewards.standing_time_reward(
            FakeEnv(),
            ramp_start_s=30.0,
            ramp_end_s=60.0,
            max_multiplier=2.0,
        )

        expected = torch.tensor([1.0, 1.0, 1.0, 1.5, 2.0, 0.0])
        torch.testing.assert_close(reward, expected)

    def test_standing_time_reward_keeps_zero_to_30_second_total_at_150_with_weight_5(self):
        stand_rewards = self.load_module()

        class FakeTerminationManager:
            def __init__(self, num_steps: int):
                self.terminated = torch.zeros(num_steps, dtype=torch.bool)

        class FakeEnv:
            def __init__(self, num_steps: int):
                self.step_dt = 0.02
                self.episode_length_buf = torch.arange(num_steps)
                self.termination_manager = FakeTerminationManager(num_steps)

        num_steps_30s = 1500
        reward_signal = stand_rewards.standing_time_reward(
            FakeEnv(num_steps_30s),
            ramp_start_s=30.0,
            ramp_end_s=60.0,
            max_multiplier=2.0,
        )

        total_reward = torch.sum(reward_signal * 5.0 * 0.02)
        self.assertAlmostEqual(150.0, total_reward.item(), places=5)

    def test_joint_pos_soft_limits_use_usd_joint_limits_not_default_pose(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.joint_pos = torch.tensor([[0.9]], dtype=torch.float32)
                self.default_joint_pos = torch.tensor([[0.9]], dtype=torch.float32)
                self.joint_pos_limits = torch.tensor([[[-1.0, 1.0]]], dtype=torch.float32)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        penalty = stand_rewards.joint_pos_soft_limits_l2(FakeEnv(), asset_cfg=FakeSceneEntityCfg("robot"))

        self.assertGreater(penalty.item(), 0.0)

    def test_joint_pos_soft_limits_can_stay_zero_inside_usd_joint_limits(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.joint_pos = torch.tensor([[0.0]], dtype=torch.float32)
                self.default_joint_pos = torch.tensor([[0.9]], dtype=torch.float32)
                self.joint_pos_limits = torch.tensor([[[-1.0, 1.0]]], dtype=torch.float32)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        penalty = stand_rewards.joint_pos_soft_limits_l2(FakeEnv(), asset_cfg=FakeSceneEntityCfg("robot"))

        self.assertAlmostEqual(0.0, penalty.item(), places=6)

    def test_joint_pos_out_of_limit_checks_usd_joint_limits(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.joint_pos = torch.tensor([[1.1]], dtype=torch.float32)
                self.joint_pos_limits = torch.tensor([[[-1.0, 1.0]]], dtype=torch.float32)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        is_out_of_limit = stand_rewards.joint_pos_out_of_limit(FakeEnv(), asset_cfg=FakeSceneEntityCfg("robot"))

        self.assertTrue(is_out_of_limit.item())

    def test_joint_pos_out_of_limit_stays_false_inside_usd_joint_limits(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.joint_pos = torch.tensor([[0.9]], dtype=torch.float32)
                self.joint_pos_limits = torch.tensor([[[-1.0, 1.0]]], dtype=torch.float32)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        is_out_of_limit = stand_rewards.joint_pos_out_of_limit(FakeEnv(), asset_cfg=FakeSceneEntityCfg("robot"))

        self.assertFalse(is_out_of_limit.item())

    def test_joint_pos_out_of_limit_ignores_small_solver_tolerance_overshoot(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.joint_pos = torch.tensor([[1.002]], dtype=torch.float32)
                self.joint_pos_limits = torch.tensor([[[-1.0, 1.0]]], dtype=torch.float32)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        is_out_of_limit = stand_rewards.joint_pos_out_of_limit(
            FakeEnv(), asset_cfg=FakeSceneEntityCfg("robot"), tolerance=0.005
        )

        self.assertFalse(is_out_of_limit.item())

    def test_joint_vel_out_of_limit_checks_usd_velocity_limits(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.joint_vel = torch.tensor([[9.0, -10.5, 11.0]], dtype=torch.float32)
                self.joint_vel_limits = torch.tensor([[10.0, 10.0, 10.0]], dtype=torch.float32)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        is_out_of_limit = stand_rewards.joint_vel_out_of_limit(FakeEnv(), asset_cfg=FakeSceneEntityCfg("robot"))

        self.assertTrue(is_out_of_limit.item())

    def test_joint_limit_violation_detects_position_or_velocity_hard_limit(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.joint_pos = torch.tensor([[0.0], [1.2], [0.0]], dtype=torch.float32)
                self.joint_pos_limits = torch.tensor([[[-1.0, 1.0]], [[-1.0, 1.0]], [[-1.0, 1.0]]])
                self.joint_vel = torch.tensor([[5.0], [5.0], [11.0]], dtype=torch.float32)
                self.joint_vel_limits = torch.tensor([[10.0], [10.0], [10.0]], dtype=torch.float32)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        is_violated = stand_rewards.joint_limit_violation(FakeEnv(), asset_cfg=FakeSceneEntityCfg("robot"))

        self.assertEqual([False, True, True], is_violated.tolist())

    def test_joint_limit_violation_event_counteracts_reward_manager_dt_scaling(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.joint_pos = torch.tensor([[0.0], [1.2], [0.0]], dtype=torch.float32)
                self.joint_pos_limits = torch.tensor([[[-1.0, 1.0]], [[-1.0, 1.0]], [[-1.0, 1.0]]])
                self.joint_vel = torch.tensor([[5.0], [5.0], [11.0]], dtype=torch.float32)
                self.joint_vel_limits = torch.tensor([[10.0], [10.0], [10.0]], dtype=torch.float32)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}
                self.step_dt = 0.02

        penalty_signal = stand_rewards.joint_limit_violation_event(
            FakeEnv(), asset_cfg=FakeSceneEntityCfg("robot")
        )

        self.assertEqual([0.0, 50.0, 50.0], penalty_signal.tolist())

    def test_root_height_below_minimum_event_counteracts_reward_manager_dt_scaling(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.root_pos_w = torch.tensor([[0.0, 0.0, 0.30], [0.0, 0.0, 0.20]], dtype=torch.float32)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}
                self.step_dt = 0.02

        penalty_signal = stand_rewards.root_height_below_minimum_event(
            FakeEnv(), minimum_height=0.25, asset_cfg=FakeSceneEntityCfg("robot")
        )

        self.assertEqual([0.0, 50.0], penalty_signal.tolist())

    def test_joint_pos_hard_limits_l1_penalizes_only_usd_limit_excess(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.joint_pos = torch.tensor([[-1.2, -0.5, 0.8, 1.4]], dtype=torch.float32)
                self.joint_pos_limits = torch.tensor(
                    [[[-1.0, 1.0], [-1.0, 1.0], [-1.0, 1.0], [-1.0, 1.0]]], dtype=torch.float32
                )

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        penalty = stand_rewards.joint_pos_hard_limits_l1(FakeEnv(), asset_cfg=FakeSceneEntityCfg("robot"))

        self.assertAlmostEqual(0.6, penalty.item(), places=6)

    def test_joint_vel_usd_limits_l1_stays_zero_below_30_percent_of_usd_limit(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.joint_vel = torch.tensor([[2.0]], dtype=torch.float32)
                self.joint_vel_limits = torch.tensor([[10.0]], dtype=torch.float32)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        penalty = stand_rewards.joint_vel_usd_limits_l1(FakeEnv(), asset_cfg=FakeSceneEntityCfg("robot"))

        self.assertAlmostEqual(0.0, penalty.item(), places=6)

    def test_joint_vel_usd_limits_l1_uses_linear_excess_above_30_percent_of_usd_limit(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.joint_vel = torch.tensor([[4.5, -5.0]], dtype=torch.float32)
                self.joint_vel_limits = torch.tensor([[10.0, 10.0]], dtype=torch.float32)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        penalty = stand_rewards.joint_vel_usd_limits_l1(FakeEnv(), asset_cfg=FakeSceneEntityCfg("robot"))

        self.assertAlmostEqual(3.5, penalty.item(), places=6)

    def test_root_height_below_minimum_matches_reset_fall_definition(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.root_pos_w = torch.tensor(
                    [
                        [0.0, 0.0, 0.24],
                        [0.0, 0.0, 0.25],
                        [0.0, 0.0, 0.40],
                    ],
                    dtype=torch.float32,
                )

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        is_fallen = stand_rewards.root_height_below_minimum(
            FakeEnv(),
            minimum_height=0.25,
            asset_cfg=FakeSceneEntityCfg("robot"),
        )

        self.assertEqual([True, False, False], is_fallen.tolist())

    def test_root_height_below_minimum_uses_height_relative_to_terrain_origin(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.root_pos_w = torch.tensor(
                    [[0.0, 0.0, 0.84], [0.0, 0.0, 1.00], [0.0, 0.0, 0.46]], dtype=torch.float32
                )

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeScene(dict):
            def __init__(self):
                super().__init__({"robot": FakeAsset()})
                self.env_origins = torch.tensor(
                    [[0.0, 0.0, 0.40], [0.0, 0.0, 0.40], [0.0, 0.0, 0.00]], dtype=torch.float32
                )

        class FakeEnv:
            def __init__(self):
                self.scene = FakeScene()

        is_fallen = stand_rewards.root_height_below_minimum(
            FakeEnv(), minimum_height=0.45, asset_cfg=FakeSceneEntityCfg("robot")
        )

        self.assertEqual([True, False, False], is_fallen.tolist())

    def test_feet_slide_penalizes_planar_foot_velocity_only_when_in_contact(self):
        stand_rewards = self.load_module()

        class FakeContactData:
            def __init__(self):
                self.net_forces_w_history = torch.tensor(
                    [
                        [
                            [[0.0, 0.0, 5.0], [0.0, 0.0, 0.2]],
                            [[0.0, 0.0, 2.0], [0.0, 0.0, 0.1]],
                        ]
                    ],
                    dtype=torch.float32,
                )

        class FakeContactSensor:
            def __init__(self):
                self.data = FakeContactData()

        class FakeAssetData:
            def __init__(self):
                self.body_lin_vel_w = torch.tensor([[[3.0, 4.0, 0.0], [10.0, 0.0, 0.0]]], dtype=torch.float32)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeScene(dict):
            @property
            def sensors(self):
                return self

        class FakeEnv:
            def __init__(self):
                self.scene = FakeScene({"robot": FakeAsset(), "contact_forces": FakeContactSensor()})

        penalty = stand_rewards.feet_slide(
            FakeEnv(),
            sensor_cfg=FakeSceneEntityCfg("contact_forces"),
            asset_cfg=FakeSceneEntityCfg("robot"),
            contact_threshold=1.0,
        )

        self.assertAlmostEqual(5.0, penalty.item(), places=6)

    def test_feet_contact_presence_penalizes_missing_contacts(self):
        stand_rewards = self.load_module()

        class FakeContactData:
            def __init__(self):
                self.net_forces_w_history = torch.tensor(
                    [
                        [[[0.0, 0.0, 5.0], [0.0, 0.0, 4.0]]],
                        [[[0.0, 0.0, 5.0], [0.0, 0.0, 0.1]]],
                        [[[0.0, 0.0, 0.1], [0.0, 0.0, 0.1]]],
                    ],
                    dtype=torch.float32,
                )

        class FakeContactSensor:
            def __init__(self):
                self.data = FakeContactData()

        class FakeScene(dict):
            @property
            def sensors(self):
                return self

        class FakeEnv:
            def __init__(self):
                self.scene = FakeScene({"contact_forces": FakeContactSensor()})

        penalty = stand_rewards.feet_contact_presence(
            FakeEnv(),
            sensor_cfg=FakeSceneEntityCfg("contact_forces"),
            contact_threshold=1.0,
        )

        self.assertEqual([0.0, 1.0, 2.0], penalty.tolist())

    def test_feet_contact_balance_penalizes_left_right_force_imbalance(self):
        stand_rewards = self.load_module()

        class FakeContactData:
            def __init__(self):
                self.net_forces_w_history = torch.tensor(
                    [
                        [[[0.0, 0.0, 6.0], [0.0, 0.0, 2.0]]],
                        [[[0.0, 0.0, 3.0], [0.0, 0.0, 3.0]]],
                    ],
                    dtype=torch.float32,
                )

        class FakeContactSensor:
            def __init__(self):
                self.data = FakeContactData()

        class FakeScene(dict):
            @property
            def sensors(self):
                return self

        class FakeEnv:
            def __init__(self):
                self.scene = FakeScene({"contact_forces": FakeContactSensor()})

        penalty = stand_rewards.feet_contact_balance(
            FakeEnv(),
            sensor_cfg=FakeSceneEntityCfg("contact_forces"),
        )

        self.assertAlmostEqual(0.5, penalty[0].item(), places=6)
        self.assertAlmostEqual(0.0, penalty[1].item(), places=6)

    def test_collapse_ground_contact_requires_at_least_three_limbs(self):
        stand_rewards = self.load_module()

        class FakeContactData:
            def __init__(self):
                forces = torch.zeros((6, 1, 10, 3), dtype=torch.float32)
                forces[0, 0, [0, 1], 2] = 5.0  # feet only
                forces[1, 0, [0, 1, 4], 2] = 5.0  # feet plus left arm only
                forces[2, 0, [0, 1, 8, 9], 2] = 5.0  # feet plus both hands
                forces[3, 0, [2, 3, 4, 5], 2] = 5.0  # knees plus elbows
                forces[4, 0, [0, 5], 2] = 5.0  # incomplete diagonal contact
                forces[5, 0, [0, 1, 5], 2] = 5.0  # both legs plus right arm
                self.net_forces_w_history = forces

        class FakeContactSensor:
            def __init__(self):
                self.data = FakeContactData()

        class FakeScene(dict):
            @property
            def sensors(self):
                return self

        class FakeEnv:
            def __init__(self):
                self.scene = FakeScene({"contact_forces": FakeContactSensor()})

        left_leg_cfg = FakeSceneEntityCfg("contact_forces")
        left_leg_cfg.body_ids = [0, 2]
        right_leg_cfg = FakeSceneEntityCfg("contact_forces")
        right_leg_cfg.body_ids = [1, 3]
        left_arm_cfg = FakeSceneEntityCfg("contact_forces")
        left_arm_cfg.body_ids = [4, 6, 8]
        right_arm_cfg = FakeSceneEntityCfg("contact_forces")
        right_arm_cfg.body_ids = [5, 7, 9]

        is_collapsed = stand_rewards.collapse_ground_contact(
            FakeEnv(),
            left_leg_sensor_cfg=left_leg_cfg,
            right_leg_sensor_cfg=right_leg_cfg,
            left_arm_sensor_cfg=left_arm_cfg,
            right_arm_sensor_cfg=right_arm_cfg,
            contact_threshold=1.0,
            min_contacting_limbs=3,
        )

        self.assertEqual([False, True, True, True, False, True], is_collapsed.tolist())

    def test_collapse_ground_contact_event_counteracts_reward_manager_dt_scaling(self):
        stand_rewards = self.load_module()

        class FakeContactData:
            def __init__(self):
                forces = torch.zeros((3, 1, 4, 3), dtype=torch.float32)
                forces[0, 0, [0, 1, 2, 3], 2] = 5.0
                forces[1, 0, [0, 1], 2] = 5.0
                forces[2, 0, [0, 1, 3], 2] = 5.0
                self.net_forces_w_history = forces

        class FakeContactSensor:
            def __init__(self):
                self.data = FakeContactData()

        class FakeScene(dict):
            @property
            def sensors(self):
                return self

        class FakeEnv:
            def __init__(self):
                self.scene = FakeScene({"contact_forces": FakeContactSensor()})
                self.step_dt = 0.02

        left_leg_cfg = FakeSceneEntityCfg("contact_forces")
        left_leg_cfg.body_ids = [0]
        right_leg_cfg = FakeSceneEntityCfg("contact_forces")
        right_leg_cfg.body_ids = [1]
        left_arm_cfg = FakeSceneEntityCfg("contact_forces")
        left_arm_cfg.body_ids = [2]
        right_arm_cfg = FakeSceneEntityCfg("contact_forces")
        right_arm_cfg.body_ids = [3]

        penalty_signal = stand_rewards.collapse_ground_contact_event(
            FakeEnv(),
            left_leg_sensor_cfg=left_leg_cfg,
            right_leg_sensor_cfg=right_leg_cfg,
            left_arm_sensor_cfg=left_arm_cfg,
            right_arm_sensor_cfg=right_arm_cfg,
            contact_threshold=1.0,
            min_contacting_limbs=3,
        )

        self.assertEqual([50.0, 0.0, 50.0], penalty_signal.tolist())

    def test_joint_deviation_symmetry_uses_deviation_from_default_pose(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.joint_pos = torch.tensor([[0.3, 0.4, 0.5, 0.1]], dtype=torch.float32)
                self.default_joint_pos = torch.tensor([[0.1, 0.2, 0.2, -0.1]], dtype=torch.float32)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        left_cfg = FakeSceneEntityCfg("robot")
        left_cfg.joint_ids = [0, 1]
        right_cfg = FakeSceneEntityCfg("robot")
        right_cfg.joint_ids = [2, 3]

        penalty = stand_rewards.joint_deviation_symmetry_l1(FakeEnv(), left_cfg, right_cfg)

        self.assertAlmostEqual(0.1, penalty.item(), places=6)

    def test_joint_deviation_l2_increases_with_joint_angle_difference(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.joint_pos = torch.tensor([[0.1, 0.3, -0.4], [0.2, 0.6, -0.8]], dtype=torch.float32)
                self.default_joint_pos = torch.zeros_like(self.joint_pos)

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        cfg = FakeSceneEntityCfg("robot")
        cfg.joint_ids = [0, 1, 2]

        penalty = stand_rewards.joint_deviation_l2(FakeEnv(), asset_cfg=cfg)

        torch.testing.assert_close(penalty, torch.tensor([0.26, 1.04]))
        self.assertGreater(penalty[1].item(), penalty[0].item())

    def test_arm_vertical_alignment_l2_penalizes_non_vertical_arms(self):
        stand_rewards = self.load_module()

        class FakeAssetData:
            def __init__(self):
                self.body_pos_w = torch.tensor(
                    [
                        [
                            [0.0, 0.0, 1.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 1.0],
                            [0.0, 0.0, 0.0],
                        ],
                        [
                            [0.0, 0.0, 1.0],
                            [1.0, 0.0, 1.0],
                            [0.0, 0.0, 1.0],
                            [0.0, 1.0, 1.0],
                        ],
                    ],
                    dtype=torch.float32,
                )

        class FakeAsset:
            def __init__(self):
                self.data = FakeAssetData()

        class FakeEnv:
            def __init__(self):
                self.scene = {"robot": FakeAsset()}

        left_shoulder_cfg = FakeSceneEntityCfg("robot")
        left_shoulder_cfg.body_ids = [0]
        left_hand_cfg = FakeSceneEntityCfg("robot")
        left_hand_cfg.body_ids = [1]
        right_shoulder_cfg = FakeSceneEntityCfg("robot")
        right_shoulder_cfg.body_ids = [2]
        right_hand_cfg = FakeSceneEntityCfg("robot")
        right_hand_cfg.body_ids = [3]

        penalty = stand_rewards.arm_vertical_alignment_l2(
            FakeEnv(),
            left_shoulder_body_cfg=left_shoulder_cfg,
            left_hand_body_cfg=left_hand_cfg,
            right_shoulder_body_cfg=right_shoulder_cfg,
            right_hand_body_cfg=right_hand_cfg,
        )

        torch.testing.assert_close(penalty, torch.tensor([0.0, 4.0]))


if __name__ == "__main__":
    unittest.main()
