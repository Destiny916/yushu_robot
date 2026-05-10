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
    def __init__(self, name: str, joint_names=None, preserve_order: bool = False):
        self.name = name
        self.joint_names = joint_names
        self.preserve_order = preserve_order
        self.joint_ids = slice(None)


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


if __name__ == "__main__":
    unittest.main()
