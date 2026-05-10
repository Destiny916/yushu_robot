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
- Episode length: 300 seconds.
- Action: 29 joint position targets, scaled by `ACTION_SCALE = 0.10`.
- Observation: 93 values from base angular velocity, projected gravity, joint
  positions, joint velocities, and last action.
- Multi-env spacing: `DEFAULT_ENV_SPACING = 4.0`.
- Foot/ground friction: static and dynamic friction set to `2.0`.

## Standing Rewards

The standing policy is shaped to remain still and avoid early joint-limit
failures:

- Base stability: alive reward, flat orientation, height, horizontal velocity,
  and angular velocity.
- Smoothness: joint velocity, joint acceleration, and action-rate penalties.
- Joint safety: USD joint-position limit proximity, USD joint-velocity limit
  threshold at 30%, and hard USD joint-position termination.
- Arm stillness: arm swing and left/right arm swing asymmetry penalties.
- Failure avoidance: `termination_penalty = -200.0`.

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

## Tests

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_env_cfg.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_rewards.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_train_stand.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_play_stand.py -v
```
