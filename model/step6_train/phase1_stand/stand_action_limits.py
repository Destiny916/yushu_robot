"""Action target limit helpers for Phase 1 standing training."""

from __future__ import annotations

import torch


def clamp_joint_position_targets(
    targets: torch.Tensor,
    joint_pos_limits: torch.Tensor,
    margin: float = 0.0,
) -> torch.Tensor:
    """Clamp joint position targets inside joint limits with an optional safety margin."""
    lower = joint_pos_limits[..., 0]
    upper = joint_pos_limits[..., 1]
    if margin > 0.0:
        clamped_lower = lower + margin
        clamped_upper = upper - margin
        midpoint = 0.5 * (lower + upper)
        invalid_margin = clamped_lower > clamped_upper
        lower = torch.where(invalid_margin, midpoint, clamped_lower)
        upper = torch.where(invalid_margin, midpoint, clamped_upper)
    return torch.clamp(targets, min=lower, max=upper)
