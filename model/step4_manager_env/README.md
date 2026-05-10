# Step 4: Manager-Based Stand Environment

This component builds a minimal IsaacLab manager-based environment for local G1
standing smoke tests.

## Files

- `stand_env_cfg.py`: manager-based environment config.
- `run_stand_env.py`: runnable environment loop.
- `test_stand_env_cfg.py`: tests for observation/action/reset contracts.

## Environment Contract

- Action: one `JointPositionActionCfg` over all 29 joints.
- Observation terms: `base_ang_vel`, `projected_gravity`, `joint_pos_rel`,
  `joint_vel_rel`, and `last_action`.
- Observation shape for one robot: 93 values.
- Reset events: root reset and zero-offset joint reset.

## Run

```powershell
D:\il\env\Scripts\python.exe -B model\step4_manager_env\run_stand_env.py --headless --max_steps 100
```

## Test

```powershell
D:\il\env\Scripts\python.exe -B model\step4_manager_env\test_stand_env_cfg.py -v
```
