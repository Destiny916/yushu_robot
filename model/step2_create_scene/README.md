# Step 2: Create Scene

This component rewrites the Step 1 smoke test using IsaacLab's declarative
`InteractiveSceneCfg` pattern.

## Files

- `step2_create_scene.py`: scene-based G1 loading script.
- `test_step2_create_scene.py`: import and contract tests for the step.

## Run

```powershell
D:\il\env\Scripts\python.exe -B model\step2_create_scene\step2_create_scene.py --headless --max_steps 100
```

## Test

```powershell
D:\il\env\Scripts\python.exe -B model\step2_create_scene\test_step2_create_scene.py -v
```

## Dependencies

This step uses the generated USD from `model/generatedUSD/`. Rebuild the USD if
the URDF or meshes change.
