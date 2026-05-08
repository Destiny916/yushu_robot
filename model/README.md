# Model Simulation Code

`model/` is the home for simulation code used with the robot assets in this repository.

Use this directory for:

- IsaacLab task or environment configuration related to this robot.
- URDF-to-USD conversion helpers and generated asset wiring scripts.
- Training, evaluation, and replay entry points.
- Controller, policy, retargeting, and experiment configuration code.
- Small verification scripts that prove a robot asset or task loads correctly.

Keep robot geometry and part metadata in `../yushu_robot_urdf/`. Do not place STL, URDF, or mesh source files in `model/` unless a generated artifact is intentionally needed by a simulation workflow and documented here.

When adding new code, include a short note in the repository README if the command, environment ID, or workflow is useful for future runs.

## Directory Layout

Keep each independent workflow in its own folder under `model/`. A workflow folder owns its runnable scripts, helper modules, and tests. Shared generated USD assets live in `model/generatedUSD/`.

## Build the G1 Robot Asset

Run the local builder from the repository root:

```powershell
D:\il\env\Scripts\python.exe model\build_robot_model\build_g1_from_urdf.py --headless
```

The script validates every mesh referenced by `../yushu_robot_urdf/g1_29dof_mode_16.urdf`, converts the URDF into `model/generatedUSD/g1_29dof_mode_16.usd`, and opens only that robot USD. It does not add terrain, tasks, controllers, or motion.

This command requires an IsaacLab/Isaac Sim Python environment with the IsaacLab dependencies installed. This repository currently uses `D:\il\env\Scripts\python.exe`.

## Step 1: Load the G1 Articulation

After the USD exists in `model/generatedUSD/`, run the manual Articulation smoke test from the repository root:

```powershell
D:\il\env\Scripts\python.exe model\step1_load_articulation\step1_load_articulation.py --headless
```

This script follows `scripts/tutorials/01_assets/run_articulation.py`: it starts Isaac Sim, creates a ground plane and light, spawns one G1 articulation by default, and applies random joint efforts. If `--max_steps` is not set, the simulation runs until the app is closed. Bounded runs exit directly after `--max_steps` because this Windows Isaac Sim 5.1 environment can hang while closing the stage through `SimulationApp.close()`. Pass `--graceful_close` when you specifically want to test the normal close path.

## Step 2: Load the G1 with InteractiveScene

Run the declaration-style scene version from the repository root:

```powershell
D:\il\env\Scripts\python.exe model\step2_create_scene\step2_create_scene.py --headless
```

This script follows `scripts/tutorials/02_scene/create_scene.py`: it defines a `G1SceneCfg`, spawns the robot at `{ENV_REGEX_NS}/Robot`, and advances the simulation through `scene.write_data_to_sim()` and `scene.update()`. It also defaults to one robot and an infinite run unless `--max_steps` is provided.

## Step 3: Reusable Local Robot Config

The reusable local G1 configuration lives in:

```text
model/step3_robot_cfg/g1_local_cfg.py
```

It exports `G1_LOCAL_CFG` and `make_g1_local_cfg()`. The config uses the global generated USD in `model/generatedUSD/`, groups actuators as `legs`, `feet`, `waist`, and `arms`, and can be reused by later scene and environment steps with `.replace(prim_path=...)`.

## Step 4: Manager-Based Stand Environment

Run the minimal Manager-Based environment from the repository root:

```powershell
D:\il\env\Scripts\python.exe model\step4_manager_env\run_stand_env.py --headless
```

The environment lives in `model/step4_manager_env/`. It uses `G1_LOCAL_CFG`, one `JointPositionActionCfg` over all 29 joints, reset events for root and joints, and a concatenated policy observation with shape `(num_envs, 93)` for one robot state/action vector.

## Step 5: Contact Sensors

Run the sensor smoke test from the repository root:

```powershell
D:\il\env\Scripts\python.exe model\step5_sensors\run_sensors_env.py --headless
```

This step extends the Step 4 Manager-Based environment with a `ContactSensorCfg` on `{ENV_REGEX_NS}/Robot/.*ankle_roll_link`. The default one-robot run reports contact force tensors with shape `(1, 2, 3)`. Camera integration remains optional and should be added only after a stable camera prim is chosen.
