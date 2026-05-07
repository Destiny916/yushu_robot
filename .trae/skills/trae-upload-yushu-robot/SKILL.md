---
name: trae-upload-yushu-robot
description: "Commits and pushes changes in this yushu_robot workspace to the codex branch on GitHub. Invoke when the user asks to upload, sync, push, or publish this project from Trae."
---

# Trae Upload Workflow for yushu_robot

Use this skill every time the user wants to upload this project from Trae.

## Non-negotiable rule

All Trae uploads for this repository go to the `codex` branch on `https://github.com/Destiny916/yushu_robot.git` unless the user explicitly requests another branch.

If the local branch is not `codex`, switch to it before staging or committing.

## Workflow

1. Confirm the working directory is the project root `d:\il\IsaacLab\scripts\yushu_robot`.
2. Run:
   ```powershell
   git status -sb
   git branch --show-current
   ```
3. If the current branch is not `codex`, switch:
   ```powershell
   git switch codex
   ```
4. Inspect changes and stage only intended files.
5. Commit with a short message describing the change.
6. Push:
   ```powershell
   git push origin codex
   ```

## Commit discipline

- Prefer scoped commits over a single giant commit when multiple unrelated changes exist.
- Do not push unrelated project files from outside `yushu_robot/`.
- If no meaningful changes exist, explain that instead of creating an empty commit.

## Example push command

```powershell
git push origin codex
```

## Notes

- Remote: `https://github.com/Destiny916/yushu_robot.git`
- Default target branch for Trae uploads: `codex`
- If the remote branch `codex` does not exist yet, create it locally and push with `git push -u origin codex`.
