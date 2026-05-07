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
