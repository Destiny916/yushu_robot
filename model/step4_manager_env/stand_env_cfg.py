"""Step 4 Manager-Based environment config for the local G1 stand smoke test."""

from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILD_ROBOT_MODEL_DIR = PROJECT_ROOT / "model" / "build_robot_model"
STEP3_DIR = PROJECT_ROOT / "model" / "step3_robot_cfg"
for import_path in (BUILD_ROBOT_MODEL_DIR, STEP3_DIR):
    import_path_str = str(import_path)
    if import_path_str not in sys.path:
        sys.path.insert(0, import_path_str)

from robot_asset import get_isaaclab_source_paths
from g1_local_cfg import G1_LOCAL_CFG


DEFAULT_NUM_ENVS = 1
DEFAULT_MAX_STEPS = 0
DEFAULT_ENV_SPACING = 2.5
ROBOT_PRIM_PATH = "{ENV_REGEX_NS}/Robot"
ACTION_TERM_NAME = "joint_pos"
RESET_JOINTS_TERM_NAME = "reset_joints_by_offset"
POLICY_OBSERVATION_TERMS = [
    "base_ang_vel",
    "projected_gravity",
    "joint_pos_rel",
    "joint_vel_rel",
    "last_action",
]


def bootstrap_isaaclab_paths() -> None:
    """Make local IsaacLab source packages importable from this project script."""
    for source_path in reversed(get_isaaclab_source_paths()):
        source_path_str = str(source_path)
        if source_path_str not in sys.path:
            sys.path.insert(0, source_path_str)


def create_g1_stand_env_cfg(num_envs: int = DEFAULT_NUM_ENVS, env_spacing: float = DEFAULT_ENV_SPACING):
    """Create a ManagerBasedEnvCfg for a minimal local G1 standing smoke test."""
    bootstrap_isaaclab_paths()

    import isaaclab.envs.mdp as mdp
    import isaaclab.sim as sim_utils
    from isaaclab.assets import ArticulationCfg, AssetBaseCfg
    from isaaclab.envs import ManagerBasedEnvCfg
    from isaaclab.managers import EventTermCfg as EventTerm
    from isaaclab.managers import ObservationGroupCfg as ObsGroup
    from isaaclab.managers import ObservationTermCfg as ObsTerm
    from isaaclab.scene import InteractiveSceneCfg
    from isaaclab.utils import configclass

    @configclass
    class G1StandSceneCfg(InteractiveSceneCfg):
        """Scene config for the local G1 stand environment."""

        ground = AssetBaseCfg(prim_path="/World/defaultGroundPlane", spawn=sim_utils.GroundPlaneCfg())

        dome_light = AssetBaseCfg(
            prim_path="/World/Light",
            spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75)),
        )

        robot: ArticulationCfg = G1_LOCAL_CFG.replace(prim_path=ROBOT_PRIM_PATH)

    @configclass
    class ActionsCfg:
        """Action specifications for the stand smoke environment."""

        joint_pos = mdp.JointPositionActionCfg(
            asset_name="robot",
            joint_names=[".*"],
            scale=0.25,
            use_default_offset=True,
        )

    @configclass
    class ObservationsCfg:
        """Observation specifications for the stand smoke environment."""

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
    class G1StandEnvCfg(ManagerBasedEnvCfg):
        """Manager-Based environment config for the local G1 stand smoke test."""

        scene = G1StandSceneCfg(num_envs=num_envs, env_spacing=env_spacing)
        observations = ObservationsCfg()
        actions = ActionsCfg()
        events = EventCfg()

        def __post_init__(self) -> None:
            self.viewer.eye = [2.5, -3.0, 2.0]
            self.viewer.lookat = [0.0, 0.0, 0.8]
            self.decimation = 4
            self.sim.dt = 0.005
            self.sim.render_interval = self.decimation

    return G1StandEnvCfg()
