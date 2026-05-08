# P1.1 地形系统设计文档

> 日期: 2026-05-08 | 状态: 待实施

## Context

AHC 训练 Phase 1 需要 6 种地形（T0-T5）用于站立/行走策略训练。本设计实现 P1.1（地形系统），每个地形类型独立为一个 Python 文件，配合共用测试脚本验证机器人在各地形上的放置效果。

## 目录结构

```
yushu_robot/model/step6_train/terrains/
├── __init__.py              # 导出 TERRAIN_REGISTRY 字典
├── T0_plane.py              # 平面地形
├── T1_slope_10.py           # 10° 斜坡 (0.175 rad)
├── T2_slope_20.py           # 20° 斜坡 (0.349 rad)
├── T3_slope_30.py           # 30° 斜坡 (0.524 rad)
├── T4_stairs.py             # 楼梯 (台阶高 0.05-0.15m, 步宽 0.3m)
├── T5_wave.py               # 不规则波浪 (波幅 0.02-0.08m)
└── test_terrains.py         # 共用测试脚本
```

## 设计方案：方案 A — 独立 TerrainGeneratorCfg

每个地形文件导出完整的 `TerrainGeneratorCfg`，可独立使用。

### 各地形文件统一接口

每个文件导出：
- `TERRAIN_NAME: str` — 地形名称（如 `"T1_slope_10"`）
- `TERRAIN_CFG: TerrainGeneratorCfg` — 完整地形生成器配置

### 地形参数规格

| 文件 | SubTerrain 类型 | 关键参数 | spec 比例 |
|------|----------------|---------|----------|
| `T0_plane.py` | `MeshPlaneTerrainCfg` | 无额外参数 | 20% |
| `T1_slope_10.py` | `HfPyramidSlopedTerrainCfg` | `slope_range=(0.175, 0.175)` | 20% |
| `T2_slope_20.py` | `HfPyramidSlopedTerrainCfg` | `slope_range=(0.349, 0.349)` | 20% |
| `T3_slope_30.py` | `HfPyramidSlopedTerrainCfg` | `slope_range=(0.524, 0.524)` | 15% |
| `T4_stairs.py` | `HfPyramidStairsTerrainCfg` | `step_height_range=(0.05, 0.15)`, `step_width=0.3` | 15% |
| `T5_wave.py` | `HfWaveTerrainCfg` | `amplitude_range=(0.02, 0.08)`, `num_waves=2` | 10% |

### TerrainGeneratorCfg 公共参数

```python
TerrainGeneratorCfg(
    size=(8.0, 8.0),          # 每个子地形 8x8m
    border_width=20.0,         # 安全边界
    num_rows=10,               # 10 个难度等级
    num_cols=1,                # 只有 1 种地形类型（独立测试时）
    horizontal_scale=0.1,
    vertical_scale=0.005,
    curriculum=True,
)
```

### __init__.py 设计

```python
from .T0_plane import TERRAIN_CFG as T0_CFG, TERRAIN_NAME as T0_NAME
# ... T1-T5 同理

TERRAIN_REGISTRY = {
    "T0": T0_CFG,
    "T1": T1_CFG,
    "T2": T2_CFG,
    "T3": T3_CFG,
    "T4": T4_CFG,
    "T5": T5_CFG,
}
```

### 测试脚本 test_terrains.py

**命令行参数**：
- `--terrain T0` — 选择地形（T0/T1/T2/T3/T4/T5），默认 T0
- `--num_envs 1` — 环境数量
- `--max_steps 0` — 最大步数（0=无限）
- `--headless` — 无头模式
- `--graceful_close` — 优雅关闭

**场景配置**：使用 `TerrainImporterCfg` 替代 step4 的 `GroundPlaneCfg`，机器人使用 `G1_LOCAL_CFG`。

**仿真行为**：机器人静止站立，每步打印 step count、robot height、contact forces。

**路径引导**：复用 step4/step5 的两阶段 bootstrap 模式（`sys.path` + `bootstrap_isaaclab_paths()`）。

**退出策略**：`--max_steps > 0` 且无 `--graceful_close` 时调用 `os._exit(0)` 避免 Kit 关闭挂死。

## 验证命令

```powershell
# 各地形 headless 冒烟测试
D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T0 --headless --max_steps 2
D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T1 --headless --max_steps 2
D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T2 --headless --max_steps 2
D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T3 --headless --max_steps 2
D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T4 --headless --max_steps 2
D:\il\env\Scripts\python.exe model\step6_train\terrains\test_terrains.py --terrain T5 --headless --max_steps 2
```

## 后续复用

训练阶段需要混合地形时，从各文件提取 sub_terrain cfg 并设置 `proportion`（独立文件中 `proportion=1.0`，混合时需按 spec 比例调整）：

```python
from terrains.T0_plane import TERRAIN_CFG as T0
from terrains.T1_slope_10 import TERRAIN_CFG as T1
# ...
combined_cfg = TerrainGeneratorCfg(
    size=(8.0, 8.0),
    border_width=20.0,
    num_rows=10,
    num_cols=6,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    curriculum=True,
    sub_terrains={
        "flat": T0.sub_terrains["flat"].replace(proportion=0.20),
        "slope_10": T1.sub_terrains["slope_10"].replace(proportion=0.20),
        "slope_20": T2.sub_terrains["slope_20"].replace(proportion=0.20),
        "slope_30": T3.sub_terrains["slope_30"].replace(proportion=0.15),
        "stairs": T4.sub_terrains["stairs"].replace(proportion=0.15),
        "wave": T5.sub_terrains["wave"].replace(proportion=0.10),
    },
)
```

## 关键文件依赖

- `model/build_robot_model/robot_asset.py` — `get_isaaclab_source_paths()` 路径引导
- `model/step3_robot_cfg/g1_local_cfg.py` — `G1_LOCAL_CFG` 机器人配置
- IsaacLab 地形 API: `isaaclab.terrains.TerrainGeneratorCfg`, `TerrainImporterCfg`
- IsaacLab 地形类型: `MeshPlaneTerrainCfg`, `HfPyramidSlopedTerrainCfg`, `HfPyramidStairsTerrainCfg`, `HfWaveTerrainCfg`
