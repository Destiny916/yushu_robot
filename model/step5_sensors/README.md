# Step 5: Contact Sensors

This component extends the Step 4 standing environment with ankle contact
sensors.

## Files

- `sensors_cfg.py`: contact sensor configuration helper.
- `run_sensors_env.py`: runnable sensor environment loop.
- `test_sensors_cfg.py`: tests for sensor path and configuration contract.

## Sensor Contract

- Sensor name: `contact_forces`
- Prim path: `{ENV_REGEX_NS}/Robot/.*ankle_roll_link`
- History length: `6`
- Default contact force tensor shape for one robot: `(1, 2, 3)`

## Run

```powershell
D:\il\env\Scripts\python.exe -B model\step5_sensors\run_sensors_env.py --headless --max_steps 100
```

## Test

```powershell
D:\il\env\Scripts\python.exe -B model\step5_sensors\test_sensors_cfg.py -v
```
