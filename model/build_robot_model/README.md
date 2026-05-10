# Build Robot Model

This component validates the local G1 URDF and converts it into the generated
USD asset used by later IsaacLab workflows.

## Files

- `robot_asset.py`: shared paths and URDF mesh validation helpers.
- `build_g1_from_urdf.py`: IsaacLab/Isaac Sim URDF-to-USD conversion entry.
- `test_robot_asset.py`: lightweight tests for path and mesh-reference helpers.

## Run

From the repository root:

```powershell
D:\il\env\Scripts\python.exe -B model\build_robot_model\build_g1_from_urdf.py --headless
```

Expected output:

```text
model/generatedUSD/g1_29dof_mode_16.usd
```

## Test

```powershell
D:\il\env\Scripts\python.exe -B model\build_robot_model\test_robot_asset.py -v
```

## Notes

- Source assets stay in `yushu_robot_urdf/`.
- Generated USD assets stay in `model/generatedUSD/`.
- Later steps depend on this generated USD file existing.
