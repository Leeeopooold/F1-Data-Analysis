# F1 Data Analysis

这是一个基于 Python 的一级方程式赛车（F1）遥测数据分析工具。通过调用国际汽联（FIA）的公开数据接口，实现对赛车性能、车手驾驶风格的深度量化对比。

![
](466a653aaa28bb533e08bf2217797888.png)

## 核心功能

- **实时数据接入**：利用 `FastF1` 库自动获取历年各站大奖赛的官方遥测数据。
- **多车手对比**：支持对不同车手的单圈数据进行叠加分析。
- **多维度分析指标**：目前已实现**赛道位置与车速（Speed vs Distance）**的动态曲线绘制。
- **本地高性能缓存**：内置缓存机制，避免重复下载冗余数据，大幅提升二次分析效率。

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
pip install fastf1 matplotlib pandas
```

### 3. 运行分析

在项目根目录下运行 `main.py`。

**注意**：首次运行会下载几十MB的数据，请确保网络通畅。

## 后续规划

- [ ] 增加 **油门**（**Throttle**） 与 **刹车**（**Brake**） 深度对比图

- [ ] 增加 **赛道地图**（**Track Map**） 可视化

- [ ] 增加 **换挡时机**（**Gear Shifts**） 统计分析

🏎️🏎️🏎️🏎️🏎️
