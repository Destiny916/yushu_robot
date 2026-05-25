# Phase 1 Standing PPO

This component trains and evaluates a no-external-force standing policy for the
local Unitree G1 robot.

## Files

- `stand_env_cfg.py`: terrain-backed manager-based RL environment.
- `stand_rewards.py`: custom standing reward helpers.
- `stand_ppo_cfg.py`: RSL-RL PPO runner and algorithm config.
- `train_stand.py`: training entry with checkpoint resume support.
- `play_stand.py`: inference-only playback/validation entry.
- `test_*.py`: focused unit tests for config, rewards, training, and playback.

## Environment Summary

- Terrain: selected by `--terrain T0` through `--terrain T5`.
- Episode length: 60 seconds.
- Action: 29 joint position targets, scaled by `ACTION_SCALE = 0.10`.
- Observation: 93 values from base angular velocity, projected gravity, joint
  positions, joint velocities, and last action.
- Multi-env spacing: `DEFAULT_ENV_SPACING = 4.0`.
- Foot/ground friction: static and dynamic friction set to `2.0`.

## Standing Rewards

The standing policy is shaped to remain still and avoid early joint-limit
failures:

- Base stability: standing-time reward starts at `+5.0` per second, keeps the
  first 30 seconds at a cumulative `+150.0`, then ramps to `2x` by 60 seconds;
  flat orientation, height, horizontal velocity, and stronger angular velocity
  penalty `-1.5`.
- Smoothness: stronger joint velocity `-5.0e-3`, joint acceleration, and
  action-rate `-0.05` penalties.
- Joint safety: USD joint-position limit proximity, hard USD joint-position
  excess, and USD joint-velocity limit threshold at 30%.
- Foot contact quality: ankle contact sensors penalize stronger foot sliding
  `-0.5`, missing foot contacts, and a lighter left/right contact-force
  imbalance penalty `-0.15` for uneven terrain tolerance.
- Natural posture: waist and shoulder joints are encouraged to stay near the
  default standing pose, with dedicated shoulder pitch/roll/yaw posture `-2.0`,
  waist/torso alignment `-2.0`, mild hip deviation `-0.3`, elbow straightness
  `-2.0`, wrist/hand joint deviation `-1.0`, and left/right arm symmetry. The
  broad whole-arm default-pose penalty is intentionally removed to avoid
  over-constraining arm posture. Knee and ankle joints are intentionally not
  posture-constrained so the policy can adapt across terrain.
- Reset conditions: 60-second timeout, full-fall root height below `0.45m`
  relative to the terrain/env origin height, hard USD joint-position limit
  violation, or hard USD joint-velocity limit violation. Joint-position resets
  use a `0.005rad` tolerance to ignore tiny solver overshoot. The episode also
  resets when any three of the four limb groups contact the ground at the same
  step: each leg is counted by ankle or knee contact, and each arm is counted
  by elbow, wrist-yaw, or rubber-hand contact.
- Action targets: policy outputs are still interpreted as
  `default_joint_pos + action * 0.10`, then the final joint-position target is
  clamped into USD soft joint limits with a `0.005rad` margin before being sent
  to the actuator.
- Arm stillness: arm swing `-3.0` covers shoulder pitch/roll/yaw, elbow, and
  wrist joints, plus left/right arm swing asymmetry penalties and an arm
  vertical-alignment penalty `-1.0` that encourages straight arms to hang along
  the world vertical axis.
- Failure avoidance: `termination_penalty = -200.0` uses the same full-fall
  root-height definition as reset. This event reward counteracts IsaacLab
  RewardManager `dt` scaling, so a fall step receives the configured `-200.0`.
- Joint-limit failure avoidance: hard joint position or velocity limit
  violations receive `joint_limit_violation_penalty = -500.0`. This is also an
  event-scaled reward, so a hard joint-limit reset receives the configured
  `-500.0` on the violating step.
- Collapse-contact failure avoidance: three-limb ground-contact resets receive
  `collapse_ground_contact_penalty = -500.0` on the violating step.

## Train

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\train_stand.py `
  --terrain T0 `
  --num_envs 2 `
  --max_iterations 5000 `
  --save_interval 25 `
  --run_name T0_stand_stable
```

Training logs are written to:

```text
logs/rsl_rl/g1_stand/<timestamp>/
```

The newest model is copied to:

```text
checkpoint_stand.pt
```

## Resume Training

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\train_stand.py `
  --terrain T0 `
  --num_envs 2 `
  --max_iterations 5000 `
  --save_interval 25 `
  --resume `
  --load_run 2026-05-09_13-40-12_T0_stand_stable `
  --checkpoint checkpoint_stand.pt `
  --run_name T0_stand_resume
```

## Playback Without Training

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\play_stand.py `
  --terrain T0 `
  --num_envs 1 `
  --load_run 2026-05-09_13-40-12_T0_stand_stable `
  --checkpoint checkpoint_stand.pt
```

Headless validation:

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\play_stand.py `
  --headless `
  --terrain T0 `
  --num_envs 1 `
  --max_steps 500 `
  --report_interval 100 `
  --load_run 2026-05-09_13-40-12_T0_stand_stable `
  --checkpoint checkpoint_stand.pt
```

If a policy failure/reset is detected during validation, playback prints:

```text
error
```

## Harness

The local harness under `harness/` records the context, contracts, feedback loop,
and entropy controls for this standing phase while still allowing read-only
reference searches across the wider `yushu_robot` project and IsaacLab example
folders.

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\harness\scripts\check_harness_contracts.py
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\harness\scripts\collect_context.py
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\harness\scripts\search_reference_examples.py TerrainImporterCfg --max-results 5
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\harness\scripts\summarize_run.py --run-dir logs\rsl_rl\g1_stand\<run_name>
```

## Tests

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_env_cfg.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_rewards.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_train_stand.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_play_stand.py -v
```
