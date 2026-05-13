"""Custom action terms for Phase 1 G1 standing training."""

from __future__ import annotations

from isaaclab.envs.mdp.actions import actions_cfg
from isaaclab.envs.mdp.actions.joint_actions import JointPositionAction
from isaaclab.utils import configclass

from stand_action_limits import clamp_joint_position_targets


class ClampedJointPositionAction(JointPositionAction):
    """Joint position action that clamps final targets to USD joint limits."""

    cfg: "ClampedJointPositionActionCfg"

    def __init__(self, cfg: "ClampedJointPositionActionCfg", env):
        super().__init__(cfg, env)
        if self.cfg.limit_kind not in ("soft", "hard"):
            raise ValueError(f"Unsupported limit_kind: {self.cfg.limit_kind!r}. Expected 'soft' or 'hard'.")

    def process_actions(self, actions):
        super().process_actions(actions)
        if self.cfg.limit_kind == "soft":
            joint_pos_limits = self._asset.data.soft_joint_pos_limits[:, self._joint_ids]
        else:
            joint_pos_limits = self._asset.data.joint_pos_limits[:, self._joint_ids]
        self._processed_actions = clamp_joint_position_targets(
            self._processed_actions,
            joint_pos_limits,
            margin=self.cfg.limit_margin,
        )


@configclass
class ClampedJointPositionActionCfg(actions_cfg.JointPositionActionCfg):
    """Config for joint position targets clamped to USD joint limits."""

    class_type: type = ClampedJointPositionAction
    limit_kind: str = "soft"
    limit_margin: float = 0.0
