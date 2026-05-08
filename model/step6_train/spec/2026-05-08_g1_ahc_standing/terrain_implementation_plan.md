# P1.1 Terrain System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create 6 independent terrain configuration files (T0-T5) and a shared test script that places the G1 robot on each terrain for verification.

**Architecture:** Each terrain file exports a standalone `TerrainGeneratorCfg` with a single sub-terrain type. A `TERRAIN_REGISTRY` dict in `__init__.py` maps terrain keys to configs. The test script uses `TerrainImporterCfg` to generate terrain in Isaac Sim and spawns the G1 robot via `G1_LOCAL_CFG`.

**Tech Stack:** Python, IsaacLab terrain API (`TerrainGeneratorCfg`, `TerrainImporterCfg`), IsaacLab scene API (`InteractiveSceneCfg`, `ManagerBasedEnv`)

**Design Doc:** `model/step6_train/spec/2026-05-08_g1_ahc_standing/terrain_design.md`

---

## File Structure

```
yushu_robot/model/step6_train/terrains/
├── __init__.py              # TERRAIN_REGISTRY dict
├── T0_plane.py              # MeshPlaneTerrainCfg
├── T1_slope_10.py           # HfPyramidSlopedTerrainCfg, slope=0.175
├── T2_slope_20.py           # HfPyramidSlopedTerrainCfg, slope=0.349
├── T3_slope_30.py           # HfPyramidSlopedTerrainCfg, slope=0.524
├── T4_stairs.py             # HfPyramidStairsTerrainCfg, step_height=0.05-0.15
├── T5_wave.py               # HfWaveTerrainCfg, amplitude=0.02-0.08
└── test_terrains.py         # Shared test runner with --terrain CLI param
```

---

### Task 1: Create T0_plane.py

**Files:**
- Create: `yushu_robot/model/step6_train/terrains/T0_plane.py`

- [ ] **Step 1: Create the T0 plane terrain file**

```python
"""T0: Flat Plane Terrain."""

from isaaclab.terrains import TerrainGeneratorCfg
from isaaclab.terrains.trimesh import MeshPlaneTerrainCfg

TERRAIN_NAME = "T0_plane"

TERRAIN_CFG = TerrainGeneratorCfg(
    size=(8.0, 8.0),
    border_width=20.0,
    num_rows=10,
    num_cols=1,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    curriculum=True,
    sub_terrains={
        "flat": MeshPlaneTerrainCfg(proportion=1.0),
    },
)
```

- [ ] **Step 2: Verify syntax**

Run: `D:\il\env\Scripts\python.exe -B -c "import ast; ast.parse(open('model/step6_train/terrains/T0_plane.py').read()); print('syntax ok')"`
Expected: `syntax ok`

- [ ] **Step 3: Commit**

```bash
git add model/step6_train/terrains/T0_plane.py
git commit -m "feat(terrains): add T0 flat plane terrain config"
```

---

### Task 2: Create T1_slope_10.py

**Files:**
- Create: `yushu_robot/model/step6_train/terrains/T1_slope_10.py`

- [ ] **Step 1: Create the T1 10-degree slope terrain file**

```python
"""T1: 10-degree Pyramid Slope Terrain (slope = 0.175 rad)."""

from isaaclab.terrains import TerrainGeneratorCfg
from isaaclab.terrains.height_field import HfPyramidSlopedTerrainCfg

TERRAIN_NAME = "T1_slope_10"

TERRAIN_CFG = TerrainGeneratorCfg(
    size=(8.0, 8.0),
    border_width=20.0,
    num_rows=10,
    num_cols=1,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    curriculum=True,
    sub_terrains={
        "slope_10": HfPyramidSlopedTerrainCfg(
            proportion=1.0,
            slope_range=(0.175, 0.175),
            platform_width=1.0,
        ),
    },
)
```

- [ ] **Step 2: Verify syntax**

Run: `D:\il\env\Scripts\python.exe -B -c "import ast; ast.parse(open('model/step6_train/terrains/T1_slope_10.py').read()); print('syntax ok')"`
Expected: `syntax ok`

- [ ] **Step 3: Commit**

```bash
git add model/step6_train/terrains/T1_slope_10.py
git commit -m "feat(terrains): add T1 10-degree slope terrain config"
```

---

### Task 3: Create T2_slope_20.py

**Files:**
- Create: `yushu_robot/model/step6_train/terrains/T2_slope_20.py`

- [ ] **Step 1: Create the T2 20-degree slope terrain file**

```python
"""T2: 20-degree Pyramid Slope Terrain (slope = 0.349 rad)."""

from isaaclab.terrains import TerrainGeneratorCfg
from isaaclab.terrains.height_field import HfPyramidSlopedTerrainCfg

TERRAIN_NAME = "T2_slope_20"

TERRAIN_CFG = TerrainGeneratorCfg(
    size=(8.0, 8.0),
    border_width=20.0,
    num_rows=10,
    num_cols=1,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    curriculum=True,
    sub_terrains={
        "slope_20": HfPyramidSlopedTerrainCfg(
            proportion=1.0,
            slope_range=(0.349, 0.349),
            platform_width=1.0,
        ),
    },
)
```

- [ ] **Step 2: Verify syntax**

Run: `D:\il\env\Scripts\python.exe -B -c "import ast; ast.parse(open('model/step6_train/terrains/T2_slope_20.py').read()); print('syntax ok')"`
Expected: `syntax ok`

- [ ] **Step 3: Commit**

```bash
git add model/step6_train/terrains/T2_slope_20.py
git commit -m "feat(terrains): add T2 20-degree slope terrain config"
```

---

### Task 4: Create T3_slope_30.py

**Files:**
- Create: `yushu_robot/model/step6_train/terrains/T3_slope_30.py`

- [ ] **Step 1: Create the T3 30-degree slope terrain file**

```python
"""T3: 30-degree Pyramid Slope Terrain (slope = 0.524 rad)."""

from isaaclab.terrains import TerrainGeneratorCfg
from isaaclab.terrains.height_field import HfPyramidSlopedTerrainCfg

TERRAIN_NAME = "T3_slope_30"

TERRAIN_CFG = TerrainGeneratorCfg(
    size=(8.0, 8.0),
    border_width=20.0,
    num_rows=10,
    num_cols=1,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    curriculum=True,
    sub_terrains={
        "slope_30": HfPyramidSlopedTerrainCfg(
            proportion=1.0,
            slope_range=(0.524, 0.524),
            platform_width=1.0,
        ),
    },
)
```

- [ ] **Step 2: Verify syntax**

Run: `D:\il\env\Scripts\python.exe -B -c "import ast; ast.parse(open('model/step6_train/terrains/T3_slope_30.py').read()); print('syntax ok')"`
Expected: `syntax ok`

- [ ] **Step 3: Commit**

```bash
git add model/step6_train/terrains/T3_slope_30.py
git commit -m "feat(terrains): add T3 30-degree slope terrain config"
```

---

### Task 5: Create T4_stairs.py

**Files:**
- Create: `yushu_robot/model/step6_train/terrains/T4_stairs.py`

- [ ] **Step 1: Create the T4 stairs terrain file**

```python
"""T4: Pyramid Stairs Terrain (step height 0.05-0.15m, step width 0.3m)."""

from isaaclab.terrains import TerrainGeneratorCfg
from isaaclab.terrains.height_field import HfPyramidStairsTerrainCfg

TERRAIN_NAME = "T4_stairs"

TERRAIN_CFG = TerrainGeneratorCfg(
    size=(8.0, 8.0),
    border_width=20.0,
    num_rows=10,
    num_cols=1,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    curriculum=True,
    sub_terrains={
        "stairs": HfPyramidStairsTerrainCfg(
            proportion=1.0,
            step_height_range=(0.05, 0.15),
            step_width=0.3,
            platform_width=1.0,
        ),
    },
)
```

- [ ] **Step 2: Verify syntax**

Run: `D:\il\env\Scripts\python.exe -B -c "import ast; ast.parse(open('model/step6_train/terrains/T4_stairs.py').read()); print('syntax ok')"`
Expected: `syntax ok`

- [ ] **Step 3: Commit**

```bash
git add model/step6_train/terrains/T4_stairs.py
git commit -m "feat(terrains): add T4 pyramid stairs terrain config"
```

---

### Task 6: Create T5_wave.py

**Files:**
- Create: `yushu_robot/model/step6_train/terrains/T5_wave.py`

- [ ] **Step 1: Create the T5 wave terrain file**

```python
"""T5: Irregular Wave Terrain (amplitude 0.02-0.08m, 2 waves)."""

from isaaclab.terrains import TerrainGeneratorCfg
from isaaclab.terrains.height_field import HfWaveTerrainCfg

TERRAIN_NAME = "T5_wave"

TERRAIN_CFG = TerrainGeneratorCfg(
    size=(8.0, 8.0),
    border_width=20.0,
    num_rows=10,
    num_cols=1,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    curriculum=True,
    sub_terrains={
        "wave": HfWaveTerrainCfg(
            proportion=1.0,
            amplitude_range=(0.02, 0.08),
            num_waves=2,
        ),
    },
)
```

- [ ] **Step 2: Verify syntax**

Run: `D:\il\env\Scripts\python.exe -B -c "import ast; ast.parse(open('model/step6_train/terrains/T5_wave.py').read()); print('syntax ok')"`
Expected: `syntax ok`

- [ ] **Step 3: Commit**

```bash
git add model/step6_train/terrains/T5_wave.py
git commit -m "feat(terrains): add T5 irregular wave terrain config"
```

---

### Task 7: Create __init__.py with TERRAIN_REGISTRY

**Files:**
- Create: `yushu_robot/model/step6_train/terrains/__init__.py`

- [ ] **Step 1: Create __init__.py**

```python
"""G1 AHC terrain configurations for Phase 1 training."""

from .T0_plane import TERRAIN_CFG as T0_CFG, TERRAIN_NAME as T0_NAME
from .T1_slope_10 import TERRAIN_CFG as T1_CFG, TERRAIN_NAME as T1_NAME
from .T2_slope_20 import TERRAIN_CFG as T2_CFG, TERRAIN_NAME as T2_NAME
from .T3_slope_30 import TERRAIN_CFG as T3_CFG, TERRAIN_NAME as T3_NAME
from .T4_stairs import TERRAIN_CFG as T4_CFG, TERRAIN_NAME as T4_NAME
from .T5_wave import TERRAIN_CFG as T5_CFG, TERRAIN_NAME as T5_NAME

TERRAIN_REGISTRY = {
    "T0": T0_CFG,
    "T1": T1_CFG,
    "T2": T2_CFG,
    "T3": T3_CFG,
    "T4": T4_CFG,
    "T5": T5_CFG,
}

__all__ = [
    "T0_CFG", "T0_NAME",
    "T1_CFG", "T1_NAME",
    "T2_CFG", "T2_NAME",
    "T3_CFG", "T3_NAME",
    "T4_CFG", "T4_NAME",
    "T5_CFG", "T5_NAME",
    "TERRAIN_REGISTRY",
]
```

- [ ] **Step 2: Verify syntax**

Run: `D:\il\env\Scripts\python.exe -B -c "import ast; ast.parse(open('model/step6_train/terrains/__init__.py').read()); print('syntax ok')"`
Expected: `syntax ok`

- [ ] **Step 3: Commit**

```bash
git add model/step6_train/terrains/__init__.py
git commit -m "feat(terrains): add __init__.py with TERRAIN_REGISTRY"
```

---

### Task 8: Create test_terrains.py

**Files:**
- Create: `yushu_robot/model/step6_train/terrains/test_terrains.py`

- [ ] **Step 1: Create the shared test runner script**

```python
"""Shared test script: place G1 robot on a selected terrain and run simulation."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# -- Path bootstrap (same pattern as step4/step5) -------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILD_ROBOT_MODEL_DIR = PROJECT_ROOT / "model" / "build_robot_model"
STEP3_DIR = PROJECT_ROOT / "model" / "step3_robot_cfg"
TERRAINS_DIR = PROJECT_ROOT / "model" / "step6_train" / "terrains"
for import_path in (BUILD_ROBOT_MODEL_DIR, STEP3_DIR, TERRAINS_DIR):
    import_path_str = str(import_path)
    if import_path_str not in sys.path:
        sys.path.insert(0, import_path_str)

from robot_asset import get_isaaclab_source_paths
from g1_local_cfg import G1_LOCAL_CFG
from terrains import TERRAIN_REGISTRY

DEFAULT_NUM_ENVS = 1
DEFAULT_MAX_STEPS = 0
DEFAULT_ENV_SPACING = 2.5
ROBOT_PRIM_PATH = "{ENV_REGEX_NS}/Robot"
VALID_TERRAINS = list(TERRAIN_REGISTRY.keys())


def bootstrap_isaaclab_paths() -> None:
    """Make local IsaacLab source packages importable from this project script."""
    for source_path in reversed(get_isaaclab_source_paths()):
        source_path_str = str(source_path)
        if source_path_str not in sys.path:
            sys.path.insert(0, source_path_str)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments and IsaacLab app launcher arguments."""
    from isaaclab.app import AppLauncher

    parser = argparse.ArgumentParser(description="Test G1 robot on a selected terrain.")
    parser.add_argument(
        "--terrain",
        type=str,
        default="T0",
        choices=VALID_TERRAINS,
        help=f"Terrain type to test. Choices: {VALID_TERRAINS}",
    )
    parser.add_argument("--num_envs", type=int, default=DEFAULT_NUM_ENVS, help="Number of environments.")
    parser.add_argument("--env_spacing", type=float, default=DEFAULT_ENV_SPACING, help="Spacing between environments.")
    parser.add_argument(
        "--max_steps",
        type=int,
        default=DEFAULT_MAX_STEPS,
        help="Number of environment steps before exiting. Use 0 for an infinite run.",
    )
    parser.add_argument(
        "--graceful_close",
        action="store_true",
        help="Use SimulationApp.close() after a bounded run. By default, bounded runs exit directly.",
    )
    AppLauncher.add_app_launcher_args(parser)
    return parser.parse_args()


def create_terrain_test_env_cfg(terrain_key: str, num_envs: int, env_spacing: float):
    """Create a ManagerBasedEnvCfg with terrain and G1 robot."""
    bootstrap_isaaclab_paths()

    import isaaclab.envs.mdp as mdp
    import isaaclab.sim as sim_utils
    from isaaclab.assets import ArticulationCfg, AssetBaseCfg
    from isaaclab.envs import ManagerBasedEnvCfg
    from isaaclab.managers import EventTermCfg as EventTerm
    from isaaclab.managers import ObservationGroupCfg as ObsGroup
    from isaaclab.managers import ObservationTermCfg as ObsTerm
    from isaaclab.scene import InteractiveSceneCfg
    from isaaclab.terrains import TerrainImporterCfg
    from isaaclab.utils import configclass

    terrain_cfg = TERRAIN_REGISTRY[terrain_key]

    @configclass
    class TerrainTestSceneCfg(InteractiveSceneCfg):
        """Scene config: terrain + dome light + G1 robot."""

        terrain = TerrainImporterCfg(
            prim_path="/World/ground",
            terrain_type="generator",
            terrain_generator=terrain_cfg,
            max_init_terrain_level=5,
            collision_group=-1,
            physics_material=sim_utils.RigidBodyMaterialCfg(
                friction_combine_mode="multiply",
                restitution_combine_mode="multiply",
                static_friction=1.0,
                dynamic_friction=1.0,
            ),
        )

        dome_light = AssetBaseCfg(
            prim_path="/World/Light",
            spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75)),
        )

        robot: ArticulationCfg = G1_LOCAL_CFG.replace(prim_path=ROBOT_PRIM_PATH)

    @configclass
    class ActionsCfg:
        """Action specifications — joint position over all 29 joints."""

        joint_pos = mdp.JointPositionActionCfg(
            asset_name="robot",
            joint_names=[".*"],
            scale=0.25,
            use_default_offset=True,
        )

    @configclass
    class ObservationsCfg:
        """Observation specifications."""

        @configclass
        class PolicyCfg(ObsGroup):
            """Policy observation group."""

            base_ang_vel = ObsTerm(func=mdp.base_ang_vel)
            projected_gravity = ObsTerm(func=mdp.projected_gravity)
            joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel)
            joint_vel_rel = ObsTerm(func=mdp.joint_vel_rel)
            last_action = ObsTerm(func=mdp.last_action)

            def __post_init__(self) -> None:
                self.enable_corruption = False
                self.concatenate_terms = True

        policy: PolicyCfg = PolicyCfg()

    @configclass
    class EventCfg:
        """Reset event specifications."""

        reset_base = EventTerm(
            func=mdp.reset_root_state_uniform,
            mode="reset",
            params={
                "pose_range": {"x": (-0.05, 0.05), "y": (-0.05, 0.05), "yaw": (-0.05, 0.05)},
                "velocity_range": {},
            },
        )

        reset_joints = EventTerm(
            func=mdp.reset_joints_by_offset,
            mode="reset",
            params={
                "position_range": (0.0, 0.0),
                "velocity_range": (0.0, 0.0),
            },
        )

    @configclass
    class TerrainTestEnvCfg(ManagerBasedEnvCfg):
        """Manager-Based environment config for terrain testing."""

        scene = TerrainTestSceneCfg(num_envs=num_envs, env_spacing=env_spacing)
        observations = ObservationsCfg()
        actions = ActionsCfg()
        events = EventCfg()

        def __post_init__(self) -> None:
            self.viewer.eye = [2.5, -3.0, 2.0]
            self.viewer.lookat = [0.0, 0.0, 0.8]
            self.decimation = 4
            self.sim.dt = 0.005
            self.sim.render_interval = self.decimation

    return TerrainTestEnvCfg()


def run_environment(env, simulation_app, max_steps: int) -> None:
    """Run zero actions through the environment — robot stands still on terrain."""
    import torch

    count = 0
    env.reset()
    terrain_key = env.cfg.scene.terrain.terrain_generator  # not directly accessible
    print(f"[INFO]: Terrain test environment reset complete.")

    while simulation_app.is_running() and (max_steps <= 0 or count < max_steps):
        with torch.inference_mode():
            actions = torch.zeros_like(env.action_manager.action)
            obs, _ = env.step(actions)
            if count == 0:
                print(f"[INFO]: Policy observation shape: {tuple(obs['policy'].shape)}")
                print(f"[INFO]: Action shape: {tuple(actions.shape)}")
            # Print robot height periodically
            if count % 50 == 0:
                root_pos = env.scene["robot"].data.root_pos_w
                avg_height = root_pos[:, 2].mean().item()
                print(f"[INFO]: Step {count} — avg robot height: {avg_height:.4f}m")
            count += 1

    print(f"[INFO]: Completed {count} steps.")


def main(args: argparse.Namespace, simulation_app) -> None:
    """Run terrain test."""
    from isaaclab.envs import ManagerBasedEnv

    print(f"[INFO]: Testing terrain: {args.terrain}")
    env_cfg = create_terrain_test_env_cfg(
        terrain_key=args.terrain,
        num_envs=args.num_envs,
        env_spacing=args.env_spacing,
    )
    env_cfg.sim.device = args.device
    env = ManagerBasedEnv(cfg=env_cfg)
    try:
        run_environment(env, simulation_app, args.max_steps)
    finally:
        env.close()


if __name__ == "__main__":
    args_cli = parse_args()

    from isaaclab.app import AppLauncher

    app_launcher = AppLauncher(args_cli)
    simulation_app = app_launcher.app
    main(args_cli, simulation_app)
    if args_cli.max_steps > 0 and not args_cli.graceful_close:
        print(f"[INFO]: Terrain test ({args_cli.terrain}) bounded run complete.", flush=True)
        os._exit(0)
    simulation_app.close()
```

- [ ] **Step 2: Verify syntax**

Run: `D:\il\env\Scripts\python.exe -B -c "import ast; ast.parse(open('model/step6_train/terrains/test_terrains.py').read()); print('syntax ok')"`
Expected: `syntax ok`

- [ ] **Step 3: Commit**

```bash
git add model/step6_train/terrains/test_terrains.py
git commit -m "feat(terrains): add shared test script with --terrain CLI param"
```

---

### Task 9: Run headless smoke tests for all 6 terrains

**Files:**
- None (verification only)

- [ ] **Step 1: Test T0 (flat plane)**

Run: `D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T0 --headless --max_steps 2`
Expected: Script starts, prints observation/action shapes, prints robot height, exits after 2 steps.

- [ ] **Step 2: Test T1 (10° slope)**

Run: `D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T1 --headless --max_steps 2`
Expected: Same as T1.

- [ ] **Step 3: Test T2 (20° slope)**

Run: `D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T2 --headless --max_steps 2`
Expected: Same pattern.

- [ ] **Step 4: Test T3 (30° slope)**

Run: `D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T3 --headless --max_steps 2`
Expected: Same pattern.

- [ ] **Step 5: Test T4 (stairs)**

Run: `D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T4 --headless --max_steps 2`
Expected: Same pattern.

- [ ] **Step 6: Test T5 (wave)**

Run: `D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T5 --headless --max_steps 2`
Expected: Same pattern.

- [ ] **Step 7: Final commit with all terrain files**

```bash
git add model/step6_train/terrains/
git commit -m "feat(terrains): complete P1.1 terrain system with 6 terrain types and test script"
```

---

## Verification Checklist

After all tasks complete:

- [ ] All 6 terrain files exist under `model/step6_train/terrains/`
- [ ] `__init__.py` exports `TERRAIN_REGISTRY` with keys T0-T5
- [ ] `test_terrains.py` runs successfully with `--terrain T0` through `--terrain T5` in headless mode
- [ ] Each terrain file can be imported independently
- [ ] Robot spawns on terrain and prints height info during simulation
- [ ] No residual Python processes after bounded runs
