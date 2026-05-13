"""Tests for Phase 1 standing action target limit helpers."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
import sys
import unittest

import torch


PHASE1_STAND_DIR = Path(__file__).resolve().parent
if str(PHASE1_STAND_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE1_STAND_DIR))


class StandActionLimitTests(unittest.TestCase):
    def load_module(self):
        """Import action limit helpers with a clear assertion failure."""
        if importlib.util.find_spec("stand_action_limits") is None:
            self.fail("stand_action_limits module should exist for Phase 1 action target clamping")
        return importlib.import_module("stand_action_limits")

    def test_clamps_joint_position_targets_inside_limits_with_margin(self):
        action_limits = self.load_module()

        targets = torch.tensor([[-2.0, -0.2, 0.5, 2.0]], dtype=torch.float32)
        limits = torch.tensor([[[-1.0, 1.0], [-0.5, 0.5], [-0.6, 0.6], [-1.5, 1.5]]], dtype=torch.float32)

        clamped = action_limits.clamp_joint_position_targets(targets, limits, margin=0.05)

        torch.testing.assert_close(clamped, torch.tensor([[-0.95, -0.2, 0.5, 1.45]], dtype=torch.float32))


if __name__ == "__main__":
    unittest.main()
