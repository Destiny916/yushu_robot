# G1 AHC 多行为蒸馏站立训练 — 技术规范 (Spec)

> 版本: v1.0 | 日期: 2026-05-08 | 作者: yushu_robot 项目组
>
> 目标: 基于 AHC (Adaptive Humanoid Control) 方案，训练 Unitree G1 29DOF 人形机器人在多地形上稳定站立，并通过多行为蒸馏实现站/走平滑切换。

---

## 1. 目标与范围

### 1.1 核心目标

训练 G1 机器人具备以下能力:

1. **多地形站立**: 在 6 种地形上保持稳定站立姿态（不倒、不滑、不超关节限位）
2. **速度指令跟随**: 根据连续置信度指令 `c ∈ [0, 1]`，实现站立 (`c=1`) 到全速行走 (`c=0`) 的平滑过渡
3. **跨地形泛化**: 在未见地形变体上保持站立/行走能力

### 1.2 地形规格

| 编号 | 地形类型 | 占比 | 关键参数 |
|------|---------|------|---------|
| T0 | 平面 (Plane) | 20% | — |
| T1 | 10° 斜坡 (Slope) | 20% | 坡度 = 0.175 rad，金字塔形 |
| T2 | 20° 斜坡 (Slope) | 20% | 坡度 = 0.349 rad，金字塔形 |
| T3 | 30° 斜坡 (Slope) | 15% | 坡度 = 0.524 rad，金字塔形 |
| T4 | 楼梯 (Stairs) | 15% | 台阶高 0.05–0.15m，步宽 0.3m |
| T5 | 不规则斜坡 (Wave) | 10% | 波幅 0.02–0.08m |

总计: 6 种地形类型，按比例混合。

### 1.3 指令接口

- **置信度指令** `c ∈ [0, 1]`: 连续值
  - `c = 1.0`: 纯站立（零速度）
  - `c = 0.0`: 全速行走（最大速度）
  - `0 < c < 1`: 站/走混合，速度按 `(1-c)` 线性缩放
- **行走速度基准**: `v_x ∈ [0, 1.0] m/s`，`v_y = 0`，`ω_z ∈ [-1.0, 1.0] rad/s`
- 实际目标速度 = `(1-c) * [v_x_target, 0, ω_z_target]`

---

## 2. AHC 三阶段方案

### 2.1 总体架构

```
Phase 1: 独立专精训练 (PPO)       Phase 2: DAgger 蒸馏           Phase 3: PCGrad 微调
┌─────────────────────┐          ┌──────────────────────────┐  ┌──────────────────────────┐
│  π_stand (29DOF→29) │──┐       │  MoE Unified Policy       │  │  MoE Unified Policy       │
│  地形: T0-T5         │  │       │                          │  │  (端到端训练)              │
│  指令: c=1 固定       │  │       │  ┌────────────────────┐  │  │                          │
└─────────────────────┘  │       │  │ Gating Network      │  │  │  ┌────────────────────┐  │
                          ├──────►│  │ α = G(o, e, c)     │  │  │  │ Gating Network      │  │
┌─────────────────────┐  │       │  │ α ∈ [0, 1]          │  │  │  │ α = G(o, e, c)     │  │
│  π_walk (29DOF→29)  │──┘       │  └─────┬──────┬───────┘  │  │  │  │ (trainable)         │  │
│  地形: T0-T5         │          │        │      │          │  │  └─────┬──────┬───────┘  │
│  指令: c∈[0,1] 随机   │          │  π_stand   π_walk      │  │  │        │      │          │
└─────────────────────┘          │  (frozen)  (frozen)     │  │  │  π_stand   π_walk      │  │
                                 │  a = α·a_s + (1-α)·a_w │  │  │  (trainable)(trainable) │  │
                                 └──────────────────────────┘  │  a = α·a_s + (1-α)·a_w │  │
                                          │                    └──────────────────────────┘
                                     DAgger 数据聚合:                  │
                                     学生执行 → 教师纠正              PCGrad 梯度修改:
                                     → 聚合数据集训练门控              cos(∇L_s, ∇L_w) < 0
                                                                      → 投影去冲突
```

### 2.2 Phase 1 — 独立专精 PPO 训练

**目标**: 训练两个独立的专精策略，分别擅长站立和行走。

**站立策略 π_stand**:
- 环境: `G1StandEnvCfg` 扩展，添加 6 种地形 + 奖励函数
- 指令: `c = 1.0` 固定（零速度指令）
- 观察空间: 93 维（base_ang_vel, projected_gravity, joint_pos_rel, joint_vel_rel, last_action, terrain_info）
- 动作空间: 29 维关节位置目标
- 训练步数: 目标 ~1500 iterations × 4096 envs
- 输出: `checkpoint_stand.pt`

**走路策略 π_walk**:
- 环境: 基于 `LocomotionVelocityRoughEnvCfg` 适配 G1
- 指令: `c ∈ [0, 1]` 随机采样（对应不同速度）
- 观察空间: 同上 + velocity_commands
- 动作空间: 29 维关节位置目标
- 训练步数: 目标 ~2000 iterations × 4096 envs
- 输出: `checkpoint_walk.pt`

**共享要素**:
- 机器人配置: `G1_LOCAL_CFG` (step3)
- 传感器: 脚踝接触力传感器 (step5)
- 仿真参数: `dt=0.005s`, `decimation=4` (策略频率 50Hz)

### 2.3 Phase 2 — DAgger 知识蒸馏

**目标**: 将两个专精策略蒸馏到一个 MoE 统一策略中。

**MoE 策略结构**:

```
输入层:
  observation (93 维)
  terrain_embedding (8 维，地形类型 one-hot 编码后的学习嵌入)
  confidence_c (1 维，目标置信度)

Gating Network:
  concat([obs, terrain_emb, c]) → Linear(102→256) → ELU → Linear(256→128) → ELU → Linear(128→1) → Sigmoid
  输出: α ∈ [0, 1]

Expert Networks (frozen from Phase 1):
  π_stand: ActorCritic 网络（权重冻结）
  π_walk: ActorCritic 网络（权重冻结）

混合输出:
  action = α * π_stand.actor(obs) + (1-α) * π_walk.actor(obs)
  value  = α * π_stand.critic(obs) + (1-α) * π_walk.critic(obs)
```

**DAgger 流程**:

```
for round in 1..K:                     # K=10 轮迭代
    for each terrain_type:             # 6 种地形
        for c in [0.0, 0.25, 0.5, 0.75, 1.0]:
            1. 学生 (Gating + frozen experts) 执行 rollout，收集 (obs, action_student)
            2. 教师 (最优专家) 对同一 obs 给出 action_teacher:
               - 如果 c >= 0.5: teacher = π_stand
               - 如果 c <  0.5: teacher = π_walk
            3. 将 (obs, terrain, c, action_teacher) 加入数据集 D
    在聚合数据集 D 上训练 Gating Network (BC Loss):
      L = MSE(α_pred, α_teacher)
      其中 α_teacher = c（置信度直接监督 α）
    D = D ∪ 本轮新增数据
```

**训练细节**:
- BC Loss: `MSE(α_pred, c_target)`
- 优化器: Adam, lr=1e-3
- 批次大小: 4096
- 总数据量: ~10 轮 × 6 地形 × 5 置信度 × 4096 envs × 24 steps ≈ 30M transitions
- 输出: `checkpoint_moe_dagger.pt`

### 2.4 Phase 3 — PCGrad 多任务 PPO 微调

**目标**: 端到端微调 MoE 策略，使站立和行走间的切换更平滑，消除门控网络与专家网络之间的不协调。

**PCGrad 流程**:

```
for iteration in 1..M:                # M=500 iterations
    1. 采样两个 mini-batch:
       - B_stand: c ~ Uniform(0.5, 1.0)  # 偏站立
       - B_walk:  c ~ Uniform(0.0, 0.5)  # 偏行走
    2. 分别计算梯度:
       - g_stand = ∇L_PPO(B_stand)   # 站立目标
       - g_walk  = ∇L_PPO(B_walk)    # 行走目标
    3. PCGrad 去冲突:
       if cos(g_stand, g_walk) < 0:  # 梯度冲突
           g_stand = g_stand - proj(g_stand, g_walk)  # 投影到 g_walk 法平面
           g_walk  = g_walk  - proj(g_walk, g_stand)
    4. g_final = g_stand + g_walk
    5. optimizer.step(g_final)
```

**PPO 配置** (与 Phase 1 相似):
- 隐藏层: Gate=[256,128], Actor=[512,256,128], Critic=[512,256,128]
- 学习率: 1e-4 (低于 Phase 1，更精细)
- 迭代数: 500
- 输出: `checkpoint_moe_final.pt`

---

## 3. 环境配置规范

### 3.1 自定义地形生成器

新建 `G1_STAND_TERRAINS_CFG`，继承 `TerrainGeneratorCfg`:

```python
G1_STAND_TERRAINS_CFG = TerrainGeneratorCfg(
    curriculum=True,         # 按难度排列行
    size=(8.0, 8.0),         # 每个子地形 8x8m
    num_rows=10,             # 10 个难度等级
    num_cols=6,              # 6 种地形类型
    border_width=20.0,       # 安全边界
    horizontal_scale=0.1,
    vertical_scale=0.005,
    sub_terrains={
        "flat": MeshPlaneTerrainCfg(proportion=0.20),
        "slope_10": HfPyramidSlopedTerrainCfg(
            proportion=0.20, slope_range=(0.175, 0.175)
        ),
        "slope_20": HfPyramidSlopedTerrainCfg(
            proportion=0.20, slope_range=(0.349, 0.349)
        ),
        "slope_30": HfPyramidSlopedTerrainCfg(
            proportion=0.15, slope_range=(0.524, 0.524)
        ),
        "stairs": HfPyramidStairsTerrainCfg(
            proportion=0.15,
            step_height_range=(0.05, 0.15),
            step_width=0.3,
        ),
        "wave": HfWaveTerrainCfg(
            proportion=0.10,
            amplitude_range=(0.02, 0.08),
            num_waves=2,
        ),
    },
)
```

### 3.2 站立环境配置 (Phase 1)

`G1StandEnvCfg` 基于当前 step4 的 `G1StandEnvCfg` 扩展:

| 组件 | 配置 |
|------|------|
| 场景 | `G1StandSceneCfg`，`terrain=TerrainImporterCfg(terrain_type="generator", terrain_generator=G1_STAND_TERRAINS_CFG)` |
| 观察 | 标准 policy obs (93维) + `terrain_info` (地形类型 one-hot 编码 6维) |
| 动作 | `JointPositionActionCfg`，29DOF，`scale=0.25` |
| 奖励 | 见 §4.1 |
| 终止 | 见 §4.2 |
| 指令 | 见 §4.3 |

### 3.3 走路环境配置 (Phase 1)

基于 `LocomotionVelocityRoughEnvCfg` 适配:

| 组件 | 配置 |
|------|------|
| 机器人 | `G1_LOCAL_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")` |
| 地形 | 同 `G1_STAND_TERRAINS_CFG` |
| 指令 | `UniformVelocityCommandCfg`，`c` 控制速度缩放 |
| 奖励 | 速度追踪 + 站立项（同 G1Rough 奖励结构） |

---

## 4. 奖励函数与终止条件

### 4.1 站立奖励函数

| 奖励项 | 权重 | 说明 |
|--------|------|------|
| `is_alive` | +1.0 | 未触发终止条件 |
| `flat_orientation_l2` | -2.0 | 躯干倾斜惩罚（投影重力与垂直方向偏差） |
| `base_height_l2` | -1.0 | 质心高度偏差（目标: 0.78m） |
| `lin_vel_xy_l2` | -1.5 | 基座水平速度惩罚（站立时应为 0） |
| `ang_vel_xy_l2` | -0.5 | 基座角速度惩罚 |
| `joint_torques_l2` | -2.5e-5 | 力矩惩罚（节能） |
| `joint_vel_l2` | -1.0e-3 | 关节速度惩罚 |
| `joint_acc_l2` | -2.5e-7 | 关节加速度惩罚（平滑） |
| `action_rate_l2` | -0.01 | 动作变化率惩罚 |
| `joint_deviation_l1` | -0.1 | 关节偏离默认姿态惩罚 |
| `feet_contact_symmetry` | -0.5 | 双脚接触力不对称惩罚 |
| `termination_penalty` | -200.0 | 掉倒终止惩罚 |

### 4.2 终止条件

| 条件 | 阈值 |
|------|------|
| `bad_orientation` | 躯干倾斜 > 45° (0.785 rad) |
| `root_height_below_minimum` | 质心高度 < 0.45m |
| `joint_pos_out_of_limit` | 任一关节超出软限位 |
| `time_out` | episode_length = 20s (1000 steps @ 50Hz) |
| `illegal_contact` | 躯干/头部接触力 > 100N |

### 4.3 行走奖励函数

沿用 `G1Rewards` 结构，额外增加:

| 奖励项 | 权重 | 说明 |
|--------|------|------|
| `track_lin_vel_xy_yaw_frame_exp` | 1.0 | 速度追踪（主要奖励） |
| `track_ang_vel_z_world_exp` | 2.0 | 角速度追踪 |
| `feet_air_time_positive_biped` | 0.25 | 双足步态周期奖励 |
| `stand_still_joint_deviation_l1` | -0.2 | 低速时保持姿态（与站立衔接关键） |

---

## 5. 网络架构细节

### 5.1 Phase 1 专精策略

**站立 Actor**:
```
Input(93) → Linear(512) → ELU → Linear(256) → ELU → Linear(128) → ELU → Linear(29) → tanh → action
```

**站立 Critic**:
```
Input(93) → Linear(512) → ELU → Linear(256) → ELU → Linear(128) → ELU → Linear(1) → value
```

**走路 Actor/Critic**: 相同结构，输入维度增加 `velocity_commands(3) = 96`

### 5.2 Phase 2 MoE 策略

**Gating Network**:
```
Input: concat[obs(93/96), terrain_embedding(8), c(1)]
       → Linear(256) → ELU → Linear(128) → ELU → Linear(1) → Sigmoid → α
```

**Expert Networks**: 直接加载 Phase 1 的 Actor 权重并冻结。

**输出混合**:
```
action = α * π_stand.actor(obs) + (1-α) * π_walk.actor(obs)
```

### 5.3 Phase 3 端到端 MoE

**结构同 Phase 2**，但所有网络权重（Gating + Actor + Critic）均可训练。PCGrad 作用于两个任务批次的完整梯度向量。

---

## 6. 文件组织

```
model/step6_train/
├── spec/
│   └── 2026-05-08_g1_ahc_standing/
│       ├── spec.md                         # 本文件
│       └── plan.md                         # 实施计划
├── terrains/
│   ├── __init__.py
│   └── g1_stand_terrains_cfg.py            # G1_STAND_TERRAINS_CFG
├── phase1_stand/
│   ├── __init__.py
│   ├── stand_env_cfg.py                    # 站立环境配置
│   ├── stand_rewards.py                    # 站立奖励/终止
│   ├── stand_ppo_cfg.py                    # 站立 PPO 超参数
│   ├── train_stand.py                      # 站立训练入口
│   └── test_stand_env.py                   # 站立环境测试
├── phase1_walk/
│   ├── __init__.py
│   ├── walk_env_cfg.py                     # 行走环境配置
│   ├── walk_ppo_cfg.py                     # 行走 PPO 超参数
│   ├── train_walk.py                       # 行走训练入口
│   └── test_walk_env.py                    # 行走环境测试
├── phase2_dagger/
│   ├── __init__.py
│   ├── moe_policy.py                       # MoE 策略架构 (Gating + Experts)
│   ├── gating_network.py                   # 门控网络定义
│   ├── dagger_trainer.py                   # DAgger 数据聚合训练器
│   ├── dagger_cfg.py                       # DAgger 超参数配置
│   ├── run_dagger.py                       # DAgger 训练入口
│   └── test_moe.py                         # MoE 推理测试
├── phase3_pcgrad/
│   ├── __init__.py
│   ├── pcgrad_trainer.py                   # PCGrad PPO 训练器
│   ├── pcgrad_cfg.py                       # PCGrad 超参数配置
│   ├── run_pcgrad.py                       # PCGrad 训练入口
│   └── test_pcgrad.py                      # PCGrad 测试
└── common/
    ├── __init__.py
    ├── terrain_utils.py                    # 地形工具函数
    └── policy_utils.py                     # 策略保存/加载工具
```

---

## 7. 成功标准

### 7.1 Phase 1 验收标准

| 指标 | 站立策略 | 走路策略 |
|------|---------|---------|
| 训练完成 | 1500 iterations 无崩溃 | 2000 iterations 无崩溃 |
| 存活率 (flat) | > 95% (20s episode) | > 90% |
| 存活率 (30° slope) | > 80% | > 70% |
| 姿态偏差 | roll/pitch < 5° | roll/pitch < 15° |
| 速度追踪 (走路) | — | avg error < 0.2 m/s |

### 7.2 Phase 2 验收标准

| 指标 | 目标 |
|------|------|
| α 预测 MSE | < 0.05 |
| 站立地形存活率 (MoE, c=1) | > 90% |
| 行走速度追踪 (MoE, c=0) | avg error < 0.3 m/s |
| 中间态 (c=0.5) 存活率 | > 80% |

### 7.3 Phase 3 验收标准

| 指标 | 目标 |
|------|------|
| 站立存活率（持平/优于 Phase 2） | > 90% |
| 行走速度追踪（持平/优于 Phase 2） | avg error < 0.3 m/s |
| 切换平滑度 | c ∈ [0,1] 连续变化时，动作无突变 (|Δa|/|Δc| < 阈值) |
| 梯度冲突率 | PCGrad 后冲突率 < 30% |

---

## 8. 已知风险与缓解

| 风险 | 概率 | 缓解措施 |
|------|------|---------|
| 30° 斜坡站立不稳定 | 高 | 降低 initial pose 高度、增大脚踝刚度 |
| DAgger 数据集分布偏移 | 中 | 多轮迭代聚合 + 数据重采样 |
| MoE 模型容量不足 | 低 | Gate 网络可扩展至 512 隐藏层 |
| PCGrad 训练不稳定 | 中 | 从低学习率开始，逐步增大 |
| 阶段依赖链过长 | 中 | 每阶段独立保存 checkpoint，可独立验证 |
| Windows Isaac Sim 5.1 关闭挂死 | 高 | 训练结束直接 `os._exit(0)`，避免 SimulationApp.close() |

---

## 9. 依赖关系

```
Phase 1 站立 ──→ Phase 2 DAgger ──→ Phase 3 PCGrad
Phase 1 走路 ──┘
```

- Step 0-5 (已完成): URDF → USD → Articulation → Scene → Config → Env → Sensors
- Phase 1 站立 + 走路可**并行开发**
- Phase 2 依赖 Phase 1 的两个 checkpoint
- Phase 3 依赖 Phase 2 的 MoE checkpoint

---

## 10. 环境要求

| 项目 | 值 |
|------|-----|
| Python | `D:\il\env\Scripts\python.exe` |
| IsaacLab | `d:\il\IsaacLab` |
| RSL-RL | 已集成于 IsaacLab |
| GPU | NVIDIA GPU (CUDA) |
| 并行环境数 | 4096 (训练), 1 (测试) |
