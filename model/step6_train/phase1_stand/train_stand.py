"""Train the Phase 1 G1 standing PPO policy with RSL-RL."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import shutil
import sys
import time

from stand_env_cfg import DEFAULT_ENV_SPACING, DEFAULT_NUM_ENVS, DEFAULT_TERRAIN
from stand_env_cfg import create_g1_stand_no_external_force_env_cfg
from stand_ppo_cfg import create_g1_stand_ppo_runner_cfg


DEFAULT_LOG_ROOT = Path("logs") / "rsl_rl" / "g1_stand"
DEFAULT_LOAD_CHECKPOINT = "model_*.pt"
FINAL_CHECKPOINT_ALIAS = "checkpoint_stand.pt"
_ON_POLICY_RUNNER_CLS = None


def preload_rsl_rl() -> None:
    """Import RSL-RL before Isaac Sim starts to avoid a Windows tensordict access violation."""
    global _ON_POLICY_RUNNER_CLS
    if _ON_POLICY_RUNNER_CLS is not None:
        return

    from rsl_rl.runners import OnPolicyRunner

    _ON_POLICY_RUNNER_CLS = OnPolicyRunner


def parse_args() -> argparse.Namespace:
    """Parse standing PPO training arguments and IsaacLab app launcher arguments."""
    preload_rsl_rl()

    from isaaclab.app import AppLauncher

    parser = argparse.ArgumentParser(description="Train the local G1 standing PPO policy with RSL-RL.")
    parser.add_argument("--terrain", type=str, default=DEFAULT_TERRAIN, help="Terrain key: T0-T5.")
    parser.add_argument("--num_envs", type=int, default=DEFAULT_NUM_ENVS, help="Number of parallel environments.")
    parser.add_argument("--env_spacing", type=float, default=DEFAULT_ENV_SPACING, help="Spacing between environments.")
    parser.add_argument("--max_iterations", type=int, default=None, help="Override PPO training iterations.")
    parser.add_argument(
        "--save_interval",
        type=int,
        default=None,
        help="Override checkpoint save interval. Use 1 for smoke runs.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Training seed.")
    parser.add_argument("--run_name", type=str, default="", help="Optional suffix for the run directory.")
    parser.add_argument("--resume", action="store_true", default=False, help="Resume training from a checkpoint.")
    parser.add_argument("--load_run", type=str, default=".*", help="Run directory or regex to resume from.")
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=DEFAULT_LOAD_CHECKPOINT,
        help="Checkpoint filename or regex to resume from.",
    )
    parser.add_argument("--logger", type=str, default="tensorboard", choices=("tensorboard", "wandb", "neptune"))
    AppLauncher.add_app_launcher_args(parser)
    return parser.parse_args()


def resolve_resume_checkpoint(log_root_path: str | Path, load_run: str, checkpoint: str) -> str:
    """Resolve the checkpoint path for resume using IsaacLab's run/checkpoint matcher."""
    from isaaclab_tasks.utils import get_checkpoint_path

    return get_checkpoint_path(str(Path(log_root_path).resolve()), load_run, checkpoint)


def make_log_dir(log_root_path: Path, run_name: str) -> Path:
    """Create the timestamped log directory path for this training run."""
    log_dir_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if run_name:
        log_dir_name += f"_{run_name}"
    return log_root_path.resolve() / log_dir_name


def _checkpoint_sort_key(path: Path) -> tuple[int, str]:
    """Sort RSL-RL model checkpoints by numeric suffix when present."""
    match = re.search(r"model_(\d+)\.pt$", path.name)
    if match:
        return int(match.group(1)), path.name
    return -1, path.name


def copy_latest_checkpoint_alias(log_dir: str | Path) -> Path | None:
    """Copy the newest RSL-RL model checkpoint to the stable standing-policy alias."""
    log_dir = Path(log_dir)
    checkpoints = sorted(log_dir.glob("model_*.pt"), key=_checkpoint_sort_key)
    if not checkpoints:
        return None
    alias_path = log_dir / FINAL_CHECKPOINT_ALIAS
    shutil.copy2(checkpoints[-1], alias_path)
    return alias_path


def train(args: argparse.Namespace) -> Path:
    """Run RSL-RL training and return the log directory."""
    print("[INFO]: Entering G1 standing PPO train().", flush=True)
    import torch

    from isaaclab.envs import ManagerBasedRLEnv
    from isaaclab.utils.io import dump_yaml
    from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper

    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.deterministic = False
    torch.backends.cudnn.benchmark = False

    agent_cfg = create_g1_stand_ppo_runner_cfg(
        max_iterations=args.max_iterations,
        save_interval=args.save_interval,
        seed=args.seed,
        device=args.device,
        run_name=args.run_name,
        resume=args.resume,
        load_run=args.load_run,
        checkpoint=args.checkpoint,
    )
    agent_cfg.logger = args.logger

    env_cfg = create_g1_stand_no_external_force_env_cfg(
        terrain_key=args.terrain,
        num_envs=args.num_envs,
        env_spacing=args.env_spacing,
    )
    env_cfg.seed = agent_cfg.seed
    env_cfg.sim.device = args.device if args.device is not None else env_cfg.sim.device

    log_root_path = DEFAULT_LOG_ROOT.resolve()
    log_dir = make_log_dir(log_root_path, agent_cfg.run_name)
    env_cfg.log_dir = str(log_dir)

    resume_path = None
    if agent_cfg.resume:
        resume_path = resolve_resume_checkpoint(log_root_path, agent_cfg.load_run, agent_cfg.load_checkpoint)

    print(f"[INFO]: Logging experiment in directory: {log_dir}", flush=True)
    print(
        "[INFO]: Training config: "
        f"terrain={args.terrain}, num_envs={args.num_envs}, "
        f"max_iterations={agent_cfg.max_iterations}, save_interval={agent_cfg.save_interval}, "
        f"device={agent_cfg.device}",
        flush=True,
    )
    print("[INFO]: Creating ManagerBasedRLEnv.", flush=True)
    env = ManagerBasedRLEnv(cfg=env_cfg)
    try:
        print("[INFO]: Wrapping environment for RSL-RL.", flush=True)
        env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
        preload_rsl_rl()
        print("[INFO]: Creating OnPolicyRunner.", flush=True)
        runner = _ON_POLICY_RUNNER_CLS(env, agent_cfg.to_dict(), log_dir=str(log_dir), device=agent_cfg.device)
        runner.add_git_repo_to_log(__file__)
        if resume_path is not None:
            print(f"[INFO]: Loading model checkpoint from: {resume_path}", flush=True)
            runner.load(resume_path)

        dump_yaml(str(log_dir / "params" / "env.yaml"), env_cfg)
        dump_yaml(str(log_dir / "params" / "agent.yaml"), agent_cfg.to_dict())

        start_time = time.time()
        print("[INFO]: Starting RSL-RL PPO learning loop.", flush=True)
        runner.learn(num_learning_iterations=agent_cfg.max_iterations, init_at_random_ep_len=True)
        print("[INFO]: RSL-RL PPO learning loop finished.", flush=True)
        final_checkpoint = copy_latest_checkpoint_alias(log_dir)
        if final_checkpoint is not None:
            print(f"[INFO]: Final standing checkpoint alias: {final_checkpoint}", flush=True)
        else:
            print("[WARN]: No model_*.pt checkpoint was found to alias.", flush=True)
        print(f"[INFO]: Training time: {round(time.time() - start_time, 2)} seconds", flush=True)
        return log_dir
    finally:
        env.close()


if __name__ == "__main__":
    args_cli = parse_args()

    from isaaclab.app import AppLauncher

    app_launcher = AppLauncher(args_cli)
    simulation_app = app_launcher.app
    try:
        train(args_cli)
    except Exception as exc:
        print(f"[ERROR]: Standing PPO training failed: {exc!r}", flush=True)
        raise
    finally:
        simulation_app.close()
