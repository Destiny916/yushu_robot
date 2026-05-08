"""Reusable IsaacLab ArticulationCfg for the local Unitree G1 29DOF asset."""

from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILD_ROBOT_MODEL_DIR = PROJECT_ROOT / "model" / "build_robot_model"
if str(BUILD_ROBOT_MODEL_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_ROBOT_MODEL_DIR))

from robot_asset import get_default_usd_path, get_isaaclab_source_paths


DEFAULT_PRIM_PATH = "/World/envs/env_.*/Robot"
ACTUATOR_GROUPS = {
    "legs": [
        ".*_hip_yaw_joint",
        ".*_hip_roll_joint",
        ".*_hip_pitch_joint",
        ".*_knee_joint",
    ],
    "feet": [".*_ankle_pitch_joint", ".*_ankle_roll_joint"],
    "waist": ["waist_.*_joint"],
    "arms": [
        ".*_shoulder_pitch_joint",
        ".*_shoulder_roll_joint",
        ".*_shoulder_yaw_joint",
        ".*_elbow_joint",
        ".*_wrist_.*_joint",
    ],
}


def bootstrap_isaaclab_paths() -> None:
    """Make local IsaacLab source packages importable from this project script."""
    for source_path in reversed(get_isaaclab_source_paths()):
        source_path_str = str(source_path)
        if source_path_str not in sys.path:
            sys.path.insert(0, source_path_str)


def get_robot_usd_path() -> Path:
    """Return the global generated USD used by the local G1 config."""
    return get_default_usd_path()


def make_g1_local_cfg(prim_path: str = DEFAULT_PRIM_PATH):
    """Create a local G1 29DOF ArticulationCfg with a replaceable prim path."""
    bootstrap_isaaclab_paths()

    import isaaclab.sim as sim_utils
    from isaaclab.actuators import DCMotorCfg, ImplicitActuatorCfg
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
            activate_contact_sensors=False,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                disable_gravity=False,
                retain_accelerations=False,
                linear_damping=0.0,
                angular_damping=0.0,
                max_linear_velocity=1000.0,
                max_angular_velocity=1000.0,
                max_depenetration_velocity=1.0,
            ),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=False,
                fix_root_link=False,
                solver_position_iteration_count=8,
                solver_velocity_iteration_count=4,
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.78),
            joint_pos={
                ".*_hip_pitch_joint": -0.10,
                ".*_knee_joint": 0.30,
                ".*_ankle_pitch_joint": -0.20,
                ".*_shoulder_pitch_joint": 0.20,
                ".*_elbow_joint": 0.30,
            },
            joint_vel={".*": 0.0},
        ),
        soft_joint_pos_limit_factor=0.9,
        actuators={
            "legs": DCMotorCfg(
                joint_names_expr=[
                    *ACTUATOR_GROUPS["legs"],
                ],
                effort_limit={
                    ".*_hip_yaw_joint": 88.0,
                    ".*_hip_roll_joint": 88.0,
                    ".*_hip_pitch_joint": 88.0,
                    ".*_knee_joint": 139.0,
                },
                velocity_limit={
                    ".*_hip_yaw_joint": 32.0,
                    ".*_hip_roll_joint": 32.0,
                    ".*_hip_pitch_joint": 32.0,
                    ".*_knee_joint": 20.0,
                },
                stiffness={
                    ".*_hip_yaw_joint": 100.0,
                    ".*_hip_roll_joint": 100.0,
                    ".*_hip_pitch_joint": 100.0,
                    ".*_knee_joint": 200.0,
                },
                damping={
                    ".*_hip_yaw_joint": 2.5,
                    ".*_hip_roll_joint": 2.5,
                    ".*_hip_pitch_joint": 2.5,
                    ".*_knee_joint": 5.0,
                },
                armature={
                    ".*_hip_.*": 0.03,
                    ".*_knee_joint": 0.03,
                },
                saturation_effort=180.0,
            ),
            "feet": DCMotorCfg(
                joint_names_expr=ACTUATOR_GROUPS["feet"],
                effort_limit={
                    ".*_ankle_pitch_joint": 50.0,
                    ".*_ankle_roll_joint": 50.0,
                },
                velocity_limit={
                    ".*_ankle_pitch_joint": 37.0,
                    ".*_ankle_roll_joint": 37.0,
                },
                stiffness={
                    ".*_ankle_pitch_joint": 20.0,
                    ".*_ankle_roll_joint": 20.0,
                },
                damping={
                    ".*_ankle_pitch_joint": 0.2,
                    ".*_ankle_roll_joint": 0.1,
                },
                armature=0.03,
                saturation_effort=80.0,
            ),
            "waist": ImplicitActuatorCfg(
                joint_names_expr=ACTUATOR_GROUPS["waist"],
                effort_limit_sim={
                    "waist_yaw_joint": 88.0,
                    "waist_roll_joint": 50.0,
                    "waist_pitch_joint": 50.0,
                },
                velocity_limit_sim={
                    "waist_yaw_joint": 32.0,
                    "waist_roll_joint": 37.0,
                    "waist_pitch_joint": 37.0,
                },
                stiffness={
                    "waist_yaw_joint": 5000.0,
                    "waist_roll_joint": 5000.0,
                    "waist_pitch_joint": 5000.0,
                },
                damping={
                    "waist_yaw_joint": 5.0,
                    "waist_roll_joint": 5.0,
                    "waist_pitch_joint": 5.0,
                },
                armature=0.001,
            ),
            "arms": ImplicitActuatorCfg(
                joint_names_expr=[
                    *ACTUATOR_GROUPS["arms"],
                ],
                effort_limit_sim=300.0,
                velocity_limit_sim=100.0,
                stiffness=3000.0,
                damping=10.0,
                armature={
                    ".*_shoulder_.*": 0.001,
                    ".*_elbow_.*": 0.001,
                    ".*_wrist_.*_joint": 0.001,
                },
            ),
        },
    )


class LazyG1LocalCfg:
    """Small proxy that can be imported before Isaac Sim is launched."""

    prim_path = DEFAULT_PRIM_PATH

    def build(self):
        """Build the actual IsaacLab ArticulationCfg."""
        return make_g1_local_cfg(self.prim_path)

    def replace(self, prim_path: str = DEFAULT_PRIM_PATH, **kwargs):
        """Mirror ArticulationCfg.replace for scripts that need a concrete cfg."""
        cfg = make_g1_local_cfg(prim_path=prim_path)
        if kwargs:
            cfg = cfg.replace(**kwargs)
        return cfg

    def __getattr__(self, name: str):
        return getattr(self.build(), name)


G1_LOCAL_CFG = LazyG1LocalCfg()
