"""G1 AHC terrain configurations for Phase 1 training."""

from .T0_plane import TERRAIN_NAME as T0_NAME, make_terrain_cfg as T0_make
from .T1_slope_10 import TERRAIN_NAME as T1_NAME, make_terrain_cfg as T1_make
from .T2_slope_20 import TERRAIN_NAME as T2_NAME, make_terrain_cfg as T2_make
from .T3_slope_30 import TERRAIN_NAME as T3_NAME, make_terrain_cfg as T3_make
from .T4_stairs import TERRAIN_NAME as T4_NAME, make_terrain_cfg as T4_make
from .T5_wave import TERRAIN_NAME as T5_NAME, make_terrain_cfg as T5_make

TERRAIN_MAKERS = {
    "T0": T0_make,
    "T1": T1_make,
    "T2": T2_make,
    "T3": T3_make,
    "T4": T4_make,
    "T5": T5_make,
}

TERRAIN_NAMES = {
    "T0": T0_NAME,
    "T1": T1_NAME,
    "T2": T2_NAME,
    "T3": T3_NAME,
    "T4": T4_NAME,
    "T5": T5_NAME,
}


def get_terrain_cfg(key: str):
    """Get a TerrainGeneratorCfg by key. Must be called after Isaac Sim is running."""
    return TERRAIN_MAKERS[key]()


__all__ = [
    "TERRAIN_MAKERS",
    "TERRAIN_NAMES",
    "get_terrain_cfg",
]
