# Model Workflows

`model/` owns the IsaacLab side of the project: robot conversion, scene smoke
tests, manager-based environments, sensors, terrain definitions, PPO training,
and policy playback.

Keep source robot assets in `../yushu_robot_urdf/`. Keep generated USD assets in
`model/generatedUSD/`.

## Component Map

| Component | README | Main Purpose |
| --- | --- | --- |
| `build_robot_model/` | `build_robot_model/README.md` | Validate the local URDF and generate the G1 USD asset. |
| `step1_load_articulation/` | `step1_load_articulation/README.md` | Minimal IsaacLab articulation loading smoke test. |
| `step2_create_scene/` | `step2_create_scene/README.md` | Declarative `InteractiveSceneCfg` smoke test. |
| `step3_robot_cfg/` | `step3_robot_cfg/README.md` | Reusable local `G1_LOCAL_CFG` asset config. |
| `step4_manager_env/` | `step4_manager_env/README.md` | Minimal manager-based standing environment. |
| `step5_sensors/` | `step5_sensors/README.md` | Contact sensor environment extension. |
| `step6_train/` | `step6_train/README.md` | Terrain system and Phase 1 standing PPO training. |

## Common Commands

Run commands from the repository root:

```powershell
Set-Location D:\il\IsaacLab\scripts\yushu_robot
```

Use the IsaacLab virtual environment:

```powershell
D:\il\env\Scripts\python.exe
```

## Verification

Useful focused checks:

```powershell
D:\il\env\Scripts\python.exe -B model\build_robot_model\test_robot_asset.py -v
D:\il\env\Scripts\python.exe -B model\step1_load_articulation\test_step1_load_articulation.py -v
D:\il\env\Scripts\python.exe -B model\step2_create_scene\test_step2_create_scene.py -v
D:\il\env\Scripts\python.exe -B model\step3_robot_cfg\test_g1_local_cfg.py -v
D:\il\env\Scripts\python.exe -B model\step4_manager_env\test_stand_env_cfg.py -v
D:\il\env\Scripts\python.exe -B model\step5_sensors\test_sensors_cfg.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_env_cfg.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_rewards.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_train_stand.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_play_stand.py -v
```

Isaac Sim runtime smoke tests should use `--headless` and a small `--max_steps`
when available.

## Conventions

- Each step directory owns its scripts, helper modules, tests, and README.
- Keep heavy/generated artifacts out of source directories unless the workflow
  explicitly requires them.
- Prefer `-B` in commands to avoid `__pycache__` churn while running tests.
- Use `D:\il\env\Scripts\python.exe`, not the system Python.
