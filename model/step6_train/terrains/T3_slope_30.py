"""T3: 30-degree Pyramid Slope Terrain (slope = 0.524 rad)."""

TERRAIN_NAME = "T3_slope_30"


def make_terrain_cfg():
    """Create T3 TerrainGeneratorCfg. Must be called after Isaac Sim is running."""
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
            "slope_30": HfPyramidSlopedTerrainCfg(
                proportion=1.0,
                slope_range=(0.524, 0.524),
                platform_width=1.0,
            ),
        },
    )
