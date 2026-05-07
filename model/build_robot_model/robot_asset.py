"""Helpers for building the local Yushu robot asset from its URDF."""

from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ISAACLAB_ROOT = PROJECT_ROOT.parents[1]
ISAACLAB_SOURCE_ROOT = ISAACLAB_ROOT / "source"
URDF_DIR = PROJECT_ROOT / "yushu_robot_urdf"
DEFAULT_URDF_PATH = URDF_DIR / "g1_29dof_mode_16.urdf"
DEFAULT_USD_DIR = Path(__file__).resolve().parent / "generated"
DEFAULT_USD_PATH = DEFAULT_USD_DIR / "g1_29dof_mode_16.usd"


def get_default_urdf_path() -> Path:
    """Return the repository-local G1 29DoF URDF path."""
    return DEFAULT_URDF_PATH


def get_default_usd_path() -> Path:
    """Return the default generated USD path."""
    return DEFAULT_USD_PATH


def get_isaaclab_source_paths() -> list[Path]:
    """Return IsaacLab source package roots for local script execution."""
    if not ISAACLAB_SOURCE_ROOT.is_dir():
        return []
    return sorted(path for path in ISAACLAB_SOURCE_ROOT.iterdir() if path.is_dir())


def list_mesh_references(urdf_path: str | Path) -> list[str]:
    """List mesh filenames exactly as referenced by the URDF."""
    root = ET.parse(Path(urdf_path)).getroot()
    mesh_refs: list[str] = []
    for mesh in root.iter("mesh"):
        filename = mesh.attrib.get("filename")
        if filename:
            mesh_refs.append(filename)
    return mesh_refs


def find_missing_meshes(urdf_path: str | Path) -> list[str]:
    """Return URDF mesh references that do not exist relative to the URDF file."""
    urdf_path = Path(urdf_path).resolve()
    urdf_dir = urdf_path.parent
    missing: list[str] = []

    for mesh_ref in sorted(set(list_mesh_references(urdf_path))):
        mesh_path = Path(mesh_ref)
        if not mesh_path.is_absolute():
            mesh_path = urdf_dir / mesh_path
        if not mesh_path.exists():
            missing.append(mesh_ref)

    return missing


def require_complete_meshes(urdf_path: str | Path) -> None:
    """Raise a clear error when a URDF references missing mesh files."""
    missing = find_missing_meshes(urdf_path)
    if not missing:
        return

    formatted = "\n".join(f"- {mesh}" for mesh in missing)
    raise FileNotFoundError(f"URDF references missing mesh files:\n{formatted}")
