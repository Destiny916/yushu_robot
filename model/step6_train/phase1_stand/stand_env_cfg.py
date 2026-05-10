"""Phase 1 standing environment without external force perturbations."""

from __future__ import annotations

from pathlib import Path
import sys


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
DEFAULT_ENV_SPACING = 4.0
DEFAULT_TERRAIN = "T0"
VALID_TERRAINS = tuple(TERRAIN_NAMES.keys())
ROBOT_PRIM_PATH = "{ENV_REGEX_NS}/Robot"
USE_TERRAIN_ORIGINS = False
ACTION_TERM_NAME = "joint_pos"
ACTION_SCALE = 0.10
STANDING_STATIC_FRICTION = 2.0
STANDING_DYNAMIC_FRICTION = 2.0
RESET_EVENT_TERMS = ("reset_base", "reset_joints")
EXTERNAL_FORCE_EVENT_TERMS = ()
EPISODE_LENGTH_S = 300.0
JOINT_POS_SOFT_LIMIT_WEIGHT = -12.0
JOINT_VEL_USD_LIMIT_WEIGHT = -8.0
TERMINATION_PENALTY_WEIGHT = -200.0
POLICY_OBSERVATION_TERMS = (
    "base_ang_vel",
    "projected_gravity",
    "joint_pos_rel",
    "joint_vel_rel",
    "last_action",
)
REWARD_TERMS = (
    "is_alive",
    "flat_orientation_l2",
    "base_height_l2",
    "lin_vel_xy_l2",
    "ang_vel_xy_l2",
    "joint_torques_l2",
    "joint_vel_l2",
    "joint_pos_soft_limits_l2",
    "joint_vel_usd_limits_l1",
    "arm_swing_l2",
    "arm_swing_asymmetry_l2",
    "joint_acc_l2",
    "action_rate_l2",
    "joint_deviation_l1",
    "termination_penalty",
)
TERMINATION_TERMS = ("time_out", "bad_orientation", "root_height_below_minimum", "joint_pos_out_of_limit")


def bootstrap_isaaclab_paths() -> None:
    """Make local IsaacLab source packages importable from this project script."""
    for source_path in reversed(get_isaaclab_source_paths()):
        source_path_str = str(source_path)
        if source_path_str not in sys.path:
            sys.path.insert(0, source_path_str)


def create_g1_stand_no_external_force_env_cfg(
    terrain_key: str = DEFAULT_TERRAIN,
    num_envs: int = DEFAULT_NUM_ENVS,
    env_spacing: float = DEFAULT_ENV_SPACING,
):
    """Create a ManagerBasedEnvCfg for standing on terrain without external force events."""
    bootstrap_isaaclab_paths()
    if terrain_key not in TERRAIN_NAMES:
        raise ValueError(f"Unknown terrain key: {terrain_key!r}. Expected one of: {', '.join(VALID_TERRAINS)}")

    import isaaclab.envs.mdp as mdp
    import isaaclab.sim as sim_utils
    from isaaclab.assets import ArticulationCfg, AssetBaseCfg
    from isaaclab.envs import ManagerBasedRLEnvCfg
    from isaaclab.managers import EventTermCfg as EventTerm
    from isaaclab.managers import ObservationGroupCfg as ObsGroup
    from isaaclab.managers import ObservationTermCfg as ObsTerm
    from isaaclab.managers import RewardTermCfg as RewTerm
    from isaaclab.managers import TerminationTermCfg as DoneTerm
    from isaaclab.scene import InteractiveSceneCfg
    from isaaclab.terrains import TerrainImporterCfg
    from isaaclab.utils import configclass
    from stand_rewards import arm_swing_asymmetry_l2 as arm_swing_asymmetry_l2_fn
    from stand_rewards import arm_swing_l2 as arm_swing_l2_fn
    from stand_rewards import joint_pos_out_of_limit as joint_pos_out_of_limit_fn
    from stand_rewards import joint_pos_soft_limits_l2 as joint_pos_soft_limits_l2_fn
    from stand_rewards import joint_vel_usd_limits_l1 as joint_vel_usd_limits_l1_fn
    from stand_rewards import lin_vel_xy_l2 as lin_vel_xy_l2_fn
    from stand_rewards import make_left_arm_swing_cfg as make_left_arm_swing_cfg_fn
    from stand_rewards import make_right_arm_swing_cfg as make_right_arm_swing_cfg_fn

    globals()["lin_vel_xy_l2_fn"] = lin_vel_xy_l2_fn
    globals()["joint_pos_soft_limits_l2_fn"] = joint_pos_soft_limits_l2_fn
    globals()["arm_swing_l2_fn"] = arm_swing_l2_fn
    globals()["arm_swing_asymmetry_l2_fn"] = arm_swing_asymmetry_l2_fn
    globals()["joint_pos_out_of_limit_fn"] = joint_pos_out_of_limit_fn
    globals()["make_left_arm_swing_cfg_fn"] = make_left_arm_swing_cfg_fn
    globals()["make_right_arm_swing_cfg_fn"] = make_right_arm_swing_cfg_fn
    globals()["joint_vel_usd_limits_l1_fn"] = joint_vel_usd_limits_l1_fn

    terrain_cfg = get_terrain_cfg(terrain_key)

    @configclass
    class G1StandSceneCfg(InteractiveSceneCfg):
        """Scene config for terrain, light, and local G1 robot."""

        terrain = TerrainImporterCfg(
            prim_path="/World/ground",
            terrain_type="generator",
            terrain_generator=terrain_cfg,
            use_terrain_origins=USE_TERRAIN_ORIGINS,
            max_init_terrain_level=5,
            collision_group=-1,
            physics_material=sim_utils.RigidBodyMaterialCfg(
                friction_combine_mode="multiply",
                restitution_combine_mode="multiply",
                static_friction=STANDING_STATIC_FRICTION,
                dynamic_friction=STANDING_DYNAMIC_FRICTION,
            ),
        )

        dome_light = AssetBaseCfg(
            prim_path="/World/Light",
            spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75)),
        )

        robot: ArticulationCfg = G1_LOCAL_CFG.replace(prim_path=ROBOT_PRIM_PATH)

    @configclass
    class ActionsCfg:
        """Joint position action over all G1 joints."""

        joint_pos = mdp.JointPositionActionCfg(
            asset_name="robot",
            joint_names=[".*"],
            scale=ACTION_SCALE,
            use_default_offset=True,
        )

    @configclass
    class ObservationsCfg:
        """Policy observation terms for the no-force standing baseline."""

        @configclass
        class PolicyCfg(ObsGroup):
            """Concatenated policy observation group."""

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
        """Reset-only events; intentionally no external pushes or force perturbations."""

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
    class RewardsCfg:
        """Standing rewards for the no-external-force PPO baseline."""

        is_alive = RewTerm(func=mdp.is_alive, weight=1.0)
        flat_orientation_l2 = RewTerm(func=mdp.flat_orientation_l2, weight=-2.0)
        base_height_l2 = RewTerm(func=mdp.base_height_l2, weight=-1.0, params={"target_height": 0.78})
        lin_vel_xy_l2 = RewTerm(func=lin_vel_xy_l2_fn, weight=-1.5)
        ang_vel_xy_l2 = RewTerm(func=mdp.ang_vel_xy_l2, weight=-0.5)
        joint_torques_l2 = RewTerm(func=mdp.joint_torques_l2, weight=-2.5e-5)
        joint_vel_l2 = RewTerm(func=mdp.joint_vel_l2, weight=-2.0e-3)
        joint_pos_soft_limits_l2 = RewTerm(func=joint_pos_soft_limits_l2_fn, weight=JOINT_POS_SOFT_LIMIT_WEIGHT)
        joint_vel_usd_limits_l1 = RewTerm(func=joint_vel_usd_limits_l1_fn, weight=JOINT_VEL_USD_LIMIT_WEIGHT)
        arm_swing_l2 = RewTerm(
            func=arm_swing_l2_fn,
            weight=-2.0,
            params={
                "left_asset_cfg": make_left_arm_swing_cfg_fn(),
                "right_asset_cfg": make_right_arm_swing_cfg_fn(),
            },
        )
        arm_swing_asymmetry_l2 = RewTerm(
            func=arm_swing_asymmetry_l2_fn,
            weight=-4.0,
            params={
                "left_asset_cfg": make_left_arm_swing_cfg_fn(),
                "right_asset_cfg": make_right_arm_swing_cfg_fn(),
            },
        )
        joint_acc_l2 = RewTerm(func=mdp.joint_acc_l2, weight=-5.0e-7)
        action_rate_l2 = RewTerm(func=mdp.action_rate_l2, weight=-0.02)
        joint_deviation_l1 = RewTerm(func=mdp.joint_deviation_l1, weight=-0.2)
        termination_penalty = RewTerm(func=mdp.is_terminated, weight=TERMINATION_PENALTY_WEIGHT)

    @configclass
    class TerminationsCfg:
        """Standing terminations for PPO training."""

        time_out = DoneTerm(func=mdp.time_out, time_out=True)
        bad_orientation = DoneTerm(func=mdp.bad_orientation, params={"limit_angle": 0.785})
        root_height_below_minimum = DoneTerm(func=mdp.root_height_below_minimum, params={"minimum_height": 0.45})
        joint_pos_out_of_limit = DoneTerm(func=joint_pos_out_of_limit_fn)

    @configclass
    class G1StandNoExternalForceEnvCfg(ManagerBasedRLEnvCfg):
        """Manager-Based RL standing environment with no external force events."""

        scene = G1StandSceneCfg(num_envs=num_envs, env_spacing=env_spacing)
        observations = ObservationsCfg()
        actions = ActionsCfg()
        rewards = RewardsCfg()
        terminations = TerminationsCfg()
        events = EventCfg()

        def __post_init__(self) -> None:
            self.viewer.eye = [2.5, -3.0, 2.0]
            self.viewer.lookat = [0.0, 0.0, 0.8]
            self.decimation = 4
            self.episode_length_s = EPISODE_LENGTH_S
            self.sim.dt = 0.005
            self.sim.render_interval = self.decimation

    return G1StandNoExternalForceEnvCfg()
