"""Play back a trained Phase 1 G1 standing PPO policy without training."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import time

from stand_env_cfg import DEFAULT_ENV_SPACING, DEFAULT_NUM_ENVS, DEFAULT_TERRAIN
from stand_env_cfg import create_g1_stand_no_external_force_env_cfg
from stand_ppo_cfg import create_g1_stand_ppo_runner_cfg


DEFAULT_LOG_ROOT = Path("logs") / "rsl_rl" / "g1_stand"
DEFAULT_PLAY_CHECKPOINT = "checkpoint_stand.pt"
DEFAULT_FALLBACK_CHECKPOINT = "model_*.pt"
DEFAULT_REPORT_INTERVAL = 100
PLAYBACK_ERROR_MESSAGE = "error"
_ON_POLICY_RUNNER_CLS = None


def preload_rsl_rl() -> None:
    """Import RSL-RL before Isaac Sim starts to avoid a Windows tensordict access violation."""
    global _ON_POLICY_RUNNER_CLS
    if _ON_POLICY_RUNNER_CLS is not None:
        return

    from rsl_rl.runners import OnPolicyRunner

    _ON_POLICY_RUNNER_CLS = OnPolicyRunner


def parse_args() -> argparse.Namespace:
    """Parse standing policy playback arguments and IsaacLab app launcher arguments."""
    preload_rsl_rl()

    from isaaclab.app import AppLauncher

    parser = argparse.ArgumentParser(description="Play a trained local G1 standing PPO policy without training.")
    parser.add_argument("--terrain", type=str, default=DEFAULT_TERRAIN, help="Terrain key: T0-T5.")
    parser.add_argument("--num_envs", type=int, default=DEFAULT_NUM_ENVS, help="Number of parallel environments.")
    parser.add_argument("--env_spacing", type=float, default=DEFAULT_ENV_SPACING, help="Spacing between environments.")
    parser.add_argument("--seed", type=int, default=42, help="Environment seed.")
    parser.add_argument(
        "--load_run",
        type=str,
        required=True,
        help="Run directory name, absolute run path, or regex under logs/rsl_rl/g1_stand.",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=DEFAULT_PLAY_CHECKPOINT,
        help="Checkpoint filename, absolute checkpoint path, or glob such as model_*.pt.",
    )
    parser.add_argument(
        "--max_steps",
        type=int,
        default=0,
        help="Number of policy steps before exiting. Use 0 to run until the viewer is closed.",
    )
    parser.add_argument(
        "--report_interval",
        type=int,
        default=DEFAULT_REPORT_INTERVAL,
        help="Print playback status every N policy steps. Use 0 to disable.",
    )
    AppLauncher.add_app_launcher_args(parser)
    return parser.parse_args()


def _checkpoint_sort_key(path: Path) -> tuple[int, str]:
    """Sort RSL-RL model checkpoints by numeric suffix when present."""
    match = re.search(r"model_(\d+)\.pt$", path.name)
    if match:
        return int(match.group(1)), path.name
    return -1, path.name


def is_policy_error(done_count: int) -> bool:
    """Return whether playback detected a policy failure/reset condition."""
    return done_count > 0


def _resolve_run_dir(log_root_path: Path, load_run: str) -> Path | None:
    """Resolve a concrete run directory if load_run names or points to one."""
    load_run_path = Path(load_run)
    if load_run_path.is_absolute() and load_run_path.is_dir():
        return load_run_path

    direct_run_path = log_root_path / load_run
    if direct_run_path.is_dir():
        return direct_run_path

    return None


def resolve_play_checkpoint(log_root_path: str | Path, load_run: str, checkpoint: str) -> Path:
    """Resolve the checkpoint used for policy playback."""
    log_root_path = Path(log_root_path).resolve()
    checkpoint_path = Path(checkpoint)
    if checkpoint_path.is_absolute():
        if checkpoint_path.is_file():
            return checkpoint_path
        raise FileNotFoundError(f"Checkpoint does not exist: {checkpoint_path}")

    run_dir = _resolve_run_dir(log_root_path, load_run)
    if run_dir is not None:
        if any(char in checkpoint for char in "*?[]"):
            checkpoints = sorted(run_dir.glob(checkpoint), key=_checkpoint_sort_key)
            if not checkpoints:
                raise FileNotFoundError(f"No checkpoints matching {checkpoint!r} in {run_dir}")
            return checkpoints[-1]

        candidate = run_dir / checkpoint
        if candidate.is_file():
            return candidate
        if checkpoint == DEFAULT_PLAY_CHECKPOINT:
            checkpoints = sorted(run_dir.glob(DEFAULT_FALLBACK_CHECKPOINT), key=_checkpoint_sort_key)
            if checkpoints:
                return checkpoints[-1]
        raise FileNotFoundError(f"Checkpoint does not exist: {candidate}")

    from isaaclab_tasks.utils import get_checkpoint_path

    return Path(get_checkpoint_path(str(log_root_path), load_run, checkpoint))


def play(args: argparse.Namespace, simulation_app) -> Path:
    """Load a trained policy checkpoint and run inference in the standing environment."""
    import torch

    from isaaclab.envs import ManagerBasedRLEnv
    from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper

    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True

    agent_cfg = create_g1_stand_ppo_runner_cfg(seed=args.seed, device=args.device)
    env_cfg = create_g1_stand_no_external_force_env_cfg(
        terrain_key=args.terrain,
        num_envs=args.num_envs,
        env_spacing=args.env_spacing,
    )
    env_cfg.seed = agent_cfg.seed
    env_cfg.sim.device = args.device if args.device is not None else env_cfg.sim.device

    log_root_path = DEFAULT_LOG_ROOT.resolve()
    checkpoint_path = resolve_play_checkpoint(log_root_path, args.load_run, args.checkpoint)

    print(f"[INFO]: Loading standing policy checkpoint: {checkpoint_path}", flush=True)
    print(
        "[INFO]: Playback config: "
        f"terrain={args.terrain}, num_envs={args.num_envs}, max_steps={args.max_steps}, device={agent_cfg.device}",
        flush=True,
    )
    print("[INFO]: Creating ManagerBasedRLEnv for policy playback.", flush=True)
    env = ManagerBasedRLEnv(cfg=env_cfg)
    try:
        env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
        preload_rsl_rl()
        runner = _ON_POLICY_RUNNER_CLS(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
        runner.load(str(checkpoint_path))
        policy = runner.get_inference_policy(device=agent_cfg.device)
        obs = env.get_observations().to(agent_cfg.device)

        step_count = 0
        start_time = time.time()
        detected_error = False
        print("[INFO]: Starting policy playback. Close the viewer or reach --max_steps to stop.", flush=True)
        while simulation_app.is_running() and (args.max_steps <= 0 or step_count < args.max_steps):
            with torch.inference_mode():
                actions = policy(obs)
                obs, rewards, dones, _ = env.step(actions)
                obs = obs.to(agent_cfg.device)

            step_count += 1
            done_count = int(dones.sum().item())
            if is_policy_error(done_count) and not detected_error:
                detected_error = True
                print(PLAYBACK_ERROR_MESSAGE, flush=True)

            if args.report_interval > 0 and step_count % args.report_interval == 0:
                root_height = env.unwrapped.scene["robot"].data.root_pos_w[:, 2].mean().item()
                print(
                    "[INFO]: Playback step "
                    f"{step_count}, mean_reward={rewards.mean().item():.4f}, "
                    f"done_count={done_count}, mean_root_height={root_height:.4f}",
                    flush=True,
                )

        print(f"[INFO]: Playback finished after {step_count} steps in {time.time() - start_time:.2f}s.", flush=True)
        return checkpoint_path
    finally:
        env.close()


if __name__ == "__main__":
    args_cli = parse_args()

    from isaaclab.app import AppLauncher

    app_launcher = AppLauncher(args_cli)
    simulation_app = app_launcher.app
    try:
        play(args_cli, simulation_app)
    except Exception as exc:
        print(PLAYBACK_ERROR_MESSAGE, flush=True)
        print(f"[ERROR]: Standing policy playback failed: {exc!r}", flush=True)
        raise
    finally:
        simulation_app.close()
