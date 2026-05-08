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

## Step 6: Terrain System (P1.1)

The AHC training terrain system lives in `model/step6_train/terrains/`. Each terrain type is an independent Python file that exports a `make_terrain_cfg()` function (lazy import pattern for Isaac Sim compatibility).

Run the terrain test from the repository root:

```powershell
D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T0 --headless --max_steps 2
```

Available terrains: `T0` (flat), `T1` (10° slope), `T2` (20° slope), `T3` (30° slope), `T4` (stairs), `T5` (wave). Use `--terrain <key>` to select, `--num_envs N` for multiple robots. The robot stands still on the terrain; height info is printed every 50 steps.

Design doc and implementation plan: `model/step6_train/spec/2026-05-08_g1_ahc_standing/`.

## Step 6: AHC Deep RL Training Framework

Step 6 implements the AHC (Adaptive Humanoid Control) multi-behavior distillation training framework. Code lives in `model/step6_train/` with three major subsystems:

### Terrain System (P1.1)

Six terrain types, each in its own Python file with lazy imports for Isaac Sim compatibility:

| Terrain | File | Type | Key Parameter |
|---------|------|------|---------------|
| T0 | `T0_plane.py` | Flat plane | — |
| T1 | `T1_slope_10.py` | 10° slope | slope=0.175 rad |
| T2 | `T2_slope_20.py` | 20° slope | slope=0.349 rad |
| T3 | `T3_slope_30.py` | 30° slope | slope=0.524 rad |
| T4 | `T4_stairs.py` | Stairs | step_height 0.05-0.15m, width 0.3m |
| T5 | `T5_wave.py` | Irregular wave | amplitude 0.02-0.08m |

Each file exports `make_terrain_cfg()` (deferred import pattern). The `terrains/__init__.py` provides `TERRAIN_MAKERS`, `TERRAIN_NAMES`, and `get_terrain_cfg(key)` for lazy lookup.

### Phase 1 Standing PPO (P1.2)

The standing environment and PPO training entry live in `model/step6_train/phase1_stand/`. It uses PPO (Proximal Policy Optimization) via RSL-RL's `OnPolicyRunner`.

**Key files:**

- `stand_env_cfg.py` — Manager-Based RL environment config with 11 reward terms, 4 termination conditions, 93-dim observation, 29-dim action
- `stand_rewards.py` — Custom reward function `lin_vel_xy_l2` for horizontal velocity penalty
- `stand_ppo_cfg.py` — PPO hyperparameters: Actor/Critic [512,256,128], lr=1e-3, γ=0.99, λ=0.95
- `train_stand.py` — Training entry with resume/checkpoint support

**Reward design (11 terms):**

| Reward | Weight | Purpose |
|--------|--------|---------|
| `is_alive` | +1.0 | Survival bonus per step |
| `flat_orientation_l2` | -2.0 | Torso tilt penalty |
| `base_height_l2` | -1.0 | Height deviation from 0.78m target |
| `lin_vel_xy_l2` | -1.5 | Horizontal velocity penalty (standing = zero) |
| `ang_vel_xy_l2` | -0.5 | Angular velocity penalty |
| `joint_torques_l2` | -2.5e-5 | Energy efficiency (very small weight) |
| `joint_vel_l2` | -1.0e-3 | Joint velocity smoothing |
| `joint_acc_l2` | -2.5e-7 | Joint acceleration smoothing (tiny weight) |
| `action_rate_l2` | -0.01 | Action change rate penalty |
| `joint_deviation_l1` | -0.1 | Deviation from default pose |
| `termination_penalty` | -200.0 | Catastrophic fall penalty |

**Termination conditions:** bad_orientation (>45°), root_height (<0.45m), joint_pos_out_of_limit, time_out (30s).

**Network architecture:**

```
Actor: Input(93) → 512 → ELU → 256 → ELU → 128 → ELU → 29 → tanh
Critic: Input(93) → 512 → ELU → 256 → ELU → 128 → ELU → 1
```

**Verify:**

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_env_cfg.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_train_stand.py -v
```

**Short smoke training:**

```powershell
D:\il\env\Scripts\python.exe model\step6_train\phase1_stand\train_stand.py --headless --num_envs 64 --max_iterations 100 --run_name smoke
```

**Full standing PPO training:**

```powershell
D:\il\env\Scripts\python.exe model\step6_train\phase1_stand\train_stand.py --headless --num_envs 4096 --max_iterations 1500
```

**Resume from checkpoint:**

```powershell
D:\il\env\Scripts\python.exe model\step6_train\phase1_stand\train_stand.py --headless --resume --load_run <run-folder> --checkpoint checkpoint_stand.pt
```

Training logs and checkpoints are written under `logs/rsl_rl/g1_stand/<timestamp>/`. RSL-RL checkpoints are saved as `model_*.pt`, and the newest checkpoint is also copied to `checkpoint_stand.pt` after training finishes.

### AHC Three-Phase Architecture (Planned)

The full AHC scheme has three phases:

1. **Phase 1 (PPO)**: Train standing (π_stand) and walking (π_walk) policies independently across T0-T5 terrains
2. **Phase 2 (DAgger)**: Distill both into a MoE unified policy — Gating Network blends frozen experts: `action = α·π_stand(obs) + (1-α)·π_walk(obs)`
3. **Phase 3 (PCGrad)**: End-to-end fine-tuning with Projecting Conflicting Gradients for smooth stand↔walk transitions

Phase 2 and Phase 3 implementation is planned under `model/step6_train/phase2_dagger/` and `model/step6_train/phase3_pcgrad/`.
