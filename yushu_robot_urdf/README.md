# Yushu Robot URDF

This directory stores the raw robot asset sources for Unitree G1 29-DOF.

See `README_部件说明.md` for the full part map and naming rules.

## Contents

- `g1_29dof_mode_16.urdf`
- `meshes/`

## Role in the Project

The URDF and meshes here are the source inputs for
`model/build_robot_model/build_g1_from_urdf.py`. Generated USD output should
stay in `model/generatedUSD/`.
