"""RSL-RL PPO config for Phase 1 G1 standing training."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BUILD_ROBOT_MODEL_DIR = PROJECT_ROOT / "model" / "build_robot_model"
if str(BUILD_ROBOT_MODEL_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_ROBOT_MODEL_DIR))

from robot_asset import get_isaaclab_source_paths


@dataclass
class DictConfig:
    """Small config object with an IsaacLab-style ``to_dict`` method."""

    def to_dict(self) -> dict:
        """Recursively convert this config into plain Python containers."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, DictConfig):
                result[key] = value.to_dict()
            elif isinstance(value, dict):
                result[key] = {
                    dict_key: dict_value.to_dict() if isinstance(dict_value, DictConfig) else dict_value
                    for dict_key, dict_value in value.items()
                }
            elif isinstance(value, list):
                result[key] = [item.to_dict() if isinstance(item, DictConfig) else item for item in value]
            else:
                result[key] = value
        return result


@dataclass
class PpoPolicyCfg(DictConfig):
    """Actor-critic network config consumed by RSL-RL."""

    class_name: str = "ActorCritic"
    init_noise_std: float = 1.0
    noise_std_type: str = "scalar"
    state_dependent_std: bool = False
    actor_obs_normalization: bool = True
    critic_obs_normalization: bool = True
    actor_hidden_dims: list[int] = field(default_factory=lambda: [512, 256, 128])
    critic_hidden_dims: list[int] = field(default_factory=lambda: [512, 256, 128])
    activation: str = "elu"


@dataclass
class PpoAlgorithmCfg(DictConfig):
    """PPO algorithm config consumed by RSL-RL."""

    class_name: str = "PPO"
    value_loss_coef: float = 1.0
    use_clipped_value_loss: bool = True
    clip_param: float = 0.2
    entropy_coef: float = 0.01
    num_learning_epochs: int = 5
    num_mini_batches: int = 4
    learning_rate: float = 1.0e-3
    schedule: str = "adaptive"
    gamma: float = 0.99
    lam: float = 0.95
    desired_kl: float = 0.01
    max_grad_norm: float = 1.0
    normalize_advantage_per_mini_batch: bool = False
    rnd_cfg: None = None
    symmetry_cfg: None = None


@dataclass
class G1StandPPORunnerCfg(DictConfig):
    """On-policy runner config for standing PPO."""

    seed: int = 42
    device: str = "cuda:0"
    num_steps_per_env: int = 24
    max_iterations: int = 1500
    obs_groups: dict[str, list[str]] = field(
        default_factory=lambda: {"policy": ["policy"], "critic": ["policy"]}
    )
    clip_actions: float = 100.0
    save_interval: int = 50
    experiment_name: str = "g1_stand"
    run_name: str = ""
    logger: str = "tensorboard"
    neptune_project: str = "isaaclab"
    wandb_project: str = "isaaclab"
    resume: bool = False
    load_run: str = ".*"
    load_checkpoint: str = "model_*.pt"
    class_name: str = "OnPolicyRunner"
    policy: PpoPolicyCfg = field(default_factory=PpoPolicyCfg)
    algorithm: PpoAlgorithmCfg = field(default_factory=PpoAlgorithmCfg)


def bootstrap_isaaclab_paths() -> None:
    """Make local IsaacLab source packages importable from this project script."""
    for source_path in reversed(get_isaaclab_source_paths()):
        source_path_str = str(source_path)
        if source_path_str not in sys.path:
            sys.path.insert(0, source_path_str)


def create_g1_stand_ppo_runner_cfg(
    *,
    max_iterations: int | None = None,
    save_interval: int | None = None,
    seed: int | None = None,
    device: str | None = None,
    experiment_name: str | None = None,
    run_name: str | None = None,
    resume: bool = False,
    load_run: str | None = None,
    checkpoint: str | None = None,
):
    """Create an RSL-RL PPO runner config for standing, with optional resume overrides."""
    bootstrap_isaaclab_paths()

    cfg = G1StandPPORunnerCfg()
    if max_iterations is not None:
        cfg.max_iterations = max_iterations
    if save_interval is not None:
        cfg.save_interval = save_interval
    if seed is not None:
        cfg.seed = seed
    if device is not None:
        cfg.device = device
    if experiment_name is not None:
        cfg.experiment_name = experiment_name
    if run_name is not None:
        cfg.run_name = run_name
    cfg.resume = resume
    if load_run is not None:
        cfg.load_run = load_run
    if checkpoint is not None:
        cfg.load_checkpoint = checkpoint
    return cfg
