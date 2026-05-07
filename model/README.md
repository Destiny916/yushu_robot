# Model Simulation Code

`model/` is the home for simulation code used with the robot assets in this repository.

Use this directory for:

- IsaacLab task or environment configuration related to this robot.
- URDF-to-USD conversion helpers and generated asset wiring scripts.
- Training, evaluation, and replay entry points.
- Controller, policy, retargeting, and experiment configuration code.
- Small verification scripts that prove a robot asset or task loads correctly.

Keep robot geometry and part metadata in `../yushu_robot_urdf/`. Do not place STL, URDF, or mesh source files in `model/` unless a generated artifact is intentionally needed by a simulation workflow and documented here.

When adding new code, include a short note in the repository README if the command, environment ID, or workflow is useful for future runs.

## Directory Layout

Keep each independent workflow in its own folder under `model/`. A workflow folder owns its runnable scripts, helper modules, tests, and generated-output placeholder directories.

## Build the G1 Robot Asset

Run the local builder from the repository root:

```powershell
D:\il\env\Scripts\python.exe model\build_robot_model\build_g1_from_urdf.py --headless
```

The script validates every mesh referenced by `../yushu_robot_urdf/g1_29dof_mode_16.urdf`, converts the URDF into `model/build_robot_model/generated/g1_29dof_mode_16.usd`, and opens only that robot USD. It does not add terrain, tasks, controllers, or motion.

This command requires an IsaacLab/Isaac Sim Python environment with the IsaacLab dependencies installed. This repository currently uses `D:\il\env\Scripts\python.exe`.
