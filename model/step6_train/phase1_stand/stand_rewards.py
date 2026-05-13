"""Custom reward helpers for Phase 1 G1 standing training."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from isaaclab.managers import SceneEntityCfg

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


LEFT_ARM_SWING_JOINT_NAMES = [
    "left_shoulder_pitch_joint",
    "left_shoulder_roll_joint",
    "left_shoulder_yaw_joint",
    "left_elbow_joint",
    "left_wrist_roll_joint",
    "left_wrist_pitch_joint",
    "left_wrist_yaw_joint",
]
RIGHT_ARM_SWING_JOINT_NAMES = [
    "right_shoulder_pitch_joint",
    "right_shoulder_roll_joint",
    "right_shoulder_yaw_joint",
    "right_elbow_joint",
    "right_wrist_roll_joint",
    "right_wrist_pitch_joint",
    "right_wrist_yaw_joint",
]


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


def _contact_force_norm_history(env: "ManagerBasedRLEnv", sensor_cfg: SceneEntityCfg) -> torch.Tensor:
    """Return max contact force norm over sensor history for the selected bodies."""
    contact_sensor = env.scene.sensors[sensor_cfg.name]
    return contact_sensor.data.net_forces_w_history[:, :, sensor_cfg.body_ids, :].norm(dim=-1).max(dim=1)[0]


def feet_slide(
    env: "ManagerBasedRLEnv",
    sensor_cfg: SceneEntityCfg,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    contact_threshold: float = 1.0,
) -> torch.Tensor:
    """Penalize planar ankle-link velocity while a foot is in contact."""
    contacts = _contact_force_norm_history(env, sensor_cfg) > contact_threshold
    asset = env.scene[asset_cfg.name]
    body_vel_xy = asset.data.body_lin_vel_w[:, asset_cfg.body_ids, :2]
    return torch.sum(body_vel_xy.norm(dim=-1) * contacts, dim=1)


def feet_contact_presence(
    env: "ManagerBasedRLEnv",
    sensor_cfg: SceneEntityCfg,
    contact_threshold: float = 1.0,
) -> torch.Tensor:
    """Penalize missing ankle contacts during standing."""
    contacts = _contact_force_norm_history(env, sensor_cfg) > contact_threshold
    return contacts.shape[1] - torch.sum(contacts.float(), dim=1)


def feet_contact_balance(
    env: "ManagerBasedRLEnv",
    sensor_cfg: SceneEntityCfg,
    eps: float = 1.0e-6,
) -> torch.Tensor:
    """Penalize left-right ankle contact force imbalance."""
    contact_force_norm = _contact_force_norm_history(env, sensor_cfg)
    left_force = contact_force_norm[:, 0]
    right_force = contact_force_norm[:, 1]
    return torch.abs(left_force - right_force) / (left_force + right_force + eps)


def _limb_has_contact(
    env: "ManagerBasedRLEnv",
    sensor_cfg: SceneEntityCfg,
    contact_threshold: float,
) -> torch.Tensor:
    """Return true when any selected body in a limb is in contact."""
    contacts = _contact_force_norm_history(env, sensor_cfg) > contact_threshold
    return torch.any(contacts, dim=1)


def collapse_ground_contact(
    env: "ManagerBasedRLEnv",
    left_leg_sensor_cfg: SceneEntityCfg,
    right_leg_sensor_cfg: SceneEntityCfg,
    left_arm_sensor_cfg: SceneEntityCfg,
    right_arm_sensor_cfg: SceneEntityCfg,
    contact_threshold: float = 1.0,
    min_contacting_limbs: int = 3,
) -> torch.Tensor:
    """Return true when at least the configured number of limb groups contact the ground."""
    limb_contacts = torch.stack(
        (
            _limb_has_contact(env, left_leg_sensor_cfg, contact_threshold),
            _limb_has_contact(env, right_leg_sensor_cfg, contact_threshold),
            _limb_has_contact(env, left_arm_sensor_cfg, contact_threshold),
            _limb_has_contact(env, right_arm_sensor_cfg, contact_threshold),
        ),
        dim=1,
    )
    return torch.sum(limb_contacts.int(), dim=1) >= min_contacting_limbs


def all_limbs_ground_contact(
    env: "ManagerBasedRLEnv",
    left_leg_sensor_cfg: SceneEntityCfg,
    right_leg_sensor_cfg: SceneEntityCfg,
    left_arm_sensor_cfg: SceneEntityCfg,
    right_arm_sensor_cfg: SceneEntityCfg,
    contact_threshold: float = 1.0,
) -> torch.Tensor:
    """Backward-compatible four-limb collapse predicate."""
    return collapse_ground_contact(
        env,
        left_leg_sensor_cfg=left_leg_sensor_cfg,
        right_leg_sensor_cfg=right_leg_sensor_cfg,
        left_arm_sensor_cfg=left_arm_sensor_cfg,
        right_arm_sensor_cfg=right_arm_sensor_cfg,
        contact_threshold=contact_threshold,
        min_contacting_limbs=4,
    )


def root_height_below_minimum(
    env: "ManagerBasedRLEnv",
    minimum_height: float,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Return true when the robot root height above its terrain origin is below the limit."""
    asset = env.scene[asset_cfg.name]
    root_height = asset.data.root_pos_w[:, 2]
    env_origins = getattr(env.scene, "env_origins", None)
    if env_origins is not None:
        root_height = root_height - env_origins[:, 2]
    return root_height < minimum_height


def _event_reward_signal(env: "ManagerBasedRLEnv", event: torch.Tensor) -> torch.Tensor:
    """Return an event indicator scaled so RewardManager applies the configured weight once."""
    return event.float() / env.step_dt


def root_height_below_minimum_event(
    env: "ManagerBasedRLEnv",
    minimum_height: float,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
) -> torch.Tensor:
    """Reward signal for a full-fall event, corrected for RewardManager dt scaling."""
    return _event_reward_signal(env, root_height_below_minimum(env, minimum_height, asset_cfg=asset_cfg))


def collapse_ground_contact_event(
    env: "ManagerBasedRLEnv",
    left_leg_sensor_cfg: SceneEntityCfg,
    right_leg_sensor_cfg: SceneEntityCfg,
    left_arm_sensor_cfg: SceneEntityCfg,
    right_arm_sensor_cfg: SceneEntityCfg,
    contact_threshold: float = 1.0,
    min_contacting_limbs: int = 3,
) -> torch.Tensor:
    """Reward signal for a multi-limb ground-contact collapse event."""
    return _event_reward_signal(
        env,
        collapse_ground_contact(
            env,
            left_leg_sensor_cfg=left_leg_sensor_cfg,
            right_leg_sensor_cfg=right_leg_sensor_cfg,
            left_arm_sensor_cfg=left_arm_sensor_cfg,
            right_arm_sensor_cfg=right_arm_sensor_cfg,
            contact_threshold=contact_threshold,
            min_contacting_limbs=min_contacting_limbs,
        ),
    )


def all_limbs_ground_contact_event(
    env: "ManagerBasedRLEnv",
    left_leg_sensor_cfg: SceneEntityCfg,
    right_leg_sensor_cfg: SceneEntityCfg,
    left_arm_sensor_cfg: SceneEntityCfg,
    right_arm_sensor_cfg: SceneEntityCfg,
    contact_threshold: float = 1.0,
) -> torch.Tensor:
    """Backward-compatible four-limb collapse reward signal."""
    return collapse_ground_contact_event(
        env,
        left_leg_sensor_cfg=left_leg_sensor_cfg,
        right_leg_sensor_cfg=right_leg_sensor_cfg,
        left_arm_sensor_cfg=left_arm_sensor_cfg,
        right_arm_sensor_cfg=right_arm_sensor_cfg,
        contact_threshold=contact_threshold,
        min_contacting_limbs=4,
    )


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


def joint_pos_hard_limits_l1(
    env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")
) -> torch.Tensor:
    """Penalize the absolute amount that joint positions exceed hard USD limits."""
    asset = env.scene[asset_cfg.name]
    if asset_cfg.joint_ids is None:
        asset_cfg.joint_ids = slice(None)

    joint_pos = asset.data.joint_pos[:, asset_cfg.joint_ids]
    joint_limits = asset.data.joint_pos_limits[:, asset_cfg.joint_ids]
    lower_excess = torch.clamp(joint_limits[..., 0] - joint_pos, min=0.0)
    upper_excess = torch.clamp(joint_pos - joint_limits[..., 1], min=0.0)
    return torch.sum(lower_excess + upper_excess, dim=1)


def joint_pos_out_of_limit(
    env: "ManagerBasedRLEnv",
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    tolerance: float = 0.0,
) -> torch.Tensor:
    """Terminate when joint positions exceed the hard USD joint limits."""
    asset = env.scene[asset_cfg.name]
    if asset_cfg.joint_ids is None:
        asset_cfg.joint_ids = slice(None)

    limits = asset.data.joint_pos_limits[:, asset_cfg.joint_ids]
    joint_pos = asset.data.joint_pos[:, asset_cfg.joint_ids]
    out_of_upper_limits = torch.any(joint_pos > limits[..., 1] + tolerance, dim=1)
    out_of_lower_limits = torch.any(joint_pos < limits[..., 0] - tolerance, dim=1)
    return torch.logical_or(out_of_upper_limits, out_of_lower_limits)


def joint_vel_out_of_limit(
    env: "ManagerBasedRLEnv", asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")
) -> torch.Tensor:
    """Return true when joint velocities exceed hard USD velocity limits."""
    asset = env.scene[asset_cfg.name]
    if asset_cfg.joint_ids is None:
        asset_cfg.joint_ids = slice(None)

    joint_vel = torch.abs(asset.data.joint_vel[:, asset_cfg.joint_ids])
    joint_vel_limits = asset.data.joint_vel_limits[:, asset_cfg.joint_ids]
    return torch.any(joint_vel > joint_vel_limits, dim=1)


def joint_limit_violation(
    env: "ManagerBasedRLEnv",
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    tolerance: float = 0.0,
) -> torch.Tensor:
    """Return true when position or velocity exceeds a hard USD joint limit."""
    return torch.logical_or(
        joint_pos_out_of_limit(env, asset_cfg=asset_cfg, tolerance=tolerance),
        joint_vel_out_of_limit(env, asset_cfg=asset_cfg),
    )


def joint_limit_violation_event(
    env: "ManagerBasedRLEnv",
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    tolerance: float = 0.0,
) -> torch.Tensor:
    """Reward signal for a hard joint-limit event, corrected for RewardManager dt scaling."""
    return _event_reward_signal(env, joint_limit_violation(env, asset_cfg=asset_cfg, tolerance=tolerance))


def joint_deviation_symmetry_l1(
    env: "ManagerBasedRLEnv",
    left_asset_cfg: SceneEntityCfg,
    right_asset_cfg: SceneEntityCfg,
) -> torch.Tensor:
    """Penalize left-right mismatch in joint deviation from the default pose."""
    asset = env.scene[left_asset_cfg.name]
    left_deviation = (
        asset.data.joint_pos[:, left_asset_cfg.joint_ids]
        - asset.data.default_joint_pos[:, left_asset_cfg.joint_ids]
    )
    right_deviation = (
        asset.data.joint_pos[:, right_asset_cfg.joint_ids]
        - asset.data.default_joint_pos[:, right_asset_cfg.joint_ids]
    )
    return torch.sum(torch.abs(left_deviation - right_deviation), dim=1)


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
