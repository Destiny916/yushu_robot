"""Step 5 sensor configuration for the local G1 Manager-Based environment."""

from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILD_ROBOT_MODEL_DIR = PROJECT_ROOT / "model" / "build_robot_model"
STEP4_DIR = PROJECT_ROOT / "model" / "step4_manager_env"
for import_path in (BUILD_ROBOT_MODEL_DIR, STEP4_DIR):
    import_path_str = str(import_path)
    if import_path_str not in sys.path:
        sys.path.insert(0, import_path_str)

from robot_asset import get_isaaclab_source_paths
from stand_env_cfg import DEFAULT_ENV_SPACING, DEFAULT_MAX_STEPS, DEFAULT_NUM_ENVS, create_g1_stand_env_cfg


CONTACT_SENSOR_NAME = "contact_forces"
CONTACT_SENSOR_PRIM_PATH = "{ENV_REGEX_NS}/Robot/.*ankle_roll_link"
CONTACT_SENSOR_HISTORY_LENGTH = 6


def bootstrap_isaaclab_paths() -> None:
    """Make local IsaacLab source packages importable from this project script."""
    for source_path in reversed(get_isaaclab_source_paths()):
        source_path_str = str(source_path)
        if source_path_str not in sys.path:
            sys.path.insert(0, source_path_str)


def create_g1_sensor_env_cfg(num_envs: int = DEFAULT_NUM_ENVS, env_spacing: float = DEFAULT_ENV_SPACING):
    """Create the Step 4 environment config with ankle contact sensors attached."""
    bootstrap_isaaclab_paths()

    from isaaclab.sensors import ContactSensorCfg

    env_cfg = create_g1_stand_env_cfg(num_envs=num_envs, env_spacing=env_spacing)
    env_cfg.scene.robot.spawn.activate_contact_sensors = True
    setattr(
        env_cfg.scene,
        CONTACT_SENSOR_NAME,
        ContactSensorCfg(
            prim_path=CONTACT_SENSOR_PRIM_PATH,
            update_period=env_cfg.sim.dt,
            history_length=CONTACT_SENSOR_HISTORY_LENGTH,
            debug_vis=False,
        ),
    )
    return env_cfg
