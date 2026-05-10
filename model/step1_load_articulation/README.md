# Step 1: Load Articulation

This component is the first IsaacLab smoke test for the generated G1 USD. It
starts Isaac Sim, creates a simple world, spawns one G1 articulation, and steps
the simulation.

## Files

- `step1_load_articulation.py`: runnable articulation loading script.
- `test_step1_load_articulation.py`: import and contract tests for the entry point.

## Run

```powershell
D:\il\env\Scripts\python.exe -B model\step1_load_articulation\step1_load_articulation.py --headless --max_steps 100
```

Without `--max_steps`, the simulation runs until the app is closed.

## Test

```powershell
D:\il\env\Scripts\python.exe -B model\step1_load_articulation\test_step1_load_articulation.py -v
```

## Dependencies

Run `model/build_robot_model/build_g1_from_urdf.py` first so
`model/generatedUSD/g1_29dof_mode_16.usd` exists.
