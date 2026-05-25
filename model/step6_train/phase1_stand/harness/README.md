# Phase 1 Stand Harness

This harness is the control layer for `model/step6_train/phase1_stand`.
It does not replace the IsaacLab training environment. It records the context,
contracts, feedback loop, and entropy policy that must be checked before
changing or running the standing trainer.

## Scope

- Primary implementation target: `yushu_robot/model/step6_train/phase1_stand`.
- Project search scope: all of `yushu_robot`.
- IsaacLab reference scope: `D:/il/IsaacLab/scripts` examples and
  `D:/il/IsaacLab/source` source code are read-only references.
- Generated logs, checkpoints, cache folders, and IsaacLab source code should
  not be modified by this harness.

## Quick Checks

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\harness\scripts\check_harness_contracts.py
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\harness\scripts\collect_context.py
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\harness\scripts\search_reference_examples.py TerrainImporterCfg --max-results 5
```

## Feedback Loop

1. Capture the current run command, seed, terrain, checkpoint, and observation.
2. Run harness contract checks.
3. Run focused unit tests for the touched area.
4. If behavior is unclear, search the declared project and IsaacLab reference
   roots before changing architecture.
5. Record the result in `feedback/run_review_template.md`.

## Change Control

- phase1_stand conversation requires harness read.
- Every conversation about `yushu_robot/model/step6_train/phase1_stand` must
  start by reading `harness/README.md`,
  `constraints/architecture_constraints.yaml`,
  `constraints/reward_contract.yaml`, and
  `constraints/termination_contract.yaml` before analysis or edits.
- phase1_stand change requires harness review.
- Any behavior change under `model/step6_train/phase1_stand` must check whether
  this harness also needs updates.
- Every phase1_stand conversation that changes behavior, commands, harness
  rules, contracts, scripts, tests, or run instructions must update the
  relevant README in the same change.
- confirm before writing harness changes.
- Before editing harness files, state the proposed file changes, reason, and
  expected impact, then wait for user confirmation.
- user confirmation is required before writing harness rule, contract, script,
  test, or README changes.
