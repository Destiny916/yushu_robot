"""Step 4: run the local G1 in a minimal Manager-Based environment."""

from __future__ import annotations

import argparse
import os

from stand_env_cfg import DEFAULT_ENV_SPACING, DEFAULT_MAX_STEPS, DEFAULT_NUM_ENVS, create_g1_stand_env_cfg


def parse_args() -> argparse.Namespace:
    """Parse Step 4 CLI arguments and IsaacLab app launcher arguments."""
    from isaaclab.app import AppLauncher

    parser = argparse.ArgumentParser(description="Step 4: run the local G1 Manager-Based stand environment.")
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
        help="Use SimulationApp.close() after a bounded run. By default, bounded runs exit directly to avoid Kit stage-close hangs.",
    )
    AppLauncher.add_app_launcher_args(parser)
    return parser.parse_args()


def run_environment(env, simulation_app, max_steps: int) -> None:
    """Run random actions through the Manager-Based environment."""
    import torch

    count = 0
    env.reset()
    print("[INFO]: Step 4 environment reset complete.")

    while simulation_app.is_running() and (max_steps <= 0 or count < max_steps):
        with torch.inference_mode():
            actions = torch.randn_like(env.action_manager.action)
            obs, _ = env.step(actions)
            if count == 0:
                print(f"[INFO]: Policy observation shape: {tuple(obs['policy'].shape)}")
            count += 1


def main(args: argparse.Namespace, simulation_app) -> None:
    """Run Step 4."""
    from isaaclab.envs import ManagerBasedEnv

    env_cfg = create_g1_stand_env_cfg(num_envs=args.num_envs, env_spacing=args.env_spacing)
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
        print("[INFO]: Step 4 bounded run complete.", flush=True)
        os._exit(0)
    simulation_app.close()
