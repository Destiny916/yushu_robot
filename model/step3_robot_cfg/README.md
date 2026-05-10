# Step 3: Robot Config

This component provides the reusable local G1 IsaacLab `ArticulationCfg` used by
later scenes and environments.

## Files

- `g1_local_cfg.py`: exports `G1_LOCAL_CFG` and `make_g1_local_cfg()`.
- `test_g1_local_cfg.py`: tests for paths, actuator groups, and lazy config access.

## Config Summary

- Uses `model/generatedUSD/g1_29dof_mode_16.usd`.
- Defines actuator groups for legs, feet, waist, and arms.
- Sets a neutral standing initial pose.
- Keeps the prim path replaceable through `G1_LOCAL_CFG.replace(prim_path=...)`.

## Test

```powershell
D:\il\env\Scripts\python.exe -B model\step3_robot_cfg\test_g1_local_cfg.py -v
```

## Dependencies

Run the robot builder first if the generated USD is missing.
