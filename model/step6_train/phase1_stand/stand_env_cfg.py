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
ACTION_TARGET_LIMIT_KIND = "soft"
ACTION_TARGET_LIMIT_MARGIN = 0.005
STANDING_STATIC_FRICTION = 2.0
STANDING_DYNAMIC_FRICTION = 2.0
RESET_EVENT_TERMS = ("reset_base", "reset_joints")
EXTERNAL_FORCE_EVENT_TERMS = ()
EPISODE_LENGTH_S = 60.0
FALLEN_ROOT_HEIGHT_THRESHOLD = 0.45
ALIVE_REWARD_WEIGHT = 5.0
STANDING_TIME_REWARD_RAMP_START_S = 30.0
STANDING_TIME_REWARD_RAMP_END_S = 60.0
STANDING_TIME_REWARD_MAX_MULTIPLIER = 2.0
CONTACT_SENSOR_NAME = "contact_forces"
CONTACT_SENSOR_PRIM_PATH = "{ENV_REGEX_NS}/Robot/.*(ankle_roll_link|knee_link|elbow_link|wrist_yaw_link|rubber_hand)"
CONTACT_SENSOR_HISTORY_LENGTH = 6
FEET_CONTACT_THRESHOLD = 1.0
FEET_SLIDE_WEIGHT = -0.5
FEET_CONTACT_PRESENCE_WEIGHT = -1.0
FEET_CONTACT_BALANCE_WEIGHT = -0.15
COLLAPSE_LEFT_LEG_BODY_NAMES = ("left_ankle_roll_link", "left_knee_link")
COLLAPSE_RIGHT_LEG_BODY_NAMES = ("right_ankle_roll_link", "right_knee_link")
COLLAPSE_LEFT_ARM_BODY_NAMES = ("left_elbow_link", "left_wrist_yaw_link", "left_rubber_hand")
COLLAPSE_RIGHT_ARM_BODY_NAMES = ("right_elbow_link", "right_wrist_yaw_link", "right_rubber_hand")
COLLAPSE_GROUND_CONTACT_THRESHOLD = 1.0
COLLAPSE_GROUND_CONTACT_MIN_LIMBS = 3
COLLAPSE_GROUND_CONTACT_PENALTY_WEIGHT = -500.0
NATURAL_POSTURE_WAIST_JOINTS = ("waist_.*_joint",)
SHOULDER_POSTURE_JOINTS = (
    ".*_shoulder_pitch_joint",
    ".*_shoulder_roll_joint",
    ".*_shoulder_yaw_joint",
)
WAIST_TORSO_ALIGNMENT_JOINTS = ("waist_yaw_joint", "waist_roll_joint", "waist_pitch_joint")
HIP_POSTURE_JOINTS = (".*_hip_yaw_joint", ".*_hip_roll_joint", ".*_hip_pitch_joint")
ELBOW_STRAIGHTNESS_JOINTS = (".*_elbow_joint",)
HAND_POSTURE_JOINTS = (".*_wrist_roll_joint", ".*_wrist_pitch_joint", ".*_wrist_yaw_joint")
LEFT_ARM_VERTICAL_SHOULDER_BODY_NAMES = ("left_shoulder_pitch_link",)
LEFT_ARM_VERTICAL_HAND_BODY_NAMES = ("left_rubber_hand",)
RIGHT_ARM_VERTICAL_SHOULDER_BODY_NAMES = ("right_shoulder_pitch_link",)
RIGHT_ARM_VERTICAL_HAND_BODY_NAMES = ("right_rubber_hand",)
LEFT_ARM_SYMMETRY_JOINTS = (
    "left_shoulder_pitch_joint",
    "left_shoulder_roll_joint",
    "left_shoulder_yaw_joint",
    "left_elbow_joint",
    "left_wrist_roll_joint",
    "left_wrist_pitch_joint",
    "left_wrist_yaw_joint",
)
RIGHT_ARM_SYMMETRY_JOINTS = (
    "right_shoulder_pitch_joint",
    "right_shoulder_roll_joint",
    "right_shoulder_yaw_joint",
    "right_elbow_joint",
    "right_wrist_roll_joint",
    "right_wrist_pitch_joint",
    "right_wrist_yaw_joint",
)
JOINT_DEVIATION_WAIST_WEIGHT = -0.2
JOINT_DEVIATION_SHOULDERS_WEIGHT = -2.0
JOINT_SYMMETRY_ARMS_WEIGHT = -0.2
ARM_SWING_L2_WEIGHT = -3.0
WAIST_TORSO_ALIGNMENT_WEIGHT = -2.0
HIP_DEVIATION_WEIGHT = -0.3
ELBOW_STRAIGHTNESS_WEIGHT = -2.0
HAND_JOINT_DEVIATION_WEIGHT = -1.0
ARM_VERTICAL_ALIGNMENT_WEIGHT = -1.0
ANG_VEL_XY_WEIGHT = -1.5
JOINT_VEL_L2_WEIGHT = -5.0e-3
ACTION_RATE_L2_WEIGHT = -0.05
JOINT_POS_SOFT_LIMIT_WEIGHT = -12.0
JOINT_POS_HARD_LIMIT_WEIGHT = -50.0
JOINT_VEL_USD_LIMIT_WEIGHT = -8.0
JOINT_POS_LIMIT_TOLERANCE = 0.005
TERMINATION_PENALTY_WEIGHT = -200.0
JOINT_LIMIT_TERMINATION_PENALTY_WEIGHT = -500.0
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
    "joint_pos_hard_limits_l1",
    "joint_vel_usd_limits_l1",
    "feet_slide",
    "feet_contact_presence",
    "feet_contact_balance",
    "arm_swing_l2",
    "arm_swing_asymmetry_l2",
    "joint_acc_l2",
    "action_rate_l2",
    "joint_deviation_waist",
    "joint_deviation_shoulders",
    "joint_symmetry_arms",
    "waist_torso_alignment_l2",
    "hip_deviation_l2",
    "elbow_straightness_l2",
    "hand_joint_deviation_l2",
    "arm_vertical_alignment_l2",
    "termination_penalty",
    "joint_limit_violation_penalty",
    "collapse_ground_contact_penalty",
)
TERMINATION_TERMS = (
    "time_out",
    "root_height_below_minimum",
    "joint_pos_out_of_limit",
    "joint_vel_out_of_limit",
    "collapse_ground_contact",
)


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
    from isaaclab.managers import SceneEntityCfg
    from isaaclab.managers import TerminationTermCfg as DoneTerm
    from isaaclab.scene import InteractiveSceneCfg
    from isaaclab.sensors import ContactSensorCfg
    from isaaclab.terrains import TerrainImporterCfg
    from isaaclab.utils import configclass
    from stand_actions import ClampedJointPositionActionCfg
    from stand_rewards import arm_vertical_alignment_l2 as arm_vertical_alignment_l2_fn
    from stand_rewards import arm_swing_asymmetry_l2 as arm_swing_asymmetry_l2_fn
    from stand_rewards import arm_swing_l2 as arm_swing_l2_fn
    from stand_rewards import collapse_ground_contact as collapse_ground_contact_fn
    from stand_rewards import collapse_ground_contact_event as collapse_ground_contact_event_fn
    from stand_rewards import feet_contact_balance as feet_contact_balance_fn
    from stand_rewards import feet_contact_presence as feet_contact_presence_fn
    from stand_rewards import feet_slide as feet_slide_fn
    from stand_rewards import joint_deviation_l2 as joint_deviation_l2_fn
    from stand_rewards import joint_deviation_symmetry_l1 as joint_deviation_symmetry_l1_fn
    from stand_rewards import joint_limit_violation_event as joint_limit_violation_event_fn
    from stand_rewards import joint_pos_hard_limits_l1 as joint_pos_hard_limits_l1_fn
    from stand_rewards import joint_pos_out_of_limit as joint_pos_out_of_limit_fn
    from stand_rewards import joint_pos_soft_limits_l2 as joint_pos_soft_limits_l2_fn
    from stand_rewards import joint_vel_out_of_limit as joint_vel_out_of_limit_fn
    from stand_rewards import joint_vel_usd_limits_l1 as joint_vel_usd_limits_l1_fn
    from stand_rewards import lin_vel_xy_l2 as lin_vel_xy_l2_fn
    from stand_rewards import make_left_arm_swing_cfg as make_left_arm_swing_cfg_fn
    from stand_rewards import make_right_arm_swing_cfg as make_right_arm_swing_cfg_fn
    from stand_rewards import root_height_below_minimum as root_height_below_minimum_fn
    from stand_rewards import root_height_below_minimum_event as root_height_below_minimum_event_fn
    from stand_rewards import standing_time_reward as standing_time_reward_fn

    globals()["lin_vel_xy_l2_fn"] = lin_vel_xy_l2_fn
    globals()["joint_pos_soft_limits_l2_fn"] = joint_pos_soft_limits_l2_fn
    globals()["joint_pos_hard_limits_l1_fn"] = joint_pos_hard_limits_l1_fn
    globals()["joint_pos_out_of_limit_fn"] = joint_pos_out_of_limit_fn
    globals()["joint_vel_out_of_limit_fn"] = joint_vel_out_of_limit_fn
    globals()["joint_limit_violation_event_fn"] = joint_limit_violation_event_fn
    globals()["feet_slide_fn"] = feet_slide_fn
    globals()["feet_contact_presence_fn"] = feet_contact_presence_fn
    globals()["feet_contact_balance_fn"] = feet_contact_balance_fn
    globals()["joint_deviation_symmetry_l1_fn"] = joint_deviation_symmetry_l1_fn
    globals()["joint_deviation_l2_fn"] = joint_deviation_l2_fn
    globals()["arm_swing_l2_fn"] = arm_swing_l2_fn
    globals()["arm_swing_asymmetry_l2_fn"] = arm_swing_asymmetry_l2_fn
    globals()["arm_vertical_alignment_l2_fn"] = arm_vertical_alignment_l2_fn
    globals()["make_left_arm_swing_cfg_fn"] = make_left_arm_swing_cfg_fn
    globals()["make_right_arm_swing_cfg_fn"] = make_right_arm_swing_cfg_fn
    globals()["joint_vel_usd_limits_l1_fn"] = joint_vel_usd_limits_l1_fn
    globals()["root_height_below_minimum_fn"] = root_height_below_minimum_fn
    globals()["root_height_below_minimum_event_fn"] = root_height_below_minimum_event_fn
    globals()["standing_time_reward_fn"] = standing_time_reward_fn
    globals()["ClampedJointPositionActionCfg"] = ClampedJointPositionActionCfg
    globals()["collapse_ground_contact_fn"] = collapse_ground_contact_fn
    globals()["collapse_ground_contact_event_fn"] = collapse_ground_contact_event_fn

    def make_collapse_ground_contact_params() -> dict:
        return {
            "left_leg_sensor_cfg": SceneEntityCfg(
                CONTACT_SENSOR_NAME, body_names=list(COLLAPSE_LEFT_LEG_BODY_NAMES), preserve_order=True
            ),
            "right_leg_sensor_cfg": SceneEntityCfg(
                CONTACT_SENSOR_NAME, body_names=list(COLLAPSE_RIGHT_LEG_BODY_NAMES), preserve_order=True
            ),
            "left_arm_sensor_cfg": SceneEntityCfg(
                CONTACT_SENSOR_NAME, body_names=list(COLLAPSE_LEFT_ARM_BODY_NAMES), preserve_order=True
            ),
            "right_arm_sensor_cfg": SceneEntityCfg(
                CONTACT_SENSOR_NAME, body_names=list(COLLAPSE_RIGHT_ARM_BODY_NAMES), preserve_order=True
            ),
            "contact_threshold": COLLAPSE_GROUND_CONTACT_THRESHOLD,
            "min_contacting_limbs": COLLAPSE_GROUND_CONTACT_MIN_LIMBS,
        }

    terrain_cfg = get_terrain_cfg(terrain_key)
    robot_cfg = G1_LOCAL_CFG.replace(prim_path=ROBOT_PRIM_PATH)
    robot_cfg.spawn.activate_contact_sensors = True

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

        robot: ArticulationCfg = robot_cfg

        contact_forces = ContactSensorCfg(
            prim_path=CONTACT_SENSOR_PRIM_PATH,
            update_period=0.0,
            history_length=CONTACT_SENSOR_HISTORY_LENGTH,
            debug_vis=False,
        )

    @configclass
    class ActionsCfg:
        """Joint position action over all G1 joints."""

        joint_pos = ClampedJointPositionActionCfg(
            asset_name="robot",
            joint_names=[".*"],
            scale=ACTION_SCALE,
            use_default_offset=True,
            limit_kind=ACTION_TARGET_LIMIT_KIND,
            limit_margin=ACTION_TARGET_LIMIT_MARGIN,
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

        is_alive = RewTerm(
            func=standing_time_reward_fn,
            weight=ALIVE_REWARD_WEIGHT,
            params={
                "ramp_start_s": STANDING_TIME_REWARD_RAMP_START_S,
                "ramp_end_s": STANDING_TIME_REWARD_RAMP_END_S,
                "max_multiplier": STANDING_TIME_REWARD_MAX_MULTIPLIER,
            },
        )
        flat_orientation_l2 = RewTerm(func=mdp.flat_orientation_l2, weight=-2.0)
        base_height_l2 = RewTerm(func=mdp.base_height_l2, weight=-1.0, params={"target_height": 0.78})
        lin_vel_xy_l2 = RewTerm(func=lin_vel_xy_l2_fn, weight=-1.5)
        ang_vel_xy_l2 = RewTerm(func=mdp.ang_vel_xy_l2, weight=ANG_VEL_XY_WEIGHT)
        joint_torques_l2 = RewTerm(func=mdp.joint_torques_l2, weight=-2.5e-5)
        joint_vel_l2 = RewTerm(func=mdp.joint_vel_l2, weight=JOINT_VEL_L2_WEIGHT)
        joint_pos_soft_limits_l2 = RewTerm(func=joint_pos_soft_limits_l2_fn, weight=JOINT_POS_SOFT_LIMIT_WEIGHT)
        joint_pos_hard_limits_l1 = RewTerm(func=joint_pos_hard_limits_l1_fn, weight=JOINT_POS_HARD_LIMIT_WEIGHT)
        joint_vel_usd_limits_l1 = RewTerm(func=joint_vel_usd_limits_l1_fn, weight=JOINT_VEL_USD_LIMIT_WEIGHT)
        feet_slide = RewTerm(
            func=feet_slide_fn,
            weight=FEET_SLIDE_WEIGHT,
            params={
                "sensor_cfg": SceneEntityCfg(
                    CONTACT_SENSOR_NAME, body_names=".*ankle_roll_link", preserve_order=True
                ),
                "asset_cfg": SceneEntityCfg("robot", body_names=".*ankle_roll_link", preserve_order=True),
                "contact_threshold": FEET_CONTACT_THRESHOLD,
            },
        )
        feet_contact_presence = RewTerm(
            func=feet_contact_presence_fn,
            weight=FEET_CONTACT_PRESENCE_WEIGHT,
            params={
                "sensor_cfg": SceneEntityCfg(
                    CONTACT_SENSOR_NAME, body_names=".*ankle_roll_link", preserve_order=True
                ),
                "contact_threshold": FEET_CONTACT_THRESHOLD,
            },
        )
        feet_contact_balance = RewTerm(
            func=feet_contact_balance_fn,
            weight=FEET_CONTACT_BALANCE_WEIGHT,
            params={
                "sensor_cfg": SceneEntityCfg(
                    CONTACT_SENSOR_NAME, body_names=".*ankle_roll_link", preserve_order=True
                )
            },
        )
        arm_swing_l2 = RewTerm(
            func=arm_swing_l2_fn,
            weight=ARM_SWING_L2_WEIGHT,
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
        action_rate_l2 = RewTerm(func=mdp.action_rate_l2, weight=ACTION_RATE_L2_WEIGHT)
        joint_deviation_waist = RewTerm(
            func=mdp.joint_deviation_l1,
            weight=JOINT_DEVIATION_WAIST_WEIGHT,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=list(NATURAL_POSTURE_WAIST_JOINTS))},
        )
        joint_deviation_shoulders = RewTerm(
            func=mdp.joint_deviation_l1,
            weight=JOINT_DEVIATION_SHOULDERS_WEIGHT,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=list(SHOULDER_POSTURE_JOINTS))},
        )
        joint_symmetry_arms = RewTerm(
            func=joint_deviation_symmetry_l1_fn,
            weight=JOINT_SYMMETRY_ARMS_WEIGHT,
            params={
                "left_asset_cfg": SceneEntityCfg(
                    "robot", joint_names=list(LEFT_ARM_SYMMETRY_JOINTS), preserve_order=True
                ),
                "right_asset_cfg": SceneEntityCfg(
                    "robot", joint_names=list(RIGHT_ARM_SYMMETRY_JOINTS), preserve_order=True
                ),
            },
        )
        waist_torso_alignment_l2 = RewTerm(
            func=joint_deviation_l2_fn,
            weight=WAIST_TORSO_ALIGNMENT_WEIGHT,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=list(WAIST_TORSO_ALIGNMENT_JOINTS))},
        )
        hip_deviation_l2 = RewTerm(
            func=joint_deviation_l2_fn,
            weight=HIP_DEVIATION_WEIGHT,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=list(HIP_POSTURE_JOINTS))},
        )
        elbow_straightness_l2 = RewTerm(
            func=joint_deviation_l2_fn,
            weight=ELBOW_STRAIGHTNESS_WEIGHT,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=list(ELBOW_STRAIGHTNESS_JOINTS))},
        )
        hand_joint_deviation_l2 = RewTerm(
            func=joint_deviation_l2_fn,
            weight=HAND_JOINT_DEVIATION_WEIGHT,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=list(HAND_POSTURE_JOINTS))},
        )
        arm_vertical_alignment_l2 = RewTerm(
            func=arm_vertical_alignment_l2_fn,
            weight=ARM_VERTICAL_ALIGNMENT_WEIGHT,
            params={
                "left_shoulder_body_cfg": SceneEntityCfg(
                    "robot", body_names=list(LEFT_ARM_VERTICAL_SHOULDER_BODY_NAMES), preserve_order=True
                ),
                "left_hand_body_cfg": SceneEntityCfg(
                    "robot", body_names=list(LEFT_ARM_VERTICAL_HAND_BODY_NAMES), preserve_order=True
                ),
                "right_shoulder_body_cfg": SceneEntityCfg(
                    "robot", body_names=list(RIGHT_ARM_VERTICAL_SHOULDER_BODY_NAMES), preserve_order=True
                ),
                "right_hand_body_cfg": SceneEntityCfg(
                    "robot", body_names=list(RIGHT_ARM_VERTICAL_HAND_BODY_NAMES), preserve_order=True
                ),
            },
        )
        termination_penalty = RewTerm(
            func=root_height_below_minimum_event_fn,
            weight=TERMINATION_PENALTY_WEIGHT,
            params={"minimum_height": FALLEN_ROOT_HEIGHT_THRESHOLD},
        )
        joint_limit_violation_penalty = RewTerm(
            func=joint_limit_violation_event_fn,
            weight=JOINT_LIMIT_TERMINATION_PENALTY_WEIGHT,
            params={"tolerance": JOINT_POS_LIMIT_TOLERANCE},
        )
        collapse_ground_contact_penalty = RewTerm(
            func=collapse_ground_contact_event_fn,
            weight=COLLAPSE_GROUND_CONTACT_PENALTY_WEIGHT,
            params=make_collapse_ground_contact_params(),
        )

    @configclass
    class TerminationsCfg:
        """Standing terminations for PPO training."""

        time_out = DoneTerm(func=mdp.time_out, time_out=True)
        root_height_below_minimum = DoneTerm(
            func=root_height_below_minimum_fn,
            params={"minimum_height": FALLEN_ROOT_HEIGHT_THRESHOLD},
        )
        joint_pos_out_of_limit = DoneTerm(
            func=joint_pos_out_of_limit_fn,
            params={"tolerance": JOINT_POS_LIMIT_TOLERANCE},
        )
        joint_vel_out_of_limit = DoneTerm(func=joint_vel_out_of_limit_fn)
        collapse_ground_contact = DoneTerm(
            func=collapse_ground_contact_fn,
            params=make_collapse_ground_contact_params(),
        )

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
