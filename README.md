# F1 Data Analysis

这是一个基于 Python 与 FastF1 的一级方程式赛车（F1）遥测数据分析工具，用于量化对比不同车手的最快圈表现。

![alt text](output/2024_Bahrain_Q_VER_vs_LEC_vs_SAI_vs_PER_telemetry.png)

![alt text](output/2024_Bahrain_Q_VER_vs_LEC_vs_SAI_vs_PER_track_speed_delta.png)

## 核心功能

- **参数化数据接入**：可指定赛季、分站、比赛阶段和两位以上车手。
- **最快圈遥测对比**：叠加展示速度、油门与刹车状态，支持按赛道距离聚焦局部路段。
- **量化结论**：导出圈速、分段、最高/平均速度、全油门比例、制动次数与换挡次数的 CSV 摘要。
- **赛道地图**：以第一位车手减第二位车手的速度差着色，直观定位性能差异区段。
- **本地缓存**：FastF1 下载结果保存在 `f1_cache/`，提升重复分析速度。

## 技术栈

- **语言**: Python 3.10+
- **关键库**: `fastf1`, `pandas`, `matplotlib`
- **编辑器**: VS Code
- **环境管理**: Python Virtual Environment

## 启动

### 1. 环境准备 (Windows)

建议在 VS Code 中创建虚拟环境以保持环境纯净：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. 安装依赖

```powershell
pip install -r requirements.txt
```

### 3. 运行分析

默认分析 2024 巴林站排位赛的 VER 与 LEC：

```powershell
python main.py
```

指定比赛和车手，并只查看 400–1200 米区间：

```powershell
python main.py --year 2024 --event Bahrain --session Q --drivers VER LEC --xlim 400 1200
```

结果默认写入 `output/`：

- `*_summary.csv`：量化指标；第一位车手是圈速差和地图速度差的基准。
- `*_telemetry.png`：速度、油门、刹车三联图。
- `*_track_speed_delta.png`：赛道速度差地图，红色表示第一位车手更快，蓝色表示第二位车手更快。

**注意**：首次运行会下载几十MB的数据，请确保网络通畅。

## 后续规划

- [ ] 增加弯角编号、制动点和油门恢复点标注
- [ ] 增加轮胎、天气和赛道状态等可比性上下文
- [ ] 增加交互式 Web 界面与多圈/长距离比赛分析

🏎️🏎️🏎️🏎️🏎️
