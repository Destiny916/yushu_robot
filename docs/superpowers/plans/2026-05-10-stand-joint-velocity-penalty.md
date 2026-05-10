# Standing Joint Velocity Penalty Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a USD-based joint velocity penalty to Phase 1 standing training so joint motion above 30% of the robot's configured maximum velocity is linearly penalized.

**Architecture:** Keep the logic inside `model/step6_train/phase1_stand/stand_rewards.py` as a small standalone reward helper that reads `asset.data.joint_vel_limits`. Wire it into `stand_env_cfg.py` as a dedicated reward term, replacing the older soft-velocity penalty so the standing policy is driven by the USD velocity ceiling instead of the soft actuator limit. Add focused tests that prove the threshold and linear penalty behavior.

**Tech Stack:** Python, PyTorch, IsaacLab manager-based RL config, `unittest`.

---

### Task 1: Add reward coverage for the new velocity penalty

**Files:**
- Create: `model/step6_train/phase1_stand/test_stand_rewards.py`

- [ ] **Step 1: Write the failing test**

```python
def test_joint_vel_usd_limits_l1_penalizes_only_above_30_percent_of_usd_limit():
    # 1. set joint_vel_limits = 10
    # 2. set joint_vel = 2.0 -> below 3.0 threshold, expect 0
    # 3. set joint_vel = 4.0 -> above threshold by 1.0, expect linear penalty of 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_rewards.py -v`
Expected: FAIL because `joint_vel_usd_limits_l1` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```python
def joint_vel_usd_limits_l1(env, soft_ratio=0.3, asset_cfg=SceneEntityCfg("robot")):
    asset = env.scene[asset_cfg.name]
    joint_vel = torch.abs(asset.data.joint_vel[:, asset_cfg.joint_ids])
    joint_limits = asset.data.joint_vel_limits[:, asset_cfg.joint_ids]
    violation = joint_vel - soft_ratio * joint_limits
    return torch.sum(torch.clamp(violation, min=0.0), dim=1)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_rewards.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add model/step6_train/phase1_stand/test_stand_rewards.py model/step6_train/phase1_stand/stand_rewards.py
git commit -m "feat: add usd-based joint velocity penalty"
```

### Task 2: Wire the new velocity penalty into the standing env

**Files:**
- Modify: `model/step6_train/phase1_stand/stand_env_cfg.py`
- Modify: `model/step6_train/phase1_stand/test_stand_env_cfg.py`

- [ ] **Step 1: Write the failing test**

```python
def test_standing_reward_terms_include_usd_velocity_penalty():
    # ensure reward term list includes joint_vel_usd_limits_l1
    # ensure old joint_vel_soft_limits_l2 term is no longer used
```

- [ ] **Step 2: Run test to verify it fails**

Run: `D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_env_cfg.py -v`
Expected: FAIL because the env config still uses the old velocity term.

- [ ] **Step 3: Write minimal implementation**

```python
from stand_rewards import joint_vel_usd_limits_l1 as joint_vel_usd_limits_l1_fn

globals()["joint_vel_usd_limits_l1_fn"] = joint_vel_usd_limits_l1_fn

joint_vel_usd_limits_l1 = RewTerm(func=joint_vel_usd_limits_l1_fn, weight=-8.0)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_env_cfg.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add model/step6_train/phase1_stand/stand_env_cfg.py model/step6_train/phase1_stand/test_stand_env_cfg.py
git commit -m "feat: wire usd-based joint velocity penalty"
```

### Task 3: Verify the touched files still parse cleanly

**Files:**
- Modify: none

- [ ] **Step 1: Run syntax check**

Run: `D:\il\env\Scripts\python.exe -B -m py_compile model\step6_train\phase1_stand\stand_rewards.py model\step6_train\phase1_stand\stand_env_cfg.py model\step6_train\phase1_stand\test_stand_rewards.py model\step6_train\phase1_stand\test_stand_env_cfg.py`
Expected: exit code `0`.

- [ ] **Step 2: Run the focused tests**

Run: `D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_rewards.py -v`
Run: `D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_env_cfg.py -v`
Expected: both pass.

