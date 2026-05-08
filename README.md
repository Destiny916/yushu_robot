# Yushu Robot - Unitree G1 29DOF URDF 模型

本目录包含 **宇树 Unitree G1 人形机器人（29自由度）** 的 URDF 模型资源，用于在 [NVIDIA IsaacLab](https://isaac-sim.github.io/IsaacLab/) 仿真框架中进行机器人运动控制、操作任务和强化学习训练。

## 目录结构

```
yushu_robot/
├── .codex/
│   └── skills/
│       └── yushu-robot-project/
│           └── SKILL.md              # Codex 项目工作流 skill
├── .trae/
│   └── skills/
│       └── trae-upload-yushu-robot/
│           └── SKILL.md              # TRAE 上传工作流 skill
├── model/                            # 机器人仿真、训练、验证代码
│   └── README.md                     # 仿真代码目录约定
├── PROJECT_PLAN.md                   # 项目计划书与后续交接清单
├── spec.md                           # 训练场景构建规范（Step 0-6）
└── yushu_robot_urdf/
    ├── g1_29dof_mode_16.urdf        # 主 URDF 模型文件
    ├── README_部件说明.md            # 机器人部件概览和命名规则
    └── meshes/                       # STL 网格文件（120+ 个）
        ├── pelvis.STL                # 骨盆
        ├── torso_link*.STL           # 躯干
        ├── head_link.STL             # 头部
        ├── left/right_hip_*.STL      # 髋关节
        ├── left/right_knee_*.STL     # 膝关节
        ├── left/right_ankle_*.STL    # 踝关节
        ├── left/right_shoulder_*.STL # 肩关节
        ├── left/right_elbow_*.STL    # 肘关节
        ├── left/right_wrist_*.STL    # 腕关节
        ├── left/right_hand_*.STL     # 灵巧手
        ├── left/right_*_force_sensor_*.STL  # 力传感器
        ├── d455_link.STL             # Intel RealSense D455 深度相机
        └── ...
```

## 项目工作约定

后续所有与本项目相关的任务都在 `yushu_robot/` 仓库内进行，避免把项目代码散落到外层 IsaacLab 目录。

- `yushu_robot_urdf/`：保存所有机器人本体相关信息，包括 URDF、mesh、传感器/末端执行器几何资源，以及后续新增机器人的部件文件。
- `model/`：保存用于机器人仿真的代码，包括 IsaacLab 环境配置、资产转换脚本、训练入口、评估脚本、控制器、策略加载与实验配置。
- `.codex/skills/yushu-robot-project/SKILL.md`：项目专用 Codex skill，记录工作根目录、资源边界、README 更新和 Git 上传规则。
- `.trae/skills/trae-upload-yushu-robot/SKILL.md`：TRAE 上传工作流 skill。当前本次上传按用户要求推送到 `codex` 分支。

### Git 分支规则

本仓库远端为：

```bash
https://github.com/Destiny916/yushu_robot.git
```

需要上传到 GitHub 时，当前提交并推送到 `codex` 分支：

```bash
git switch codex
git status -sb
git add <changed-files>
git commit -m "<message>"
git push origin codex
```

除非明确要求，项目相关提交不推送到 `main` 或其他分支。

## 机器人关节配置（29 DOF）

### 下肢（12 DOF）

| 关节 | 左腿 | 右腿 |
|------|------|------|
| 髋关节 Pitch | `left_hip_pitch_joint` | `right_hip_pitch_joint` |
| 髋关节 Roll | `left_hip_roll_joint` | `right_hip_roll_joint` |
| 髋关节 Yaw | `left_hip_yaw_joint` | `right_hip_yaw_joint` |
| 膝关节 | `left_knee_joint` | `right_knee_joint` |
| 踝关节 Pitch | `left_ankle_pitch_joint` | `right_ankle_pitch_joint` |
| 踝关节 Roll | `left_ankle_roll_joint` | `right_ankle_roll_joint` |

### 躯干（3 DOF）

| 关节 | 关节名 |
|------|--------|
| 腰部 Yaw | `waist_yaw_joint` |
| 腰部 Roll | `waist_roll_joint` |
| 腰部 Pitch | `waist_pitch_joint` |

### 上肢（14 DOF）

| 关节 | 左臂 | 右臂 |
|------|------|------|
| 肩关节 Pitch | `left_shoulder_pitch_joint` | `right_shoulder_pitch_joint` |
| 肩关节 Roll | `left_shoulder_roll_joint` | `right_shoulder_roll_joint` |
| 肩关节 Yaw | `left_shoulder_yaw_joint` | `right_shoulder_yaw_joint` |
| 肘关节 | `left_elbow_joint` | `right_elbow_joint` |
| 腕关节 Roll | `left_wrist_roll_joint` | `right_wrist_roll_joint` |
| 腕关节 Pitch | `left_wrist_pitch_joint` | `right_wrist_pitch_joint` |
| 腕关节 Yaw | `left_wrist_yaw_joint` | `right_wrist_yaw_joint` |

## 末端执行器

机器人末端附带 **Rubber Hand（橡胶手）** 作为基础末端执行器：
- `left_rubber_hand` — 左手（固定在 `left_wrist_yaw_link` 上）
- `right_rubber_hand` — 右手（固定在 `right_wrist_yaw_link` 上）

同时包含 **灵巧手力传感器** 网格（index/middle/ring/little/thumb force sensor），可用于力控抓取研究。

## 传感器配置

| 传感器 | 链接名 | 说明 |
|--------|--------|------|
| IMU（躯干） | `imu_in_torso` | 位于躯干，用于姿态估计 |
| IMU（骨盆） | `imu_in_pelvis` | 位于骨盆，用于基础运动状态感知 |
| 深度相机 | `d435_link` | Intel RealSense D455（安装在头部区域） |
| LiDAR | `mid360_link` | Livox Mid-360 激光雷达 |

## 材质配色

URDF 中定义了两种材质：
- **dark**（深色）：`rgba(0.2, 0.2, 0.2, 1)` — 骨盆、髋关节等主要结构件
- **white**（浅色）：`rgba(0.7, 0.7, 0.7, 1)` — 躯干、四肢连杆等部件

## 在 IsaacLab 中的集成

本 URDF 模型在 IsaacLab 项目中通过以下配置文件和任务环境进行使用：

### 核心资产配置

- **`G1_29DOF_CFG`** — G1 29DOF 机器人完整配置，定义在 [unitree.py](file:///d:/il/IsaacLab/source/isaaclab_assets/isaaclab_assets/robots/unitree.py)，采用 DC Motor 驱动腿部，ImplicitActuator 驱动手臂/手部/腰部
- **`G1_INSPIRE_FTP_CFG`** — 在 G1_29DOF 基础上适配 Inspire 五指灵巧手，用于抓取放置任务

### 已注册的仿真环境

| 环境 ID | 任务类型 | 说明 |
|---------|---------|------|
| `Isaac-Velocity-Rough-G1-v0` | 运动控制 | 粗糙地形运动 |
| `Isaac-Velocity-Flat-G1-v0` | 运动控制 | 平坦地面运动 |
| `Isaac-PickPlace-G1-InspireFTP-Abs-v0` | 抓取放置 | 灵巧手抓取任务 |
| `Isaac-PickPlace-Locomanipulation-G1-Abs-v0` | 全身移动操作 | 下肢移动 + 上肢操作 |
| `Isaac-PickPlace-FixedBaseUpperBodyIK-G1-Abs-v0` | 固定基座操作 | 上半身 IK 控制 |

### 遥操作支持

通过 OpenXR 支持 VR 遥操作重定向：
- **Inspire 五指手重定向**：`inspire/g1_upper_body_retargeter.py`
- **TriHand 三指手重定向**：`trihand/g1_upper_body_retargeter.py`
- **下半身站立控制**：`g1_lower_body_standing.py`

## 本地机器人构建

`model/` 中提供了一个最小构建脚本，用于从本仓库的 URDF 和 mesh 部件信息生成机器人 USD：

```powershell
D:\il\env\Scripts\python.exe model\build_robot_model\build_g1_from_urdf.py --headless
```

该脚本会先检查 `yushu_robot_urdf/g1_29dof_mode_16.urdf` 引用的 mesh 文件是否都存在，然后生成 `model/generatedUSD/g1_29dof_mode_16.usd`。当前流程只构建机器人本体，不添加动作、任务、控制器或额外场景。

`model/` 中每个独立问题或工作流都应放入自己的文件夹；当前机器人模型构建代码位于 `model/build_robot_model/`。全局 USD 生成资产统一保存在 `model/generatedUSD/`。

运行该命令需要已配置 IsaacLab/Isaac Sim Python 环境。本仓库当前使用 `D:\il\env\Scripts\python.exe`。

### Step 1：手动加载 Articulation

生成全局 USD 后，可以用 Step 1 脚本把机器人加载到 Isaac Sim 场景中：

```powershell
D:\il\env\Scripts\python.exe model\step1_load_articulation\step1_load_articulation.py --headless
```

该脚本位于 `model/step1_load_articulation/`，默认只创建 1 个 G1 机器人实例；若不设置 `--max_steps`，仿真会一直运行，直到应用关闭。脚本只创建地面、灯光和机器人，并用随机关节力矩做最小仿真验证，不包含任务、训练或额外场景。

### Step 2：声明式 InteractiveScene

Step 2 使用 IsaacLab 的 `InteractiveSceneCfg` 管理同样的机器人、地面和灯光：

```powershell
D:\il\env\Scripts\python.exe model\step2_create_scene\step2_create_scene.py --headless
```

该脚本位于 `model/step2_create_scene/`，默认 1 个机器人，未设置 `--max_steps` 时无限循环。

### Step 3：本地机器人配置

Step 3 将本地 G1 机器人资产配置抽取到可复用模块：

```text
model/step3_robot_cfg/g1_local_cfg.py
```

后续场景和环境代码通过 `G1_LOCAL_CFG.replace(prim_path=...)` 复用该配置，USD 路径统一指向 `model/generatedUSD/g1_29dof_mode_16.usd`。

### Step 4：Manager-Based 环境

Step 4 构建最小 Manager-Based 站立环境：

```powershell
D:\il\env\Scripts\python.exe model\step4_manager_env\run_stand_env.py --headless
```

该环境默认 1 个机器人，未设置 `--max_steps` 时无限循环；action 维度为 29，policy observation 维度为 93。

### Step 5：接触传感器

Step 5 在 Step 4 环境上追加脚踝接触传感器：

```powershell
D:\il\env\Scripts\python.exe model\step5_sensors\run_sensors_env.py --headless
```

接触传感器挂在 `{ENV_REGEX_NS}/Robot/.*ankle_roll_link`，默认单机器人输出 contact force shape 为 `(1, 2, 3)`。

### Step 6：地形系统（P1.1）

Step 6 为 AHC 训练 Phase 1 创建了 6 种地形配置，每种地形独立为一个 Python 文件：

```powershell
# 测试指定地形（headless，2步验证）
D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T0 --headless --max_steps 2
D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T1 --headless --max_steps 2
D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T3 --headless --max_steps 2
D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T4 --headless --max_steps 2
```

地形类型：

| 地形 | 文件 | 类型 | 参数 |
|------|------|------|------|
| T0 | `T0_plane.py` | 平面 | — |
| T1 | `T1_slope_10.py` | 10° 斜坡 | slope=0.175 rad |
| T2 | `T2_slope_20.py` | 20° 斜坡 | slope=0.349 rad |
| T3 | `T3_slope_30.py` | 30° 斜坡 | slope=0.524 rad |
| T4 | `T4_stairs.py` | 楼梯 | 台阶高 0.05-0.15m，步宽 0.3m |
| T5 | `T5_wave.py` | 不规则波浪 | 波幅 0.02-0.08m |

使用 `--terrain T0~T5` 切换地形，`--num_envs N` 设置环境数量。机器人静止站立在地形上，每 50 步打印高度信息。

设计文档和实施计划位于 `model/step6_train/spec/2026-05-08_g1_ahc_standing/`。

### Step 6：AHC 深度强化学习训练框架

Step 6 实现 AHC (Adaptive Humanoid Control) 多行为蒸馏训练框架，核心代码位于：

```text
model/step6_train/
├── terrains/                  # 地形系统（T0-T5，6种地形）
│   ├── T0_plane.py            # 平面
│   ├── T1_slope_10.py         # 10° 斜坡
│   ├── T2_slope_20.py         # 20° 斜坡
│   ├── T3_slope_30.py         # 30° 斜坡
│   ├── T4_stairs.py           # 楼梯
│   ├── T5_wave.py             # 不规则波浪
│   ├── __init__.py            # 地形注册表（TERRAIN_MAKERS, get_terrain_cfg）
│   └── test_terrains.py       # 地形测试脚本
├── phase1_stand/              # Phase 1 站立 PPO 训练
│   ├── stand_env_cfg.py       # 站立环境配置（奖励、终止、观察、动作）
│   ├── stand_rewards.py       # 自定义奖励函数
│   ├── stand_ppo_cfg.py       # PPO 超参数配置
│   ├── train_stand.py         # 训练入口
│   ├── test_stand_env_cfg.py  # 环境配置单元测试
│   └── test_train_stand.py    # 训练入口单元测试
└── spec/                      # 设计文档
    └── 2026-05-08_g1_ahc_standing/
        ├── spec.md            # 技术规范
        └── plan.md            # 实施计划
```

#### AHC 三阶段训练架构

AHC 方案通过三个阶段训练 G1 机器人在 6 种地形上实现站/走平滑切换：

```
Phase 1: 独立专精 PPO 训练          Phase 2: DAgger 蒸馏           Phase 3: PCGrad 微调
┌─────────────────────┐            ┌──────────────────────────┐  ┌──────────────────────────┐
│  π_stand (29DOF→29) │──┐         │  MoE Unified Policy       │  │  MoE Unified Policy       │
│  地形: T0-T5         │  │         │  ┌────────────────────┐  │  │  (端到端训练)              │
│  指令: c=1 固定       │  ├────────►│  │ Gating Network      │  │  │  ┌────────────────────┐  │
└─────────────────────┘  │         │  │ α = G(o, e, c)     │  │  │  │ Gating Network      │  │
                          │         │  └─────┬──────┬───────┘  │  │  │ α = G(o, e, c)     │  │
┌─────────────────────┐  │         │  π_stand   π_walk      │  │  │  └─────┬──────┬───────┘  │
│  π_walk (29DOF→29)  │──┘         │  (frozen)  (frozen)     │  │  │  π_stand   π_walk      │  │
│  地形: T0-T5         │            │  a = α·a_s + (1-α)·a_w │  │  │  (trainable)(trainable) │  │
└─────────────────────┘            └──────────────────────────┘  │  a = α·a_s + (1-α)·a_w │  │
                                                                  └──────────────────────────┘
```

- **Phase 1**：PPO 独立训练站立策略 π_stand 和行走策略 π_walk（当前已实现站立部分）
- **Phase 2**：DAgger 将两个专精策略蒸馏到 MoE 统一策略（Gating Network + 冻结 Experts）
- **Phase 3**：PCGrad 多任务 PPO 端到端微调，消除站/走切换时的动作突变

置信度指令 `c ∈ [0, 1]`：`c=1` 为纯站立，`c=0` 为全速行走，中间值为混合状态。

#### 深度强化学习核心逻辑（Phase 1 站立）

Phase 1 使用 **PPO (Proximal Policy Optimization)** 算法训练站立策略，核心流程：

```
┌─────────────────────────────────────────────────────────────────┐
│  PPO 训练循环 (RSL-RL OnPolicyRunner)                           │
│                                                                 │
│  1. 采集 rollout: 24 steps × N envs → (obs, action, reward)    │
│  2. 计算 GAE (γ=0.99, λ=0.95) 优势估计                         │
│  3. 分 4 个 mini-batch, 5 个 epoch 更新:                        │
│     - Actor Loss:  clip(ratio, 1±0.2) * advantage              │
│     - Critic Loss: MSE(V_pred, V_target)                       │
│     - Entropy Bonus: 0.01 * entropy (鼓励探索)                  │
│  4. 自适应学习率: KL 散度 > 0.01 则降低 lr                      │
│  5. 每 50 iteration 保存 checkpoint                             │
└─────────────────────────────────────────────────────────────────┘
```

**观察空间** (93 维)：

| 观察项 | 维度 | 说明 |
|--------|------|------|
| `base_ang_vel` | 3 | 基座角速度（本体坐标系） |
| `projected_gravity` | 3 | 重力在基座坐标系的投影（姿态感知） |
| `joint_pos_rel` | 29 | 关节位置相对默认姿态的偏差 |
| `joint_vel_rel` | 29 | 关节速度 |
| `last_action` | 29 | 上一步动作（动作平滑性） |
| **合计** | **93** | |

**动作空间** (29 维)：29 个关节的位置目标，`scale=0.25` 缩放，使用默认姿态作为偏移。

**仿真参数**：`dt=0.005s`，`decimation=4`，策略频率 50Hz，episode 长度 30s。

#### 奖励函数设计

站立奖励函数由 11 项组成，平衡稳定性、能效和平滑性：

| 奖励项 | 权重 | 类型 | 设计意图 |
|--------|------|------|---------|
| `is_alive` | **+1.0** | 正向 | 每步存活奖励，鼓励机器人保持站立不倒 |
| `flat_orientation_l2` | **-2.0** | 姿态 | 躯干倾斜惩罚，投影重力与垂直方向偏差的 L2 范数 |
| `base_height_l2` | **-1.0** | 姿态 | 质心高度偏差惩罚，目标高度 0.78m（G1 自然站立高度） |
| `lin_vel_xy_l2` | **-1.5** | 稳定 | 水平速度惩罚，站立时基座不应有水平移动 |
| `ang_vel_xy_l2` | **-0.5** | 稳定 | 角速度惩罚，防止躯干晃动 |
| `joint_torques_l2` | **-2.5e-5** | 能效 | 关节力矩惩罚，降低能耗，权重极小避免过度影响 |
| `joint_vel_l2` | **-1.0e-3** | 平滑 | 关节速度惩罚，鼓励平稳运动 |
| `joint_acc_l2` | **-2.5e-7** | 平滑 | 关节加速度惩罚，权重极小，防止关节抖动 |
| `action_rate_l2` | **-0.01** | 平滑 | 动作变化率惩罚，相邻步动作不应剧烈变化 |
| `joint_deviation_l1` | **-0.1** | 姿态 | 关节偏离默认姿态惩罚，L1 范数鼓励回到自然姿态 |
| `termination_penalty` | **-200.0** | 终止 | 掉倒终止惩罚，极大负奖励使策略极力避免失败 |

**奖励设计原则**：
- **正向奖励稀疏**：仅有 `is_alive(+1)` 提供持续正向信号，迫使策略通过避免惩罚来获得高回报
- **终止惩罚极大**：`-200.0` 的终止惩罚相当于 200 步存活奖励被清零，策略必须学会不倒
- **能效权重极小**：`joint_torques_l2(-2.5e-5)` 和 `joint_acc_l2(-2.5e-7)` 权重极小，仅起正则化作用，不主导学习
- **姿态约束适中**：`flat_orientation_l2(-2.0)` 权重最高（除终止外），确保躯干保持直立

#### 终止条件

| 条件 | 阈值 | 说明 |
|------|------|------|
| `bad_orientation` | > 45° (0.785 rad) | 躯干倾斜过大，视为即将摔倒 |
| `root_height_below_minimum` | < 0.45m | 质心过低，可能已蹲下或摔倒 |
| `joint_pos_out_of_limit` | 软限位 | 任一关节超出安全范围 |
| `time_out` | 30s (1500 steps) | episode 自然结束 |

#### PPO 网络架构

```
Actor (策略网络):
  Input(93) → Linear(512) → ELU → Linear(256) → ELU → Linear(128) → ELU → Linear(29) → tanh

Critic (价值网络):
  Input(93) → Linear(512) → ELU → Linear(256) → ELU → Linear(128) → ELU → Linear(1)
```

| 参数 | 值 |
|------|-----|
| Actor 隐藏层 | [512, 256, 128] |
| Critic 隐藏层 | [512, 256, 128] |
| 激活函数 | ELU |
| 学习率 | 1e-3（自适应） |
| Clip 参数 | 0.2 |
| 熵系数 | 0.01 |
| GAE γ | 0.99 |
| GAE λ | 0.95 |
| Mini-batch 数 | 4 |
| Learning epoch 数 | 5 |
| 每环境步数 | 24 |
| 最大迭代数 | 1500 |
| Checkpoint 间隔 | 50 iterations |

#### 站立训练命令

验证环境配置：

```powershell
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_stand_env_cfg.py -v
D:\il\env\Scripts\python.exe -B model\step6_train\phase1_stand\test_train_stand.py -v
```

短训练冒烟：

```powershell
D:\il\env\Scripts\python.exe model\step6_train\phase1_stand\train_stand.py --headless --num_envs 64 --max_iterations 100 --run_name smoke
```

指定地形训练：

```powershell
D:\il\env\Scripts\python.exe model\step6_train\phase1_stand\train_stand.py --headless --terrain T0 --num_envs 8 --max_iterations 20 --save_interval 5 --run_name T0_2env
```

完整站立 PPO 训练：

```powershell
D:\il\env\Scripts\python.exe model\step6_train\phase1_stand\train_stand.py --headless --num_envs 4096 --max_iterations 1500
```

续训（从已有 checkpoint 恢复）：

```powershell
D:\il\env\Scripts\python.exe model\step6_train\phase1_stand\train_stand.py `
  --headless `
  --terrain T1 `
  --num_envs 2 `
  --max_iterations 100 `
  --save_interval 10 `
  --resume `
  --load_run <run文件夹名> `
  --checkpoint model_15.pt `
  --run_name T1_resume
```

训练输出位于 `logs/rsl_rl/g1_stand/<timestamp>/`。RSL-RL 原始 checkpoint 命名为 `model_*.pt`；训练结束后，最新 checkpoint 会复制为 `checkpoint_stand.pt`，可用于后续续训。

#### 训练 CLI 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--terrain` | T0 | 地形类型：T0-T5 |
| `--num_envs` | 1 | 并行环境数 |
| `--max_iterations` | 1500 | PPO 训练迭代数 |
| `--save_interval` | 50 | Checkpoint 保存间隔 |
| `--run_name` | — | 运行目录后缀 |
| `--resume` | false | 从 checkpoint 续训 |
| `--load_run` | — | 续训的 run 目录名 |
| `--checkpoint` | model_*.pt | 续训的 checkpoint 文件名 |
| `--logger` | tensorboard | 日志后端：tensorboard/wandb/neptune |
| `--seed` | 42 | 随机种子 |

## 注意事项

1. **MuJoCo 兼容性**：URDF 中包含 MuJoCo 编译器配置（`<mujoco>` 标签），如需转换为 MuJoCo 格式，需取消注释 floating base joint 相关配置。
2. **碰撞模型**：大部分 link 使用原始 STL 作为碰撞体，踝关节（`*_ankle_roll_link`）使用球体简化碰撞体，肩关节使用圆柱体简化。
3. **版本标记**：部分 mesh 文件名包含 `_rev_1_0` 后缀，表示该 link 使用了 Rev 1.0 版本的几何体。
4. **手腕配置**：手腕包含 `_5010` 后缀版本的 link，对应 5010 规格的执行器。
