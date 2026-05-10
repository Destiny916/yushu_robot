# Yushu Robot URDF 部件说明

这里保存 Unitree G1 29-DOF 机器人的原始几何和命名资料。

## 目录内容

- `g1_29dof_mode_16.urdf`：主 URDF 文件
- `meshes/`：URDF 引用的 STL 网格文件
- `README.md`：目录入口说明

## 命名约定

- `left_` / `right_`：左右对称部件
- `_link`：结构链接
- `_joint`：URDF 关节
- `_force_sensor`：力传感器相关几何或命名
- `_rev_1_0`：Rev 1.0 几何版本
- `_5010`：5010 规格执行器相关部件

## 主要部件

- 躯干：`pelvis*`、`torso*`、`waist*`、`head*`
- 左右腿：`left_hip_*`、`left_knee_*`、`left_ankle_*` 及对应右侧部件
- 左右臂：`left_shoulder_*`、`left_elbow_*`、`left_wrist_*` 及对应右侧部件
- 手部与末端执行器：`left_rubber_hand*`、`right_rubber_hand*`、`left_hand_*`、`right_hand_*`
- 传感器：`*_force_sensor_*`、`d455_link*`、`imu_in_torso`、`imu_in_pelvis`、`d435_link`、`mid360_link`

## 维护规则

- 新增部件时优先放在本目录或其子目录中。
- 不要随意改名 mesh 文件，因为 URDF 的 `<mesh filename="...">` 依赖这些路径。
- 修改 URDF 后，先确认 XML 可解析，再确认所有 mesh 路径都存在。

## 与模拟代码的关系

`model/` 目录负责仿真、训练和验证代码，`yushu_robot_urdf/` 负责机器人本体资源。两边分开维护，避免把源资源和生成物混在一起。
