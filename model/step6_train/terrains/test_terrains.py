"""Shared test script: place G1 robot on a selected terrain and run simulation."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# -- Path bootstrap (same pattern as step4/step5) -------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]
BUILD_ROBOT_MODEL_DIR = PROJECT_ROOT / "model" / "build_robot_model"
STEP3_DIR = PROJECT_ROOT / "model" / "step3_robot_cfg"
STEP6_DIR = PROJECT_ROOT / "model" / "step6_train"
for import_path in (BUILD_ROBOT_MODEL_DIR, STEP3_DIR, STEP6_DIR):
    import_path_str = str(import_path)
    if import_path_str not in sys.path:
        sys.path.insert(0, import_path_str)

from robot_asset import get_isaaclab_source_paths
from g1_local_cfg import G1_LOCAL_CFG
from terrains import TERRAIN_NAMES, get_terrain_cfg

DEFAULT_NUM_ENVS = 1
DEFAULT_MAX_STEPS = 0
DEFAULT_ENV_SPACING = 2.5
ROBOT_PRIM_PATH = "{ENV_REGEX_NS}/Robot"
VALID_TERRAINS = list(TERRAIN_NAMES.keys())


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

    terrain_cfg = get_terrain_cfg(terrain_key)

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
    print("[INFO]: Terrain test environment reset complete.")

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
