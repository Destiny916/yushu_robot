# Yushu Robot URDF 部件说明

本目录保存机器人本体相关资源：URDF、mesh、传感器链接、末端执行器几何体，以及后续新增机器人的部件信息。

## 主要文件

- `g1_29dof_mode_16.urdf`：Unitree G1 29DOF 主 URDF。
- `meshes/`：URDF 引用的 STL 网格目录。

## 部件分类

- 躯干：`pelvis*`、`torso*`、`waist*`、`head*`。
- 左腿：`left_hip_*`、`left_knee_*`、`left_ankle_*`。
- 右腿：`right_hip_*`、`right_knee_*`、`right_ankle_*`。
- 左臂：`left_shoulder_*`、`left_elbow_*`、`left_wrist_*`、`left_base_link*`。
- 右臂：`right_shoulder_*`、`right_elbow_*`、`right_wrist_*`、`right_base_link*`。
- 手部和末端执行器：`left_rubber_hand*`、`right_rubber_hand*`、`left_hand_*`、`right_hand_*`、`Dex1_*`、`L_hand_base_link*`、`R_hand_base_link*`、`Link*_L`、`Link*_R`。
- 传感器/感知部件：`*_force_sensor_*`、`d455_link*`、URDF 中的 `imu_in_torso`、`imu_in_pelvis`、`d435_link`、`mid360_link`。

## 命名规则

- `left_` / `right_`：左右对称部件。
- `_link`：连杆或结构部件。
- `_joint`：URDF 关节名称。
- `_rev_1_0`：Rev 1.0 几何版本。
- `_5010`：5010 规格执行器相关部件。
- `_force_sensor`：力传感器相关几何体。

## 维护约定

- 新增机器人本体资源时，优先放在本目录或本目录下的子目录中。
- 不要随意重命名 mesh 文件，URDF 的 `<mesh filename="...">` 依赖这些路径。
- 修改 URDF 后，检查 XML 能被解析，并确认所有 mesh 引用都存在。
- 仿真、训练、控制、评估代码放到仓库根目录的 `model/`，不要混入本资源目录。
