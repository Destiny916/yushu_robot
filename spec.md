# Yushu Robot 训练场景构建规范

> 目标：基于 Unitree G1 29DOF URDF 模型，在 IsaacLab 中逐步构建完整的机器人训练场景。
> 每一步产出一个可独立运行的 Python 脚本，放在 `model/` 对应子目录下。
> 脚本风格参照 `scripts/tutorials/` 的递进模式。

---

## 现状

| 已完成 | 位置 |
|--------|------|
| URDF + 120+ STL mesh | `yushu_robot_urdf/g1_29dof_mode_16.urdf` |
| URDF → USD 转换脚本 | `model/build_robot_model/build_g1_from_urdf.py` |
| 路径管理 / mesh 校验工具 | `model/build_robot_model/robot_asset.py` |
| 单元测试 | `model/build_robot_model/test_robot_asset.py` |
| Step 1 手动 Articulation 加载 | `model/step1_load_articulation/step1_load_articulation.py` |
| Step 2 声明式场景 | `model/step2_create_scene/step2_create_scene.py` |
| Step 3 本地 ArticulationCfg | `model/step3_robot_cfg/g1_local_cfg.py` |
| Step 4 Manager-Based 环境 | `model/step4_manager_env/run_stand_env.py` |
| Step 5 接触传感器 | `model/step5_sensors/run_sensors_env.py` |

未完成：训练入口。

---

## 步骤总览

```
Step 0  构建 USD 资产（已有，验证即可）
Step 1  加载机器人到场景 ── 手动 Articulation 模式
Step 2  声明式场景 ── InteractiveSceneCfg
Step 3  定义本地 ArticulationCfg（关节 / 执行器 / 物理参数）
Step 4  Manager-Based 环境 ── 观测 + 动作 + 事件
Step 5  传感器集成（接触传感器 / 相机）
Step 6  训练入口 ── RSL-RL / rl_games PPO
```

每步对应一个 Python 脚本，可独立 `--headless` 运行。

---

## Step 0 — 验证 USD 资产构建

**目的**：确认 URDF → USD 转换正常，USD 可被 Isaac Sim 加载。

**输入**：`yushu_robot_urdf/g1_29dof_mode_16.urdf`

**输出**：`model/generatedUSD/g1_29dof_mode_16.usd`

**脚本**：`model/build_robot_model/build_g1_from_urdf.py`（已有）

**验证命令**：

```powershell
D:\il\env\Scripts\python.exe model\build_robot_model\build_g1_from_urdf.py --headless
D:\il\env\Scripts\python.exe -m pytest model/build_robot_model/test_robot_asset.py -v
```

**完成标准**：
- USD 文件成功生成在全局 `model/generatedUSD/` 目录
- 所有单元测试通过
- 无 mesh 缺失警告

---

## Step 1 — 加载机器人到场景（手动 Articulation）

**目的**：用最底层 API 将 G1 机器人加载进 Isaac Sim，验证关节可驱动。

**参照**：`tutorials/01_assets/run_articulation.py`

**新脚本**：`model/step1_load_articulation/step1_load_articulation.py`

**核心逻辑**：

```
1. AppLauncher 启动 Isaac Sim
2. 创建 SimulationContext
3. 手动放置地面 + 灯光
4. 从生成的 USD 创建 Articulation（手动定义 ArticulationCfg）
5. 仿真循环：每 500 步重置，施加随机关节力矩
```

**关键配置**：

```python
G1_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path="<generated_usd_path>",
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            max_depenetration_velocity=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True,
            solver_position_iteration_count=4,
            solver_velocity_iteration_count=0,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.78),   # G1 站立高度约 0.78m
        joint_pos={...},          # 所有关节默认 0
    ),
    actuators={
        "legs": ImplicitActuatorCfg(
            joint_names_expr=[".*_hip_.*", ".*_knee_.*", ".*_ankle_.*"],
            effort_limit_sim=200.0,
            stiffness=200.0,
            damping=10.0,
        ),
        "waist": ImplicitActuatorCfg(
            joint_names_expr=["waist_.*"],
            effort_limit_sim=100.0,
            stiffness=200.0,
            damping=10.0,
        ),
        "arms": ImplicitActuatorCfg(
            joint_names_expr=[".*_shoulder_.*", ".*_elbow_.*", ".*_wrist_.*"],
            effort_limit_sim=50.0,
            stiffness=100.0,
            damping=5.0,
        ),
    },
)
```

**验证标准**：
- 默认只加载 1 个机器人；若不设置 `--max_steps`，仿真无限循环
- 脚本 `--headless --num_envs 1` 无报错运行
- 机器人在仿真中保持站立不倒
- 随机力矩可驱动关节运动

**当前验证命令**：

```powershell
D:\il\env\Scripts\python.exe model\step1_load_articulation\step1_load_articulation.py --headless --num_envs 2 --max_steps 2
```

说明：当前 Windows + Isaac Sim 5.1 环境在 `SimulationApp.close()` 关闭 stage 时可能挂住，因此 Step 1 的有界运行默认在完成 `--max_steps` 后直接退出。若需要专门检查正常关闭路径，可额外传入 `--graceful_close`。

---

## Step 2 — 声明式场景（InteractiveSceneCfg）

**目的**：用 `InteractiveSceneCfg` 替代手动管理，支持多环境并行。

**参照**：`tutorials/02_scene/create_scene.py`

**新脚本**：`model/step2_create_scene/step2_create_scene.py`

**核心逻辑**：

```
1. AppLauncher 启动
2. 定义 G1SceneCfg（@configclass）
   - ground: GroundPlaneCfg
   - dome_light: DomeLightCfg
   - robot: G1 ArticulationCfg（Step 1 的配置，prim_path 用 {ENV_REGEX_NS}/Robot）
3. 创建 SimulationContext + InteractiveScene
4. 仿真循环：使用 scene.write_data_to_sim() / scene.update()
```

**场景配置**：

```python
@configclass
class G1SceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(
        prim_path="/World/GroundPlane",
        spawn=sim_utils.GroundPlaneCfg(),
    )
    dome_light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75)),
    )
    robot: ArticulationCfg = G1_CFG.replace(
        prim_path="{ENV_REGEX_NS}/Robot",
    )
```

**验证标准**：
- 默认只加载 1 个机器人；若不设置 `--max_steps`，仿真无限循环
- `--num_envs 1` 可正常运行
- 机器人实例可独立站立
- `scene.env_origins` 正确计算环境偏移

**当前验证命令**：

```powershell
D:\il\env\Scripts\python.exe model\step2_create_scene\step2_create_scene.py --headless --max_steps 2
```

---

## Step 3 — 定义本地 ArticulationCfg

**目的**：将机器人配置从脚本中提取为独立的可复用配置模块。

**参照**：`isaaclab_assets/robots/unitree.py` 中的 `G1_29DOF_CFG`

**新文件**：`model/step3_robot_cfg/g1_local_cfg.py`

**内容**：

```
1. 定义 G1_LOCAL_CFG：基于 Step 1/2 中验证通过的配置
   - 使用本地 generated USD 路径（而非 Nucleus 远程路径）
   - 执行器分组：legs / feet / waist / arms
   - 关节正则匹配：".*_hip_yaw_joint" 等
   - 差异化刚度/阻尼参数
2. 提供 .replace() 便捷方法用于不同场景
3. 导出为模块级常量
```

**执行器分组参考**（基于 URDF 关节 limit）：

| 分组 | 关节匹配 | effort_limit | stiffness | damping |
|------|---------|-------------|-----------|---------|
| legs | `.*_hip_(pitch\|roll)_joint`, `.*_knee_joint` | 139 | 200 | 10 |
| feet | `.*_ankle_.*_joint`, `.*_hip_yaw_joint` | 35~88 | 100 | 5 |
| waist | `waist_.*_joint` | 35~88 | 200 | 10 |
| arms | `.*_shoulder_.*`, `.*_elbow_.*`, `.*_wrist_.*` | 13~25 | 50 | 3 |

**验证标准**：
- 可被 Step 2 脚本 import 替换使用
- 机器人站立姿态稳定
- 关节不过载（检查 effort 不超 limit）

**当前验证命令**：

```powershell
D:\il\env\Scripts\python.exe -B -m unittest test_g1_local_cfg -v
D:\il\env\Scripts\python.exe model\step2_create_scene\step2_create_scene.py --headless --max_steps 2
```

---

## Step 4 — Manager-Based 环境

**目的**：构建完整的 Manager-Based RL 环境，定义观测、动作、事件。

**参照**：`tutorials/03_envs/create_cartpole_base_env.py`

**新文件**：

| 文件 | 用途 |
|------|------|
| `model/step4_manager_env/stand_env_cfg.py` | 站立任务环境配置 |
| `model/step4_manager_env/run_stand_env.py` | 运行入口（交互式测试） |

**环境配置结构**：

```python
@configclass
class G1StandSceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(...)
    robot: ArticulationCfg = G1_LOCAL_CFG.replace(...)

@configclass
class ActionsCfg:
    joint_pos = mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=[".*"],       # 全部 29 DOF
        scale=0.25,
        use_default_offset=True,
    )

@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        base_lin_vel = ObsTerm(func=mdp.base_lin_vel)
        base_ang_vel = ObsTerm(func=mdp.base_ang_vel)
        projected_gravity = ObsTerm(func=mdp.projected_gravity)
        joint_pos_rel = ObsTerm(func=mdp.joint_pos_rel)
        joint_vel_rel = ObsTerm(func=mdp.joint_vel_rel)
        last_action = ObsTerm(func=mdp.last_action)
    policy: PolicyCfg = PolicyCfg()

@configclass
class EventCfg:
    reset_base = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={"pose_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5)},
                "velocity_range": {}},
    )
    reset_joints = EventTerm(
        func=mdp.reset_joints_by_default,
        mode="reset",
    )

@configclass
class G1StandEnvCfg(ManagerBasedRLEnvCfg):
    scene = G1StandSceneCfg(num_envs=args_cli.num_envs, env_spacing=2.5)
    observations = ObservationsCfg()
    actions = ActionsCfg()
    events = EventCfg()
    # 奖励、终止条件后续补充
```

**验证标准**：
- 默认只加载 1 个机器人；若不设置 `--max_steps`，仿真无限循环
- `run_stand_env.py --headless --max_steps 2` 无报错
- `env.step()` 返回 shape 为 `(1, 93)` 的 policy observation
- Action manager 输出 29 维动作

---

## Step 5 — 传感器集成

**目的**：为机器人添加接触传感器，用于后续奖励计算。相机作为可选增强，等稳定 camera prim 确认后再加入。

**参照**：`tutorials/04_sensors/add_sensors_on_robot.py`

**新文件**：

| 文件 | 用途 |
|------|------|
| `model/step5_sensors/sensors_cfg.py` | 扩展 Step 4 环境，追加传感器配置 |
| `model/step5_sensors/run_sensors_env.py` | 运行入口，读取传感器数据 |
| `model/step5_sensors/test_sensors_cfg.py` | 单元测试 |

**传感器配置**：

```python
# 在 G1StandSceneCfg 中追加：
contact_forces = ContactSensorCfg(
    prim_path="{ENV_REGEX_NS}/Robot/.*ankle_roll_link",
    update_period=0.0,
    history_length=6,
)

# 可选：头部相机
head_camera = CameraCfg(
    prim_path="{ENV_REGEX_NS}/Robot/head_link/camera",
    update_period=0.1,
    height=240,
    width=320,
    data_types=["rgb", "distance_to_image_plane"],
    spawn=sim_utils.PinholeCameraCfg(
        focal_length=1.88,
        focus_distance=0.15,
        horizontal_aperture=3.84,
    ),
    offset=CameraCfg.OffsetCfg(
        pos=(0.05, 0.0, 0.05),
        rot=(0.5, -0.5, 0.5, -0.5),
        convention="ros",
    ),
)
```

**验证标准**：
- 接触传感器数据 shape 正确，默认单机器人为 `(1, 2, 3)`
- 传感器数据可在仿真循环中正常读取
- 相机为可选项，不阻塞 Step 5 完成

**当前验证命令**：

```powershell
D:\il\env\Scripts\python.exe -B -m unittest test_sensors_cfg -v
D:\il\env\Scripts\python.exe model\step5_sensors\run_sensors_env.py --headless --max_steps 2
```

---

## Step 6 — 训练入口

**目的**：接入 RL 训练框架，完成端到端站立策略训练。

**新文件**：

| 文件 | 用途 |
|------|------|
| `model/step6_train/rsl_rl_stand_ppo.py` | RSL-RL PPO 训练入口 |
| `model/step6_train/agents/rsl_rl_ppo_cfg.py` | PPO 超参数配置 |

**训练入口逻辑**：

```python
# 1. 注册自定义环境（或复用已注册的）
# 2. 创建 RSL-RL runner
runner = OnPolicyRunner(env, agent_cfg, log_dir=log_dir)
# 3. 加载 checkpoint（如有）
# 4. 训练
runner.learn(num_learning_iterations=500)
```

**PPO 超参数参考**：

```python
G1StandPPORunnerCfg = RslRlPpoRunnerCfg(
    policy=RslRlPpoActorCriticCfg(
        class_name="ActorCritic",
        init_noise_std=1.0,
        actor_hidden_dims=[256, 256, 128],
        critic_hidden_dims=[256, 256, 128],
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
    num_steps_per_env=24,
    max_iterations=500,
    save_interval=50,
)
```

**验证标准**：
- 训练可正常启动并运行至少 100 个 iteration
- reward 曲线有上升趋势
- 保存的 checkpoint 可加载推理

---

## 目录结构（完成后）

```
yushu_robot/
├── model/
│   ├── build_robot_model/          # Step 0 — URDF → USD
│   │   ├── build_g1_from_urdf.py
│   │   ├── robot_asset.py
│   │   ├── test_robot_asset.py
│   ├── generatedUSD/               # 全局 USD 生成资产
│   │   └── g1_29dof_mode_16.usd
│   ├── step1_load_articulation/    # Step 1 — 手动 Articulation 加载
│   │   ├── step1_load_articulation.py
│   │   └── test_step1_load_articulation.py
│   ├── step2_create_scene/         # Step 2 — InteractiveSceneCfg
│   │   └── step2_create_scene.py
│   ├── step3_robot_cfg/            # Step 3 — 机器人配置模块
│   │   └── g1_local_cfg.py
│   ├── step4_manager_env/          # Step 4 — Manager-Based 环境
│   │   ├── stand_env_cfg.py
│   │   └── run_stand_env.py
│   ├── step5_sensors/              # Step 5 — 传感器集成
│   │   └── sensors_cfg.py
│   ├── step6_train/                # Step 6 — 训练
│   │   ├── rsl_rl_stand_ppo.py
│   │   └── agents/
│   │       └── rsl_rl_ppo_cfg.py
│   └── README.md
├── yushu_robot_urdf/
│   ├── g1_29dof_mode_16.urdf
│   └── meshes/
├── README.md
└── spec.md                         # 本文件
```

---

## 开发顺序与依赖

```
Step 0  (已有) ──→ Step 1  ──→ Step 2
                        ↓
                     Step 3  ──→ Step 4  ──→ Step 5
                                                ↓
                                             Step 6
```

- Step 0 → 1：需要 USD 文件路径
- Step 1 → 2：将手动管理改为声明式场景
- Step 1 → 3：将内联配置提取为独立模块
- Step 3 → 4：在场景上叠加 Manager 层
- Step 4 → 5：向场景追加传感器
- Step 5 → 6：接入训练框架

---

## 运行环境

| 项目 | 值 |
|------|-----|
| Python | `D:\il\env\Scripts\python.exe` |
| 工作目录 | `d:\il\IsaacLab\scripts\yushu_robot` |
| IsaacLab | `d:\il\IsaacLab` |
| GPU | 需要支持 CUDA 的 NVIDIA GPU |

---

## 命名约定

| 类型 | 格式 | 示例 |
|------|------|------|
| 脚本文件 | `step{N}_{动词}_{对象}.py` | `step1_load_articulation.py` |
| 配置类 | `{功能}Cfg` | `G1StandEnvCfg` |
| 环境 ID | `Isaac-{Task}-{Robot}-{Variant}-v0` | `Isaac-Stand-G1-v0` |
| 场景类 | `{Robot}SceneCfg` | `G1SceneCfg` |
| USD 输出 | `model/generatedUSD/{urdf_name}.usd` | `model/generatedUSD/g1_29dof_mode_16.usd` |
