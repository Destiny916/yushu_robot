"""T5: Irregular Wave Terrain (amplitude 0.02-0.08m, 2 waves)."""

TERRAIN_NAME = "T5_wave"


def make_terrain_cfg():
    """Create T5 TerrainGeneratorCfg. Must be called after Isaac Sim is running."""
    from isaaclab.terrains import TerrainGeneratorCfg
    from isaaclab.terrains.height_field import HfWaveTerrainCfg

    return TerrainGeneratorCfg(
        size=(8.0, 8.0),
        border_width=20.0,
        num_rows=10,
        num_cols=1,
        horizontal_scale=0.1,
        vertical_scale=0.005,
        curriculum=True,
        sub_terrains={
            "wave": HfWaveTerrainCfg(
                proportion=1.0,
                amplitude_range=(0.02, 0.08),
                num_waves=2,
            ),
        },
    )
