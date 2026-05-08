# G1 AHC 多行为蒸馏站立训练 — 实施计划 (Plan)

> 版本: v1.0 | 日期: 2026-05-08
>
> 本文件是 `spec.md` 的配套实施计划，按阶段分解为可独立验证的步骤。

---

## 开发总览

```
Phase 1             Phase 2          Phase 3
┌──────────────┐    ┌──────────┐    ┌──────────┐
│ P1.1 地形系统  │    │ P2.1 MoE  │    │ P3.1 PCGrad│
│ P1.2 站立环境  │    │ 网络架构   │    │ Trainer   │
│ P1.3 站立训练  │    │ P2.2 DAgger│   │ P3.2 微调   │
│ P1.4 行走环境  │    │ Trainer   │    │ 训练       │
│ P1.5 行走训练  │    │ P2.3 蒸馏  │    │ P3.3 评估   │
└──────────────┘    └──────────┘    └──────────┘
      ↓                  ↓                ↓
  独立验证          独立验证          最终验证
```

## 前置条件

- [x] Step 0: URDF → USD 转换 (已完成)
- [x] Step 1: 手动 Articulation 加载 (已完成)
- [x] Step 2: InteractiveSceneCfg (已完成)
- [x] Step 3: G1_LOCAL_CFG (已完成)
- [x] Step 4: Manager-Based 环境 (已完成)
- [x] Step 5: 接触传感器 (已完成)
- [ ] 验证现有 USD 路径 `model/generatedUSD/g1_29dof_mode_16.usd` 存在
- [ ] 验证 `D:\il\env\Scripts\python.exe` 环境可正常导入 IsaacLab

---

## Phase 1: 独立专精 PPO 训练

### P1.1 — 自定义地形系统

**目录**: `model/step6_train/terrains/`

**文件**:

| 文件 | 用途 |
|------|------|
| `__init__.py` | 导出 `G1_STAND_TERRAINS_CFG` |
| `g1_stand_terrains_cfg.py` | 6 种地形混合配置 |

**实现要点**:

1. 创建 `G1_STAND_TERRAINS_CFG` = `TerrainGeneratorCfg(...)` 包含:
   - `MeshPlaneTerrainCfg` (平面，占比 20%)
   - `HfPyramidSlopedTerrainCfg` × 3 (10°/20°/30° 斜坡)
   - `HfPyramidStairsTerrainCfg` (楼梯)
   - `HfWaveTerrainCfg` (不规则波浪)
2. 设置 `curriculum=True`，`num_rows=10`，`num_cols=6`
3. 编写单元测试验证地形配置结构

**验证命令**:
```powershell
D:\il\env\Scripts\python.exe -B -c "from model.step6_train.terrains.g1_stand_terrains_cfg import G1_STAND_TERRAINS_CFG; print(G1_STAND_TERRAINS_CFG.sub_terrains.keys())"
```

**预计工作量**: 1 个文件 + 1 个测试

**依赖**: 无 (纯配置，不依赖 Isaac Sim)

**状态**: 待开始

---

### P1.2 — 站立环境配置

**目录**: `model/step6_train/phase1_stand/`

**文件**:

| 文件 | 用途 |
|------|------|
| `__init__.py` | 模块导出 |
| `stand_env_cfg.py` | `G1StandEnvCfg` (ManagerBasedRLEnvCfg) |
| `stand_rewards.py` | 站立奖励函数和终止条件 |
| `test_stand_env.py` | 环境冒烟测试 |

**实现要点**:

1. `stand_env_cfg.py`:
   - 继承/扩展 step4 的 `create_g1_stand_env_cfg()`
   - 将 `GroundPlaneCfg` 替换为 `TerrainImporterCfg(terrain_type="generator", terrain_generator=G1_STAND_TERRAINS_CFG)`
   - 添加 `ManagerBasedRLEnvCfg` 字段: `rewards`, `terminations`, `curriculum`, `commands`
   - 设置 `episode_length_s=20.0`
   - 观察空间增加 `terrain_type` one-hot (6维)
   - 命令: `c = 1.0` (固定站立)

2. `stand_rewards.py`:
   - `G1StandRewards` = `RewardsCfg` 包含:
     - `is_alive` (权重 1.0)
     - `flat_orientation_l2` (权重 -2.0)
     - `base_height_l2` (目标 0.78m, 权重 -1.0)
     - `lin_vel_xy_l2` (权重 -1.5)
     - `ang_vel_xy_l2` (权重 -0.5)
     - `joint_torques_l2` (权重 -2.5e-5)
     - `joint_vel_l2` (权重 -1.0e-3)
     - `joint_acc_l2` (权重 -2.5e-7)
     - `action_rate_l2` (权重 -0.01)
     - `joint_deviation_l1` (权重 -0.1)
     - `feet_contact_symmetry` (自定义，基于 contact_forces)
     - `termination_penalty` (权重 -200.0)

3. `G1StandTerminations`:
   - `time_out`: episode_length_s 耗尽
   - `bad_orientation`: 倾斜 > 0.785 rad
   - `root_height_below_minimum`: 高度 < 0.45m
   - `joint_pos_out_of_limit`: 关节超限
   - `illegal_contact`: torso/head contact > 100N

**验证命令**:
```powershell
D:\il\env\Scripts\python.exe -B -m unittest model/step6_train/phase1_stand/test_stand_env.py -v
D:\il\env\Scripts\python.exe -B -c "from model.step6_train.phase1_stand.stand_env_cfg import G1StandEnvCfg; print('import ok')"
```

**预计工作量**: 3-4 个文件

**依赖**: P1.1 (地形配置)

**状态**: 待开始

---

### P1.3 — 站立 PPO 训练

**目录**: `model/step6_train/phase1_stand/`

**文件**:

| 文件 | 用途 |
|------|------|
| `stand_ppo_cfg.py` | PPO 超参数配置 (RslRlOnPolicyRunnerCfg) |
| `train_stand.py` | 训练入口脚本 |

**实现要点**:

1. `stand_ppo_cfg.py`:
   ```python
   G1StandPPORunnerCfg = RslRlOnPolicyRunnerCfg(
       num_steps_per_env=24,
       max_iterations=1500,
       save_interval=50,
       experiment_name="g1_stand",
       policy=RslRlPpoActorCriticCfg(
           init_noise_std=1.0,
           actor_obs_normalization=True,
           critic_obs_normalization=True,
           actor_hidden_dims=[512, 256, 128],
           critic_hidden_dims=[512, 256, 128],
           activation="elu",
       ),
       algorithm=RslRlPpoAlgorithmCfg(
           value_loss_coef=1.0,
           use_clipped_value_loss=True,
           clip_param=0.2,
           entropy_coef=0.01,
           num_learning_epochs=5,
           num_mini_batches=4,
           learning_rate=1.0e-3,
           schedule="adaptive",
           gamma=0.99,
           lam=0.95,
           desired_kl=0.01,
           max_grad_norm=1.0,
       ),
   )
   ```

2. `train_stand.py`:
   - 基于 `scripts/reinforcement_learning/rsl_rl/train.py` 简化版本
   - 不使用 gym 注册，直接实例化 `ManagerBasedRLEnv(cfg=G1StandEnvCfg)`
   - 包装为 `RslRlVecEnvWrapper`
   - 创建 `OnPolicyRunner` 启动训练
   - 日志输出到 `logs/rsl_rl/g1_stand/`
   - checkpoint 保存为 `checkpoint_stand.pt`

**验证命令**:
```powershell
# 冒烟训练 (100 iters)
D:\il\env\Scripts\python.exe model/step6_train/phase1_stand/train_stand.py --headless --num_envs 64 --max_iterations 100
```

**预计工作量**: 2 个文件

**依赖**: P1.2 (站立环境)

**状态**: 待开始

---

### P1.4 — 行走环境配置

**目录**: `model/step6_train/phase1_walk/`

**文件**:

| 文件 | 用途 |
|------|------|
| `__init__.py` | 模块导出 |
| `walk_env_cfg.py` | `G1WalkEnvCfg` (继承 LocomotionVelocityRoughEnvCfg) |
| `walk_ppo_cfg.py` | 行走 PPO 超参数 |
| `test_walk_env.py` | 环境冒烟测试 |

**实现要点**:

1. `walk_env_cfg.py`:
   - 继承 `LocomotionVelocityRoughEnvCfg` 的奖励/终止结构
   - 使用 `G1_STAND_TERRAINS_CFG` 作为地形
   - 机器人: `G1_LOCAL_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")`
   - 命令: `UniformVelocityCommandCfg`，速度范围受 `c` 缩放
   - 置信度 `c ~ Uniform(0.0, 1.0)` 在 reset 时采样
   - 实际速度指令 = `(1-c) * lin_vel_x_target` (0 到 1.0 m/s)
   - 新增观测: `confidence_c` (1维) + `terrain_type` one-hot (6维)
   - 奖励增加: `stand_still_joint_deviation_l1` (低速时保持姿态)

2. `walk_ppo_cfg.py`:
   - 参照 `G1RoughPPORunnerCfg`
   - `max_iterations=2000`
   - 其余参数同 Phase 1 站立 PPO

**验证命令**:
```powershell
D:\il\env\Scripts\python.exe -B -m unittest model/step6_train/phase1_walk/test_walk_env.py -v
```

**预计工作量**: 3 个文件

**依赖**: P1.1 (地形配置)

**状态**: 待开始

---

### P1.5 — 行走 PPO 训练

**目录**: `model/step6_train/phase1_walk/`

**文件**:

| 文件 | 用途 |
|------|------|
| `train_walk.py` | 行走训练入口 |

**实现要点**: 同 P1.3，但使用 `G1WalkEnvCfg` 和 `G1WalkPPORunnerCfg`。checkpoint 保存为 `checkpoint_walk.pt`。

**验证命令**:
```powershell
D:\il\env\Scripts\python.exe model/step6_train/phase1_walk/train_walk.py --headless --num_envs 64 --max_iterations 100
```

**预计工作量**: 1 个文件

**依赖**: P1.4 (行走环境)

**状态**: 待开始

---

## Phase 2: DAgger 知识蒸馏

### P2.1 — MoE 网络架构

**目录**: `model/step6_train/phase2_dagger/`

**文件**:

| 文件 | 用途 |
|------|------|
| `__init__.py` | 模块导出 |
| `gating_network.py` | Gating Network 定义 (PyTorch nn.Module) |
| `moe_policy.py` | MoE 策略封装 (Gating + frozen Experts) |
| `test_moe.py` | MoE 网络单元测试 |

**实现要点**:

1. `gating_network.py`:
   ```python
   class GatingNetwork(nn.Module):
       def __init__(self, obs_dim, terrain_emb_dim=8, hidden_dims=[256, 128]):
           super().__init__()
           input_dim = obs_dim + terrain_emb_dim + 1  # +1 for confidence c
           layers = []
           prev = input_dim
           for h in hidden_dims:
               layers.extend([nn.Linear(prev, h), nn.ELU()])
               prev = h
           layers.append(nn.Linear(prev, 1))
           layers.append(nn.Sigmoid())
           self.net = nn.Sequential(*layers)
           self.terrain_embedding = nn.Embedding(6, terrain_emb_dim)  # 6 terrain types

       def forward(self, obs, terrain_type_idx, c):
           t_emb = self.terrain_embedding(terrain_type_idx)
           x = torch.cat([obs, t_emb, c], dim=-1)
           return self.net(x)  # α ∈ [0, 1]
   ```

2. `moe_policy.py`:
   ```python
   class MoEPolicy(nn.Module):
       def __init__(self, gating, actor_stand, actor_walk, critic_stand, critic_walk):
           self.gating = gating
           self.actor_stand = actor_stand  # frozen
           self.actor_walk = actor_walk    # frozen
           self.critic_stand = critic_stand  # frozen
           self.critic_walk = critic_walk    # frozen

       def forward(self, obs, terrain_type_idx, c):
           alpha = self.gating(obs, terrain_type_idx, c)
           action = alpha * self.actor_stand(obs) + (1-alpha) * self.actor_walk(obs)
           return action, alpha
   ```

**验证命令**:
```powershell
D:\il\env\Scripts\python.exe -B -m unittest model/step6_train/phase2_dagger/test_moe.py -v
```

**预计工作量**: 3 个文件

**依赖**: Phase 1 的两个 checkpoint（单元测试阶段可用随机权重替代）

**状态**: 待开始

---

### P2.2 — DAgger 数据聚合训练器

**目录**: `model/step6_train/phase2_dagger/`

**文件**:

| 文件 | 用途 |
|------|------|
| `dagger_cfg.py` | DAgger 超参数配置 |
| `dagger_trainer.py` | DAgger 训练循环实现 |

**实现要点**:

1. `dagger_cfg.py`:
   ```python
   @configclass
   class DaggerCfg:
       num_rounds: int = 10            # DAgger 迭代轮数
       confidences: list = [0.0, 0.25, 0.5, 0.75, 1.0]  # 覆盖的 c 值
       num_envs_per_config: int = 64   # 每个配置的环境数
       steps_per_rollout: int = 24     # 每次 rollout 步数
       batch_size: int = 4096
       learning_rate: float = 1.0e-3
       num_epochs_per_round: int = 50
       dataset_cache_path: str = "model/step6_train/phase2_dagger/dagger_dataset.pt"
   ```

2. `dagger_trainer.py`:
   - `DaggerTrainer` 类:
     - `collect_rollouts(env, gating, experts, c, terrain)`:
       1. 学生推演: MoE 策略在环境中 rollout
       2. 教师标注: 对每一步的 obs，用目标专家 (c≥0.5→stand, c<0.5→walk) 计算 action
       3. 存储: `(obs, terrain_idx, c, teacher_action)`
     - `train_round(dataset)`:
       1. 训练 Gating Network 使 `α = G(obs, terrain_idx, c)` 接近 `c`
       2. Loss: `MSE(α_pred, c_target)`
       3. 也可加辅助 Loss: `MSE(action_pred, teacher_action)`
     - `run()`: 多轮迭代聚合

**注意事项**:
- DAgger 不需要完整的 Isaac Sim 环境——可以用 Phase 1 的 Actor 做推理模式
- 数据集以 `.pt` 文件缓存
- 每轮后评估 α 预测准确率

**预计工作量**: 2 个文件

**依赖**: P2.1 (MoE 网络) + Phase 1 checkpoints

**状态**: 待开始

---

### P2.3 — DAgger 蒸馏执行

**目录**: `model/step6_train/phase2_dagger/`

**文件**:

| 文件 | 用途 |
|------|------|
| `run_dagger.py` | DAgger 训练入口 |

**实现要点**:

1. 加载 Phase 1 的两个 checkpoint
2. 创建 MoE 策略（Gating 随机初始化）
3. 运行 `DaggerTrainer.run()` 执行 K 轮 DAgger
4. 保存 MoE checkpoint: `checkpoint_moe_dagger.pt`

**验证命令**:
```powershell
D:\il\env\Scripts\python.exe model/step6_train/phase2_dagger/run_dagger.py --num_rounds 3 --headless
```

**预计工作量**: 1 个文件

**依赖**: P2.2 (DAgger Trainer)

**状态**: 待开始

---

## Phase 3: PCGrad 多任务 PPO 微调

### P3.1 — PCGrad Trainer

**目录**: `model/step6_train/phase3_pcgrad/`

**文件**:

| 文件 | 用途 |
|------|------|
| `__init__.py` | 模块导出 |
| `pcgrad_cfg.py` | PCGrad + PPO 超参数配置 |
| `pcgrad_trainer.py` | PCGrad 多任务 PPO 训练器 |
| `test_pcgrad.py` | PCGrad 单元测试 |

**实现要点**:

1. `pcgrad_trainer.py`:
   ```python
   class PCGradPPOTrainer:
       def compute_pcgrad_gradients(self, loss_stand, loss_walk):
           # 1. 分别计算两个 task 的梯度
           grad_stand = autograd.grad(loss_stand, params, retain_graph=True)
           grad_walk = autograd.grad(loss_walk, params)

           # 2. 逐参数检查冲突并投影
           for i, (g_s, g_w) in enumerate(zip(grad_stand, grad_walk)):
               if g_s is None or g_w is None:
                   continue
               cos_sim = (g_s * g_w).sum() / (g_s.norm() * g_w.norm() + 1e-8)
               if cos_sim < 0:
                   # 投影: g_s' = g_s - (g_s·g_w)/(g_w·g_w) * g_w
                   g_s = g_s - (g_s * g_w).sum() / (g_w * g_w + 1e-8).sum() * g_w
                   g_w = g_w - (g_w * g_s).sum() / (g_s * g_s + 1e-8).sum() * g_s
               grad_stand[i] = g_s
               grad_walk[i] = g_w

           return grad_stand, grad_walk

       def train_step(self, batch_stand, batch_walk):
           # 1. 前向: 分别计算 standing (c∈[0.5,1.0]) 和 walking (c∈[0,0.5]) 的 PPO loss
           loss_stand = self.ppo_loss(batch_stand, task="stand")
           loss_walk = self.ppo_loss(batch_walk, task="walk")

           # 2. PCGrad 梯度处理
           g_s, g_w = self.compute_pcgrad_gradients(loss_stand, loss_walk)

           # 3. 合并梯度并更新
           for param in self.moe_policy.parameters():
               param.grad = (g_s[param] + g_w[param]) if param in g_s else None
           self.optimizer.step()
   ```

2. `pcgrad_cfg.py`:
   - Max iterations: 500
   - Batch 大小: 2048 per task
   - 学习率: 1e-4
   - Standing batch: c ~ Uniform(0.5, 1.0)
   - Walking batch: c ~ Uniform(0.0, 0.5)
   - 其余 PPO 参数同 Phase 1

**验证命令**:
```powershell
D:\il\env\Scripts\python.exe -B -m unittest model/step6_train/phase3_pcgrad/test_pcgrad.py -v
```

**预计工作量**: 3 个文件

**依赖**: Phase 2 (MoE checkpoint)

**状态**: 待开始

---

### P3.2 — PCGrad 微调训练

**目录**: `model/step6_train/phase3_pcgrad/`

**文件**:

| 文件 | 用途 |
|------|------|
| `run_pcgrad.py` | PCGrad 微调训练入口 |

**实现要点**:

1. 加载 `checkpoint_moe_dagger.pt` (Phase 2 输出)
2. 解冻 Expert 网络（从 frozen 变为 trainable）
3. 创建两个环境变体:
   - Standing env: c ~ Uniform(0.5, 1.0)
   - Walking env: c ~ Uniform(0.0, 0.5)
4. 运行 PCGrad Trainer
5. 保存最终 checkpoint: `checkpoint_moe_final.pt`

**验证命令**:
```powershell
D:\il\env\Scripts\python.exe model/step6_train/phase3_pcgrad/run_pcgrad.py --headless --num_envs 64 --max_iterations 50
```

**预计工作量**: 1 个文件

**依赖**: P3.1 (PCGrad Trainer)

**状态**: 待开始

---

### P3.3 — 最终评估

**目录**: `model/step6_train/phase3_pcgrad/`

**文件**:

| 文件 | 用途 |
|------|------|
| `evaluate.py` | 综合评估脚本 |

**评估维度**:

1. **存活率测试**: 6 种地形 × 5 个 c 值 × 20s episode，各跑 10 次，统计存活率
2. **切换平滑度**: c 从 0.0 递增到 1.0 (step=0.05)，测量动作变化量 |Δa|
3. **速度追踪**: c=0 时追踪 v_x=0.5, 1.0 m/s 的误差
4. **与 Phase 2 对比**: 存活率、速度追踪误差、α 预测准确率

**验证命令**:
```powershell
D:\il\env\Scripts\python.exe model/step6_train/phase3_pcgrad/evaluate.py --headless --checkpoint checkpoint_moe_final.pt
```

**预计工作量**: 1 个文件

**依赖**: P3.2 (PCGrad 完成)

**状态**: 待开始

---

### P.C — 通用工具模块

**目录**: `model/step6_train/common/`

**文件**:

| 文件 | 用途 |
|------|------|
| `__init__.py` | 模块导出 |
| `terrain_utils.py` | 地形类型索引、one-hot 编码工具 |
| `policy_utils.py` | 策略保存/加载/冻结工具 |

**预计工作量**: 2 个文件

**依赖**: 无

**状态**: 待开始

---

## 任务依赖图

```
P.C (common) ──────────────────────────────────────────┐
     │                                                  │
P1.1 (地形) ──┬── P1.2 (站立环境) ── P1.3 (站立训练) ──┤
     │        │                         ↓               │
     │        └── P1.4 (行走环境) ── P1.5 (行走训练) ──┤
     │                                     ↓            │
     │                              P2.1 (MoE网络) ─────┤
     │                                     ↓            │
     │                              P2.2 (DAgger) ──────┤
     │                                     ↓            │
     │                              P2.3 (蒸馏执行) ────┤
     │                                     ↓            │
     │                              P3.1 (PCGrad) ──────┤
     │                                     ↓            │
     │                              P3.2 (微调训练) ────┤
     │                                     ↓            │
     │                              P3.3 (最终评估) ────┘
```

---

## 总文件清单

| 阶段 | 文件数 | 目录 |
|------|--------|------|
| P.C (通用) | 2 | `common/` |
| P1.1 (地形) | 1 | `terrains/` |
| P1.2 (站立环境) | 3 | `phase1_stand/` |
| P1.3 (站立训练) | 2 | `phase1_stand/` |
| P1.4 (行走环境) | 3 | `phase1_walk/` |
| P1.5 (行走训练) | 1 | `phase1_walk/` |
| P2.1 (MoE网络) | 3 | `phase2_dagger/` |
| P2.2 (DAgger) | 2 | `phase2_dagger/` |
| P2.3 (蒸馏执行) | 1 | `phase2_dagger/` |
| P3.1 (PCGrad) | 3 | `phase3_pcgrad/` |
| P3.2 (微调训练) | 1 | `phase3_pcgrad/` |
| P3.3 (评估) | 1 | `phase3_pcgrad/` |
| **总计** | **23** | |

---

## 预计时间线

| 阶段 | 预计文件数 | 预计耗时 | 关键风险 |
|------|-----------|---------|---------|
| P1.1-P1.3 (站立) | 6 | 2-3 天 | 30° 斜坡收敛困难 |
| P1.4-P1.5 (行走) | 4 | 2-3 天 | 双足步态稳定性 |
| P2.1-P2.3 (DAgger蒸馏) | 6 | 2-3 天 | 数据集分布偏移 |
| P3.1-P3.3 (PCGrad微调) | 5 | 2-3 天 | 梯度冲突处理 |
| P.C (通用) | 2 | 0.5 天 | — |
| **总计** | **23** | **8-12 天** | |

---

## 开发约定

- 每完成一个子步骤，运行对应单元测试
- 每个 Phase 完成后，更新 `PROJECT_PLAN.md` 状态
- 所有训练日志保存在 `logs/` 下
- checkpoint 命名: `checkpoint_{phase}_{variant}.pt`
- 提交前确保 `--headless --max_steps 2` 冒烟测试通过
- 不提交 checkpoint 文件（加入 `.gitignore`）
