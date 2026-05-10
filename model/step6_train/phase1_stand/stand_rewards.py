"""Custom reward helpers for Phase 1 G1 standing training."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from isaaclab.managers import SceneEntityCfg

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


LEFT_ARM_SWING_JOINT_NAMES = ["left_shoulder_pitch_joint", "left_elbow_joint"]
RIGHT_ARM_SWING_JOINT_NAMES = ["right_shoulder_pitch_joint", "right_elbow_joint"]


def make_left_arm_swing_cfg() -> SceneEntityCfg:
    """Create a scene entity cfg for the left arm swing joints."""
    return SceneEntityCfg("robot", joint_names=LEFT_ARM_SWING_JOINT_NAMES, preserve_order=True)


def make_right_arm_swing_cfg() -> SceneEntityCfg:
    """Create a scene entity cfg for the right arm swing joints."""
    return SceneEntityCfg("robot", joint_names=RIGHT_ARM_SWING_JOINT_NAMES, preserve_order=True)


def lin_vel_xy_l2(env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
    """Penalize horizontal root velocity for standing."""
    asset = env.scene[asset_cfg.name]
    return torch.sum(torch.square(asset.data.root_lin_vel_b[:, :2]), dim=1)


def joint_pos_soft_limits_l2(
    env: "ManagerBasedRLEnv",
    soft_ratio: float = 0.6,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Penalize joint positions once they exceed a fraction of the USD joint range."""
    asset = env.scene[asset_cfg.name]
    joint_pos = asset.data.joint_pos[:, asset_cfg.joint_ids]
    joint_limits = asset.data.joint_pos_limits[:, asset_cfg.joint_ids]

    joint_center = 0.5 * (joint_limits[..., 0] + joint_limits[..., 1])
    joint_half_range = 0.5 * (joint_limits[..., 1] - joint_limits[..., 0])
    lower_bound = joint_center - soft_ratio * joint_half_range
    upper_bound = joint_center + soft_ratio * joint_half_range
    violation = torch.clamp(lower_bound - joint_pos, min=0.0) + torch.clamp(joint_pos - upper_bound, min=0.0)
    return torch.sum(torch.square(violation), dim=1)


def joint_pos_out_of_limit(
    env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")
) -> torch.Tensor:
    """Terminate when joint positions exceed the hard USD joint limits."""
    asset = env.scene[asset_cfg.name]
    if asset_cfg.joint_ids is None:
        asset_cfg.joint_ids = slice(None)

    limits = asset.data.joint_pos_limits[:, asset_cfg.joint_ids]
    out_of_upper_limits = torch.any(asset.data.joint_pos[:, asset_cfg.joint_ids] > limits[..., 1], dim=1)
    out_of_lower_limits = torch.any(asset.data.joint_pos[:, asset_cfg.joint_ids] < limits[..., 0], dim=1)
    return torch.logical_or(out_of_upper_limits, out_of_lower_limits)


def joint_vel_usd_limits_l1(
    env: "ManagerBasedRLEnv",
    soft_ratio: float = 0.3,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Penalize joint velocities once they exceed a fraction of the USD velocity limit."""
    asset = env.scene[asset_cfg.name]
    joint_vel = torch.abs(asset.data.joint_vel[:, asset_cfg.joint_ids])
    joint_vel_limits = asset.data.joint_vel_limits[:, asset_cfg.joint_ids]
    violation = joint_vel - soft_ratio * joint_vel_limits
    return torch.sum(torch.clamp(violation, min=0.0), dim=1)


def joint_vel_soft_limits_l2(
    env: "ManagerBasedRLEnv",
    soft_ratio: float = 0.6,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Penalize joint velocities once they exceed a fraction of the soft joint velocity limit."""
    asset = env.scene[asset_cfg.name]
    joint_vel = asset.data.joint_vel[:, asset_cfg.joint_ids]
    soft_vel_limits = asset.data.soft_joint_vel_limits[:, asset_cfg.joint_ids]
    violation = torch.abs(joint_vel) - soft_ratio * soft_vel_limits
    return torch.sum(torch.square(torch.clamp(violation, min=0.0)), dim=1)


def arm_swing_l2(
    env: "ManagerBasedRLEnv",
    left_asset_cfg: SceneEntityCfg,
    right_asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Penalize arm swing energy so the standing policy stays still."""
    asset = env.scene[left_asset_cfg.name]
    left_vel = asset.data.joint_vel[:, left_asset_cfg.joint_ids]
    right_vel = asset.data.joint_vel[:, right_asset_cfg.joint_ids]
    return torch.sum(torch.square(left_vel), dim=1) + torch.sum(torch.square(right_vel), dim=1)


def arm_swing_asymmetry_l2(
    env: "ManagerBasedRLEnv",
    left_asset_cfg: SceneEntityCfg,
    right_asset_cfg: SceneEntityCfg,
    tolerance: float = 0.5,
) -> torch.Tensor:
    """Penalize left-right arm swing imbalance when one side is much more active."""
    asset = env.scene[left_asset_cfg.name]
    left_motion = torch.mean(torch.abs(asset.data.joint_vel[:, left_asset_cfg.joint_ids]), dim=1)
    right_motion = torch.mean(torch.abs(asset.data.joint_vel[:, right_asset_cfg.joint_ids]), dim=1)
    relative_difference = torch.abs(left_motion - right_motion) / (0.5 * (left_motion + right_motion) + 1.0e-6)
    return torch.square(torch.clamp(relative_difference - tolerance, min=0.0))
