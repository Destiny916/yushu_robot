"""T0: Flat Plane Terrain."""

TERRAIN_NAME = "T0_plane"


def make_terrain_cfg():
    """Create T0 TerrainGeneratorCfg. Must be called after Isaac Sim is running."""
    from isaaclab.terrains import TerrainGeneratorCfg
    from isaaclab.terrains.trimesh import MeshPlaneTerrainCfg

    return TerrainGeneratorCfg(
        size=(8.0, 8.0),
        border_width=20.0,
        num_rows=10,
        num_cols=1,
        horizontal_scale=0.1,
        vertical_scale=0.005,
        curriculum=True,
        sub_terrains={
            "flat": MeshPlaneTerrainCfg(proportion=1.0),
        },
    )
