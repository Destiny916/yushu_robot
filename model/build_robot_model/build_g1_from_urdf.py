"""Build the local Unitree G1 robot asset from the repository URDF.

This script intentionally creates only the robot asset. It does not add a task,
controller, terrain, or extra scene objects.
"""

from __future__ import annotations

import argparse
import contextlib
from pathlib import Path
import sys

from robot_asset import get_default_urdf_path, get_default_usd_path, get_isaaclab_source_paths, require_complete_meshes


def bootstrap_isaaclab_paths() -> None:
    """Make local IsaacLab source packages importable from this project script."""
    for source_path in reversed(get_isaaclab_source_paths()):
        source_path_str = str(source_path)
        if source_path_str not in sys.path:
            sys.path.insert(0, source_path_str)


def parse_args() -> argparse.Namespace:
    bootstrap_isaaclab_paths()
    from isaaclab.app import AppLauncher

    parser = argparse.ArgumentParser(description="Build the Yushu Unitree G1 robot from the local URDF.")
    parser.add_argument(
        "--urdf",
        type=Path,
        default=get_default_urdf_path(),
        help="Path to the source URDF. Defaults to yushu_robot_urdf/g1_29dof_mode_16.urdf.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=get_default_usd_path(),
        help="Path for the generated USD. Defaults to model/build_robot_model/generated/g1_29dof_mode_16.usd.",
    )
    parser.add_argument(
        "--fix-base",
        action="store_true",
        default=False,
        help="Fix the robot base during URDF import.",
    )
    parser.add_argument(
        "--merge-fixed-joints",
        action="store_true",
        default=False,
        help="Merge links connected by fixed joints during URDF import.",
    )
    parser.add_argument(
        "--joint-stiffness",
        type=float,
        default=100.0,
        help="Default joint drive stiffness used by the URDF importer.",
    )
    parser.add_argument(
        "--joint-damping",
        type=float,
        default=1.0,
        help="Default joint drive damping used by the URDF importer.",
    )
    parser.add_argument(
        "--joint-target-type",
        choices=("position", "velocity", "none"),
        default="position",
        help="Default joint drive target type used by the URDF importer.",
    )
    AppLauncher.add_app_launcher_args(parser)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    urdf_path = args.urdf.resolve()
    usd_path = args.output.resolve()

    require_complete_meshes(urdf_path)
    usd_path.parent.mkdir(parents=True, exist_ok=True)

    from isaaclab.app import AppLauncher

    app_launcher = AppLauncher(args)
    simulation_app = app_launcher.app

    try:
        import carb
        import omni.kit.app

        import isaaclab.sim as sim_utils
        from isaaclab.sim.converters import UrdfConverter, UrdfConverterCfg
        from isaaclab.utils.dict import print_dict

        converter_cfg = UrdfConverterCfg(
            asset_path=str(urdf_path),
            usd_dir=str(usd_path.parent),
            usd_file_name=usd_path.name,
            fix_base=args.fix_base,
            merge_fixed_joints=args.merge_fixed_joints,
            force_usd_conversion=True,
            joint_drive=UrdfConverterCfg.JointDriveCfg(
                gains=UrdfConverterCfg.JointDriveCfg.PDGainsCfg(
                    stiffness=args.joint_stiffness,
                    damping=args.joint_damping,
                ),
                target_type=args.joint_target_type,
            ),
        )

        print("-" * 80)
        print(f"Input URDF file: {urdf_path}")
        print(f"Output USD file: {usd_path}")
        print("URDF importer config:")
        print_dict(converter_cfg.to_dict(), nesting=0)
        print("-" * 80)

        converter = UrdfConverter(converter_cfg)
        print(f"Generated USD file: {converter.usd_path}")

        sim_utils.open_stage(converter.usd_path)

        carb_settings_iface = carb.settings.get_settings()
        local_gui = carb_settings_iface.get("/app/window/enabled")
        livestream_gui = carb_settings_iface.get("/app/livestream/enabled")

        if local_gui or livestream_gui:
            app = omni.kit.app.get_app_interface()
            with contextlib.suppress(KeyboardInterrupt):
                while app.is_running():
                    app.update()
    finally:
        simulation_app.close()


if __name__ == "__main__":
    main()
