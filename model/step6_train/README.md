# Step 6: AHC Training

This component contains the terrain system and Phase 1 standing PPO workflow for
the G1 AHC training plan.

## Subcomponents

| Path | Purpose |
| --- | --- |
| `terrains/` | Terrain generator configs `T0` to `T5`. |
| `phase1_stand/` | No-external-force standing environment, PPO config, training, and playback. |
| `spec/2026-05-08_g1_ahc_standing/` | Technical spec and planning documents. |

## Terrain Test

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\terrains\test_terrains.py --terrain T0 --headless --max_steps 2
```

## Phase 1 Standing Tests

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_env_cfg.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_rewards.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_train_stand.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_play_stand.py -v
```

## Train Standing PPO

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\train_stand.py `
  --terrain T0 `
  --num_envs 2 `
  --max_iterations 5000 `
  --save_interval 25 `
  --run_name T0_stand_stable
```

## Playback

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\play_stand.py `
  --terrain T0 `
  --num_envs 1 `
  --load_run <run-folder> `
  --checkpoint checkpoint_stand.pt
```
