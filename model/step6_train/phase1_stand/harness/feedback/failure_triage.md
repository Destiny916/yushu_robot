# Failure Triage Guide

Use this guide before changing rewards or reset logic.

## Joint Limit Or Velocity Limit

Check `stand_action_limits.py`, `stand_actions.py`, `JOINT_POS_LIMIT_TOLERANCE`,
`joint_pos_out_of_limit`, and `joint_vel_out_of_limit`.

## Shoulder Or Arm Motion

Check `SHOULDER_POSTURE_JOINTS`, `joint_deviation_shoulders`,
`joint_deviation_arms`, `arm_swing_l2`, and `arm_swing_asymmetry_l2`.

## Robot Lies Down Without Reset

Check `root_height_below_minimum`, `collapse_ground_contact`, contact sensor
body names, and `COLLAPSE_GROUND_CONTACT_MIN_LIMBS`.

## Terrain-Specific Failure

Search `model/step6_train/terrains` first, then IsaacLab terrain examples under
`D:/il/IsaacLab/scripts/demos`, `tutorials`, and `source`.
