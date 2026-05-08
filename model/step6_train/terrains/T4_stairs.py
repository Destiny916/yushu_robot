"""T4: Pyramid Stairs Terrain (step height 0.05-0.15m, step width 0.3m)."""

TERRAIN_NAME = "T4_stairs"


def make_terrain_cfg():
    """Create T4 TerrainGeneratorCfg. Must be called after Isaac Sim is running."""
    from isaaclab.terrains import TerrainGeneratorCfg
    from isaaclab.terrains.height_field import HfPyramidStairsTerrainCfg

    return TerrainGeneratorCfg(
        size=(8.0, 8.0),
        border_width=20.0,
        num_rows=10,
        num_cols=1,
        horizontal_scale=0.1,
        vertical_scale=0.005,
        curriculum=True,
        sub_terrains={
            "stairs": HfPyramidStairsTerrainCfg(
                proportion=1.0,
                step_height_range=(0.05, 0.15),
                step_width=0.3,
                platform_width=1.0,
            ),
        },
    )
