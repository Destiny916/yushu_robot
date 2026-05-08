"""Step 1: load the generated G1 USD with the manual Articulation API.

This script intentionally uses the low-level pattern from
`scripts/tutorials/01_assets/run_articulation.py` before later steps move to
InteractiveScene and Manager-Based environments.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILD_ROBOT_MODEL_DIR = PROJECT_ROOT / "model" / "build_robot_model"
if str(BUILD_ROBOT_MODEL_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_ROBOT_MODEL_DIR))

from robot_asset import get_default_usd_path, get_isaaclab_source_paths


DEFAULT_NUM_ENVS = 1
DEFAULT_MAX_STEPS = 0


def bootstrap_isaaclab_paths() -> None:
    """Make local IsaacLab source packages importable from this project script."""
    for source_path in reversed(get_isaaclab_source_paths()):
        source_path_str = str(source_path)
        if source_path_str not in sys.path:
            sys.path.insert(0, source_path_str)


def get_robot_usd_path() -> Path:
    """Return the global generated USD used by all later steps."""
    return get_default_usd_path()


def make_scene_origins(num_envs: int, spacing: float) -> list[tuple[float, float, float]]:
    """Create simple x-axis origins for manually spawned robot instances."""
    return [(float(index) * spacing, 0.0, 0.0) for index in range(num_envs)]


def build_g1_articulation_cfg(prim_path: str = "/World/Origin.*/Robot"):
    """Build the manual ArticulationCfg for the locally generated G1 USD."""
    bootstrap_isaaclab_paths()

    import isaaclab.sim as sim_utils
    from isaaclab.actuators import ImplicitActuatorCfg
    from isaaclab.assets import ArticulationCfg

    usd_path = get_robot_usd_path()
    if not usd_path.exists():
        raise FileNotFoundError(
            f"Generated robot USD not found: {usd_path}\n"
            "Run: D:\\il\\env\\Scripts\\python.exe model\\build_robot_model\\build_g1_from_urdf.py --headless"
        )

    return ArticulationCfg(
        prim_path=prim_path,
        spawn=sim_utils.UsdFileCfg(
            usd_path=str(usd_path),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(max_depenetration_velocity=5.0),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=True,
                solver_position_iteration_count=4,
                solver_velocity_iteration_count=0,
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.78),
            joint_pos={".*": 0.0},
            joint_vel={".*": 0.0},
        ),
        actuators={
            "legs": ImplicitActuatorCfg(
                joint_names_expr=[".*_hip_.*", ".*_knee_.*", ".*_ankle_.*"],
                effort_limit_sim=200.0,
                stiffness=200.0,
                damping=10.0,
            ),
            "waist": ImplicitActuatorCfg(
                joint_names_expr=["waist_.*"],
                effort_limit_sim=100.0,
                stiffness=200.0,
                damping=10.0,
            ),
            "arms": ImplicitActuatorCfg(
                joint_names_expr=[".*_shoulder_.*", ".*_elbow_.*", ".*_wrist_.*"],
                effort_limit_sim=50.0,
                stiffness=100.0,
                damping=5.0,
            ),
        },
    )


def parse_args() -> argparse.Namespace:
    """Parse Step 1 CLI arguments and IsaacLab app launcher arguments."""
    bootstrap_isaaclab_paths()
    from isaaclab.app import AppLauncher

    parser = argparse.ArgumentParser(description="Step 1: manually load the local G1 articulation.")
    parser.add_argument(
        "--num_envs",
        type=int,
        default=DEFAULT_NUM_ENVS,
        help="Number of manually spawned robot instances.",
    )
    parser.add_argument("--env_spacing", type=float, default=1.5, help="Spacing between manually spawned origins.")
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


def design_scene(num_envs: int, env_spacing: float):
    """Spawn ground, lights, origins, and the G1 articulation."""
    bootstrap_isaaclab_paths()

    import isaaclab.sim as sim_utils
    from isaaclab.assets import Articulation

    ground_cfg = sim_utils.GroundPlaneCfg()
    ground_cfg.func("/World/defaultGroundPlane", ground_cfg)

    light_cfg = sim_utils.DomeLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75))
    light_cfg.func("/World/Light", light_cfg)

    origins = make_scene_origins(num_envs=num_envs, spacing=env_spacing)
    for index, origin in enumerate(origins):
        sim_utils.create_prim(f"/World/Origin{index + 1}", "Xform", translation=origin)

    robot = Articulation(cfg=build_g1_articulation_cfg())
    return {"robot": robot}, origins


def run_simulator(sim, simulation_app, entities, origins, max_steps: int, random_effort_scale: float) -> None:
    """Run the manual articulation simulation loop."""
    bootstrap_isaaclab_paths()

    import torch

    robot = entities["robot"]
    sim_dt = sim.get_physics_dt()
    origins_tensor = torch.tensor(origins, device=sim.device)
    count = 0

    while simulation_app.is_running() and (max_steps <= 0 or count < max_steps):
        if count % 500 == 0:
            root_state = robot.data.default_root_state.clone()
            root_state[:, :3] += origins_tensor
            robot.write_root_pose_to_sim(root_state[:, :7])
            robot.write_root_velocity_to_sim(root_state[:, 7:])
            robot.write_joint_state_to_sim(robot.data.default_joint_pos.clone(), robot.data.default_joint_vel.clone())
            robot.reset()
            print("[INFO]: Resetting G1 state...")

        efforts = torch.randn_like(robot.data.joint_pos) * random_effort_scale
        robot.set_joint_effort_target(efforts)
        robot.write_data_to_sim()
        sim.step()
        robot.update(sim_dt)
        count += 1


def main(args: argparse.Namespace, simulation_app) -> None:
    """Run Step 1."""
    import isaaclab.sim as sim_utils
    from isaaclab.sim import SimulationContext

    sim_cfg = sim_utils.SimulationCfg(device=args.device)
    sim = SimulationContext(sim_cfg)
    sim.set_camera_view([2.5, -3.0, 2.0], [0.0, 0.0, 0.8])

    entities, origins = design_scene(args.num_envs, args.env_spacing)
    sim.reset()
    print("[INFO]: Step 1 setup complete.")
    run_simulator(sim, simulation_app, entities, origins, args.max_steps, args.random_effort_scale)


if __name__ == "__main__":
    args_cli = parse_args()

    from isaaclab.app import AppLauncher

    app_launcher = AppLauncher(args_cli)
    simulation_app = app_launcher.app
    main(args_cli, simulation_app)
    if args_cli.max_steps > 0 and not args_cli.graceful_close:
        print("[INFO]: Step 1 bounded run complete.", flush=True)
        os._exit(0)
    simulation_app.close()
