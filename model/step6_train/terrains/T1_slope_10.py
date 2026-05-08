"""T1: 10-degree Pyramid Slope Terrain (slope = 0.175 rad)."""

TERRAIN_NAME = "T1_slope_10"


def make_terrain_cfg():
    """Create T1 TerrainGeneratorCfg. Must be called after Isaac Sim is running."""
    from isaaclab.terrains import TerrainGeneratorCfg
    from isaaclab.terrains.height_field import HfPyramidSlopedTerrainCfg

    return TerrainGeneratorCfg(
        size=(8.0, 8.0),
        border_width=20.0,
        num_rows=10,
        num_cols=1,
        horizontal_scale=0.1,
        vertical_scale=0.005,
        curriculum=True,
        sub_terrains={
            "slope_10": HfPyramidSlopedTerrainCfg(
                proportion=1.0,
                slope_range=(0.175, 0.175),
                platform_width=1.0,
            ),
        },
    )
