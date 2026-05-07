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
- `.trae/skills/trae-upload-yushu-robot/SKILL.md`：TRAE 上传工作流 skill，同样遵循 `codex` 分支上传规则。

### Git 分支规则

本仓库远端为：

```bash
https://github.com/Destiny916/yushu_robot.git
```

需要上传到 GitHub 时，统一提交并推送到 `codex` 分支：

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

该脚本会先检查 `yushu_robot_urdf/g1_29dof_mode_16.urdf` 引用的 mesh 文件是否都存在，然后生成 `model/build_robot_model/generated/g1_29dof_mode_16.usd`。当前流程只构建机器人本体，不添加动作、任务、控制器或额外场景。

`model/` 中每个独立问题或工作流都应放入自己的文件夹；当前机器人模型构建代码位于 `model/build_robot_model/`。

运行该命令需要已配置 IsaacLab/Isaac Sim Python 环境。本仓库当前使用 `D:\il\env\Scripts\python.exe`。

## 注意事项

1. **MuJoCo 兼容性**：URDF 中包含 MuJoCo 编译器配置（`<mujoco>` 标签），如需转换为 MuJoCo 格式，需取消注释 floating base joint 相关配置。
2. **碰撞模型**：大部分 link 使用原始 STL 作为碰撞体，踝关节（`*_ankle_roll_link`）使用球体简化碰撞体，肩关节使用圆柱体简化。
3. **版本标记**：部分 mesh 文件名包含 `_rev_1_0` 后缀，表示该 link 使用了 Rev 1.0 版本的几何体。
4. **手腕配置**：手腕包含 `_5010` 后缀版本的 link，对应 5010 规格的执行器。
