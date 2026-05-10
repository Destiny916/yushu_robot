# Step 6 Terrains

This component defines the terrain set used by the AHC standing-training work.

## Terrain Keys

| Key | File | Type |
| --- | --- | --- |
| `T0` | `T0_plane.py` | Flat plane |
| `T1` | `T1_slope_10.py` | 10 degree slope |
| `T2` | `T2_slope_20.py` | 20 degree slope |
| `T3` | `T3_slope_30.py` | 30 degree slope |
| `T4` | `T4_stairs.py` | Stairs |
| `T5` | `T5_wave.py` | Irregular wave |

Each file exports `TERRAIN_NAME` and `make_terrain_cfg()`. `__init__.py`
registers all makers through `TERRAIN_MAKERS`, `TERRAIN_NAMES`, and
`get_terrain_cfg(key)`.

## Test One Terrain

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\terrains\test_terrains.py --terrain T0 --headless --max_steps 2
```

Use `--terrain T1`, `--terrain T2`, etc. to switch terrain.

## Multi-Environment Note

The Phase 1 standing environment currently uses grid origins rather than terrain
origins so multiple robots do not spawn on top of each other.
