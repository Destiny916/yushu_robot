"""Step 2: load the generated G1 USD through InteractiveSceneCfg.

This script follows `scripts/tutorials/02_scene/create_scene.py` and keeps the
robot asset configuration from Step 1.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILD_ROBOT_MODEL_DIR = PROJECT_ROOT / "model" / "build_robot_model"
STEP3_DIR = PROJECT_ROOT / "model" / "step3_robot_cfg"
for import_path in (BUILD_ROBOT_MODEL_DIR, STEP3_DIR):
    import_path_str = str(import_path)
    if import_path_str not in sys.path:
        sys.path.insert(0, import_path_str)

from robot_asset import get_default_usd_path, get_isaaclab_source_paths
from g1_local_cfg import G1_LOCAL_CFG


DEFAULT_NUM_ENVS = 1
DEFAULT_MAX_STEPS = 0
ROBOT_PRIM_PATH = "{ENV_REGEX_NS}/Robot"


def bootstrap_isaaclab_paths() -> None:
    """Make local IsaacLab source packages importable from this project script."""
    for source_path in reversed(get_isaaclab_source_paths()):
        source_path_str = str(source_path)
        if source_path_str not in sys.path:
            sys.path.insert(0, source_path_str)


def get_robot_usd_path() -> Path:
    """Return the global generated USD used by the scene."""
    return get_default_usd_path()


def create_g1_scene_cfg_class():
    """Create the InteractiveSceneCfg class for the local G1 robot."""
    bootstrap_isaaclab_paths()

    import isaaclab.sim as sim_utils
    from isaaclab.assets import ArticulationCfg, AssetBaseCfg
    from isaaclab.scene import InteractiveSceneCfg
    from isaaclab.utils import configclass

    @configclass
    class G1SceneCfg(InteractiveSceneCfg):
        """Configuration for the local G1 scene."""

        ground = AssetBaseCfg(prim_path="/World/defaultGroundPlane", spawn=sim_utils.GroundPlaneCfg())

        dome_light = AssetBaseCfg(
            prim_path="/World/Light",
            spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75)),
        )

        robot: ArticulationCfg = G1_LOCAL_CFG.replace(prim_path=ROBOT_PRIM_PATH)

    return G1SceneCfg


def parse_args() -> argparse.Namespace:
    """Parse Step 2 CLI arguments and IsaacLab app launcher arguments."""
    bootstrap_isaaclab_paths()
    from isaaclab.app import AppLauncher

    parser = argparse.ArgumentParser(description="Step 2: load the local G1 with InteractiveSceneCfg.")
    parser.add_argument("--num_envs", type=int, default=DEFAULT_NUM_ENVS, help="Number of scene environments.")
    parser.add_argument("--env_spacing", type=float, default=1.5, help="Spacing between scene environments.")
    parser.add_argument(
        "--max_steps",
        type=int,
        default=DEFAULT_MAX_STEPS,
        help="Number of simulation steps before exiting. Use 0 for an infinite run.",
    )
    parser.add_argument(
        "--random_effort_scale",
        type=float,
        default=1.0,
        help="Scale for random joint efforts applied each simulation step.",
    )
    parser.add_argument(
        "--graceful_close",
        action="store_true",
        help="Use SimulationApp.close() after a bounded run. By default, bounded runs exit directly to avoid Kit stage-close hangs.",
    )
    AppLauncher.add_app_launcher_args(parser)
    return parser.parse_args()


def run_simulator(sim, simulation_app, scene, max_steps: int, random_effort_scale: float) -> None:
    """Run the InteractiveScene simulation loop."""
    bootstrap_isaaclab_paths()

    import torch

    robot = scene["robot"]
    sim_dt = sim.get_physics_dt()
    count = 0

    while simulation_app.is_running() and (max_steps <= 0 or count < max_steps):
        if count % 500 == 0:
            root_state = robot.data.default_root_state.clone()
            root_state[:, :3] += scene.env_origins
            robot.write_root_pose_to_sim(root_state[:, :7])
            robot.write_root_velocity_to_sim(root_state[:, 7:])
            robot.write_joint_state_to_sim(robot.data.default_joint_pos.clone(), robot.data.default_joint_vel.clone())
            scene.reset()
            print("[INFO]: Resetting G1 scene state...")

        efforts = torch.randn_like(robot.data.joint_pos) * random_effort_scale
        robot.set_joint_effort_target(efforts)
        scene.write_data_to_sim()
        sim.step()
        scene.update(sim_dt)
        count += 1


def main(args: argparse.Namespace, simulation_app) -> None:
    """Run Step 2."""
    bootstrap_isaaclab_paths()

    import isaaclab.sim as sim_utils
    from isaaclab.scene import InteractiveScene
    from isaaclab.sim import SimulationContext

    sim_cfg = sim_utils.SimulationCfg(device=args.device)
    sim = SimulationContext(sim_cfg)
    sim.set_camera_view([2.5, -3.0, 2.0], [0.0, 0.0, 0.8])

    scene_cfg_class = create_g1_scene_cfg_class()
    scene = InteractiveScene(scene_cfg_class(num_envs=args.num_envs, env_spacing=args.env_spacing))
    sim.reset()
    print("[INFO]: Step 2 setup complete.")
    run_simulator(sim, simulation_app, scene, args.max_steps, args.random_effort_scale)


if __name__ == "__main__":
    args_cli = parse_args()

    from isaaclab.app import AppLauncher

    app_launcher = AppLauncher(args_cli)
    simulation_app = app_launcher.app
    main(args_cli, simulation_app)
    if args_cli.max_steps > 0 and not args_cli.graceful_close:
        print("[INFO]: Step 2 bounded run complete.", flush=True)
        os._exit(0)
    simulation_app.close()
