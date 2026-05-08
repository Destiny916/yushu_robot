# Yushu Robot Project Plan

> Last updated: 2026-05-08

## Goal

Build a local IsaacLab simulation and training workflow for the Unitree G1 29DOF robot from this repository's URDF and mesh assets.

The project progresses one step at a time. Each step must be placed in its own folder under `model/`, verified independently, and only continued after user confirmation.

## Fixed Project Rules

- Work only inside `d:\il\IsaacLab\scripts\yushu_robot`.
- Use `D:\il\env\Scripts\python.exe` for IsaacLab and Isaac Sim commands.
- Keep robot asset source files in `yushu_robot_urdf/`.
- Keep simulation, scene, environment, training, and test code in `model/`.
- Keep generated USD assets globally in `model/generatedUSD/`.
- Do not put generated USD output inside a step folder.
- Default runtime behavior for scene scripts:
  - one robot by default
  - `--max_steps 0` means infinite loop
  - pass `--max_steps N` only for bounded verification
- Current Windows + Isaac Sim 5.1 can hang during `SimulationApp.close()` stage cleanup. Bounded scripts may exit directly after `--max_steps`; use `--graceful_close` only when testing normal close behavior.
- Stop after each step and wait for user confirmation before implementing the next step.
- Do not commit or push unless the user explicitly asks.

## Repository Layout

```text
yushu_robot/
├── PROJECT_PLAN.md
├── README.md
├── spec.md
├── yushu_robot_urdf/
│   ├── g1_29dof_mode_16.urdf
│   └── meshes/
└── model/
    ├── README.md
    ├── build_robot_model/
    ├── generatedUSD/
    ├── step1_load_articulation/
    ├── step2_create_scene/
    ├── step3_robot_cfg/
    ├── step4_manager_env/
    ├── step5_sensors/
    └── step6_train/
```

Steps 0-5 are complete. Step 6 P1.1 (terrain system) is complete under `model/step6_train/terrains/`.

## Current Status

| Step | Status | Folder | Purpose |
|------|--------|--------|---------|
| Step 0 | Complete | `model/build_robot_model/` | Convert URDF + meshes into global USD |
| Step 1 | Complete | `model/step1_load_articulation/` | Load one G1 with manual `Articulation` API |
| Step 2 | Complete | `model/step2_create_scene/` | Load one G1 with `InteractiveSceneCfg` |
| Step 3 | Complete | `model/step3_robot_cfg/` | Reusable local `G1_LOCAL_CFG` |
| Step 4 | Complete | `model/step4_manager_env/` | Manager-Based RL environment |
| Step 5 | Complete | `model/step5_sensors/` | Contact sensor integration |
| Step 6 | P1.1 Terrain Complete | `model/step6_train/` | AHC multi-behavior distillation (23 files planned) |

## Known Warnings

These warnings are known and not Step 1-3 blockers:

- Empty sensor links from the URDF can cause unresolved visual reference warnings for `imu_in_pelvis`, `imu_in_torso`, `d435_link`, and `mid360_link`.
- IsaacLab may warn about `enable_external_forces_every_iteration=False`; this is advisory.
- Isaac Sim may log MaterialX, dynamic control deprecation, or GPU/system information warnings during startup.

## Completed Work

### Step 0: Build Global USD

Files:

- `model/build_robot_model/build_g1_from_urdf.py`
- `model/build_robot_model/robot_asset.py`
- `model/build_robot_model/test_robot_asset.py`
- `model/generatedUSD/.gitignore`

Outputs:

- `model/generatedUSD/g1_29dof_mode_16.usd`
- `model/generatedUSD/configuration/...`

Verification:

```powershell
D:\il\env\Scripts\python.exe model\build_robot_model\build_g1_from_urdf.py --headless
D:\il\env\Scripts\python.exe -m pytest model\build_robot_model\test_robot_asset.py -v
```

### Step 1: Manual Articulation Load

Files:

- `model/step1_load_articulation/step1_load_articulation.py`
- `model/step1_load_articulation/test_step1_load_articulation.py`

Behavior:

- Starts Isaac Sim with `AppLauncher`.
- Creates `SimulationContext`.
- Manually creates ground, dome light, and robot origin.
- Loads the global generated USD as an `Articulation`.
- Applies random joint efforts.
- Defaults to one robot and infinite runtime.

Verification:

```powershell
D:\il\env\Scripts\python.exe -B -m unittest test_step1_load_articulation -v
D:\il\env\Scripts\python.exe model\step1_load_articulation\step1_load_articulation.py --headless --max_steps 2
```

### Step 2: InteractiveScene Load

Files:

- `model/step2_create_scene/step2_create_scene.py`
- `model/step2_create_scene/test_step2_create_scene.py`

Behavior:

- Uses `InteractiveSceneCfg`.
- Spawns ground, dome light, and robot declaratively.
- Robot prim path is `{ENV_REGEX_NS}/Robot`.
- Defaults to one robot and infinite runtime.
- Uses `scene.write_data_to_sim()` and `scene.update()`.

Verification:

```powershell
D:\il\env\Scripts\python.exe -B -m unittest test_step2_create_scene -v
D:\il\env\Scripts\python.exe model\step2_create_scene\step2_create_scene.py --headless --max_steps 2
```

### Step 3: Reusable Local Robot Config

Files:

- `model/step3_robot_cfg/g1_local_cfg.py`
- `model/step3_robot_cfg/test_g1_local_cfg.py`

Behavior:

- Exports `G1_LOCAL_CFG`.
- Exports `make_g1_local_cfg()`.
- Uses global generated USD.
- Provides actuator groups:
  - `legs`
  - `feet`
  - `waist`
  - `arms`
- Step 2 now reuses `G1_LOCAL_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")`.

Verification:

```powershell
D:\il\env\Scripts\python.exe -B -m unittest test_g1_local_cfg -v
D:\il\env\Scripts\python.exe -B -m unittest test_step2_create_scene -v
D:\il\env\Scripts\python.exe model\step2_create_scene\step2_create_scene.py --headless --max_steps 2
```

### Step 4: Manager-Based Environment

Purpose:

Create a minimal Manager-Based RL environment for standing-oriented testing. This step does not attempt full reward shaping or training yet. It proves that the robot can be wrapped in a Manager-Based environment and stepped successfully.

Files:

- `model/step4_manager_env/stand_env_cfg.py`
- `model/step4_manager_env/run_stand_env.py`
- `model/step4_manager_env/test_stand_env_cfg.py`

Behavior:

- Scene config uses `G1_LOCAL_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")`.
- Observations:
  - base angular velocity
  - projected gravity
  - joint position relative
  - joint velocity relative
  - last action
- Action:
  - joint position action over all 29 joints
- Reset events:
  - reset root state near origin
  - reset joints by zero offset from default
- Runner creates the environment and calls `env.step()` with random actions.
- Defaults to one robot and infinite runtime.
- Supports `--max_steps` for bounded verification.

Verification:

```powershell
D:\il\env\Scripts\python.exe -B -m unittest test_stand_env_cfg -v
D:\il\env\Scripts\python.exe model\step4_manager_env\run_stand_env.py --headless --max_steps 2
```

Verified result:

- Action shape: 29
- Policy observation shape: `(1, 93)` for default one-robot run
- Known unresolved visual reference warnings remain limited to empty sensor links.

### Step 5: Contact Sensors

Purpose:

Add ankle contact sensor configuration after the Manager-Based environment is stable.

Files:

- `model/step5_sensors/sensors_cfg.py`
- `model/step5_sensors/run_sensors_env.py`
- `model/step5_sensors/test_sensors_cfg.py`

Behavior:

- Extends Step 4 environment with `ContactSensorCfg`.
- Enables contact sensors on the robot USD spawn config.
- Contact sensor target:

```python
ContactSensorCfg(
    prim_path="{ENV_REGEX_NS}/Robot/.*ankle_roll_link",
    update_period=0.0,
    history_length=6,
)
```

- Camera integration remains optional until a stable camera prim is chosen.

Verification:

```powershell
D:\il\env\Scripts\python.exe -B -m unittest test_sensors_cfg -v
D:\il\env\Scripts\python.exe model\step5_sensors\run_sensors_env.py --headless --max_steps 2
```

Verified result:

- Contact force shape: `(1, 2, 3)` for default one-robot run
- Policy observation shape remains `(1, 93)`
- Maximum contact force can be read from `contact_forces.data.net_forces_w`

## Next Step: Step 6 AHC Multi-Behavior Distillation Training

Status: **Spec Complete** — see `model/step6_train/spec/2026-05-08_g1_ahc_standing/`

The AHC (Adaptive Humanoid Control) scheme trains the G1 robot to stand across 6 terrain types (flat, 10°/20°/30° slopes, stairs, irregular waves) and walk with smooth switching via confidence command `c ∈ [0,1]`.

Three phases:
1. **Phase 1**: PPO independently trains Standing and Walking specialized policies
2. **Phase 2**: DAgger distills both into a MoE unified policy (Gating Network + frozen Experts)
3. **Phase 3**: PCGrad multi-task PPO fine-tuning for smooth stand↔walk transitions

Spec doc: `model/step6_train/spec/2026-05-08_g1_ahc_standing/spec.md`
Plan doc: `model/step6_train/spec/2026-05-08_g1_ahc_standing/plan.md`

Implementation scope: 23 files across 7 subdirectories under `model/step6_train/`.

Acceptance criteria:

- Phase 1: Standing survival > 95% (flat), > 80% (30° slope); Walking avg velocity error < 0.2 m/s
- Phase 2: α prediction MSE < 0.05; MoE standing survival > 90% (c=1); walking error < 0.3 m/s (c=0)
- Phase 3: Performance ≥ Phase 2; smooth action transition across c ∈ [0, 1]

## Verification Checklist Before Saying a Step Is Complete

For every step:

- Run unit tests for the new folder.
- Run `py_compile` for changed Python files.
- Run one bounded IsaacLab command with `--headless --max_steps 2` when the step involves simulation.
- Check there are no residual Python processes for that step.
- Update `README.md`, `model/README.md`, `spec.md`, and this `PROJECT_PLAN.md` if behavior, commands, or status changed.
- Stop and wait for user confirmation.

## Git Notes

Current instruction: do not commit or push unless explicitly asked.

If upload is requested, use the repository's upload skill/rules and carefully stage only intended files. There are known unrelated workspace changes, including `.trae/skills/trae-upload-yushu-robot/SKILL.md`; do not stage unrelated changes by accident.
