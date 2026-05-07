---
name: yushu-robot-project
description: Use this skill for any work inside the yushu_robot repository, especially tasks involving Unitree G1 URDF assets, robot part files, IsaacLab simulation code under model/, README updates, or publishing changes. Always use it when the user mentions yushu_robot, yushu_robot_urdf, robot simulation code, or pushing this project to GitHub.
---

# Yushu Robot Project Workflow

## Scope

Treat `yushu_robot/` as the project root for this repository. Keep all project-specific work inside this tree unless the user explicitly asks to modify the surrounding IsaacLab checkout.

Primary directories:

- `yushu_robot_urdf/`: robot part information, including URDF files, mesh files, sensor links, actuator geometry, and future robot asset variants.
- `model/`: simulation code for the robot, including IsaacLab configs, conversion helpers, training scripts, evaluation scripts, controllers, retargeting code, and verification code.

## Before Editing

1. Start from the repository root:

   ```powershell
   Set-Location d:\il\IsaacLab\scripts\yushu_robot
   ```

2. Check branch and worktree state:

   ```powershell
   git status -sb
   git branch --show-current
   ```

3. If uploading may be needed, switch to `codex` before editing:

   ```powershell
   git switch codex
   ```

4. Inspect existing patterns before adding files. Prefer `rg` and `rg --files`.

## Editing Rules

- Put robot hardware and geometry assets in `yushu_robot_urdf/`.
- Put runnable simulation, conversion, training, evaluation, and controller code in `model/`.
- Update `README.md` whenever a new workflow, command, robot asset, environment ID, or directory convention is introduced.
- Keep edits scoped to this repository unless the user explicitly asks for IsaacLab source changes outside `yushu_robot/`.
- Do not move or rename mesh files casually because URDF mesh paths depend on stable filenames.

## Verification

Use the smallest command that proves the change:

- Documentation-only changes: inspect the rendered Markdown source and run `git diff --check`.
- URDF changes: parse the XML and confirm referenced mesh files exist.
- Python simulation code: run the targeted script, import check, or the narrowest relevant IsaacLab command available.

Report any verification command that cannot be run, with the concrete blocker.

## Git Upload Rule

The project remote is:

```text
https://github.com/Destiny916/yushu_robot.git
```

All uploads for this project go to the `codex` branch unless the user explicitly gives a different branch:

```powershell
git switch codex
git status -sb
git add <intended-files>
git commit -m "<short message>"
git push origin codex
```

Before committing, inspect the staged diff. Stage only intended project files.
