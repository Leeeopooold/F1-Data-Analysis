"""数据加载、指标计算和可视化功能。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import fastf1
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection
from matplotlib.colors import TwoSlopeNorm


DEFAULT_COLORS = ["#0600EF", "#DC0000", "#00A19C", "#FF8700", "#2293D1", "#900000"]


# --- 数据读取与最快圈选择 -------------------------------------------------

def load_session(year: int, event: str, session_type: str, cache_dir: Path):
    """加载一个 FastF1 session；缓存目录不存在时自动创建。"""
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))
    session = fastf1.get_session(year, event, session_type)
    # 位置与遥测数据是地图和曲线所必需的；天气和消息不参与本次计算。
    session.load(telemetry=True, weather=False, messages=False)
    return session


def get_fastest_laps(session, drivers: Sequence[str]) -> dict[str, Any]:
    """取得每位车手的最快有效圈，缺少数据时给出明确错误。"""
    fastest_laps = {}
    for driver in drivers:
        lap = session.laps.pick_driver(driver).pick_fastest()
        if lap is None or pd.isna(lap["LapTime"]):
            raise ValueError(f"未找到车手 {driver} 的有效最快圈，请检查车手缩写和比赛阶段。")
        fastest_laps[driver] = lap
    return fastest_laps


def _format_timedelta(value) -> str:
    if pd.isna(value):
        return "—"
    total_seconds = value.total_seconds()
    minutes, seconds = divmod(total_seconds, 60)
    return f"{int(minutes)}:{seconds:06.3f}"


def _brake_event_count(telemetry: pd.DataFrame) -> int:
    brake = telemetry["Brake"].fillna(False).astype(bool)
    return int((brake & ~brake.shift(fill_value=False)).sum())


def _gear_shift_count(telemetry: pd.DataFrame) -> int:
    gears = telemetry["nGear"].ffill().fillna(0)
    return int(gears.ne(gears.shift()).sum() - 1)


def build_summary_table(laps: Mapping[str, Any]) -> pd.DataFrame:
    """生成可导出的最快圈量化摘要；第一位车手作为圈速差基准。"""
    rows = []
    reference_lap_time = next(iter(laps.values()))["LapTime"]
    for driver, lap in laps.items():
        telemetry = lap.get_telemetry()
        lap_time = lap["LapTime"]
        rows.append(
            {
                "Driver": driver,
                "Lap time": _format_timedelta(lap_time),
                "Delta to reference (s)": round((lap_time - reference_lap_time).total_seconds(), 3),
                "Sector 1": _format_timedelta(lap["Sector1Time"]),
                "Sector 2": _format_timedelta(lap["Sector2Time"]),
                "Sector 3": _format_timedelta(lap["Sector3Time"]),
                "Top speed (km/h)": round(float(telemetry["Speed"].max()), 1),
                "Average speed (km/h)": round(float(telemetry["Speed"].mean()), 1),
                "Full throttle (%)": round(float((telemetry["Throttle"] >= 99).mean() * 100), 1),
                "Brake applications": _brake_event_count(telemetry),
                "Gear shifts": _gear_shift_count(telemetry),
            }
        )
    return pd.DataFrame(rows)


def save_summary(summary: pd.DataFrame, output_path: Path) -> None:
    # utf-8-sig 让 Windows 版 Excel 可以直接正确识别中文表头。
    summary.to_csv(output_path, index=False, encoding="utf-8-sig")


# --- 遥测与赛道可视化 -----------------------------------------------------

def plot_telemetry(
    session, laps: Mapping[str, Any], output_path: Path, colors: Sequence[str], xlim: Sequence[float] | None, show: bool
) -> None:
    """绘制速度、油门和刹车三联图。"""
    fig, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
    drivers = list(laps)
    fig.suptitle(f"{' vs '.join(drivers)} — Telemetry Comparison", fontsize=16)

    for index, (driver, lap) in enumerate(laps.items()):
        telemetry = lap.get_telemetry()
        color = colors[index % len(colors)]
        distance = telemetry["Distance"]
        
        # 基础折线
        axes[0].plot(distance, telemetry["Speed"], label=driver, color=color, linewidth=2)
        axes[1].plot(distance, telemetry["Throttle"], label=driver, color=color, linewidth=1.5)
        axes[2].step(distance, telemetry["Brake"].astype(int), label=driver, color=color, linewidth=1.25, where="post")
        
        # 标注制动点（Brake 从 False 变 True 的时刻）
        brake = telemetry["Brake"].fillna(False).astype(bool)
        brake_points = telemetry[brake & ~brake.shift(fill_value=False)]
        brake_label = "Brake point" if index == 0 else "_nolegend_"
        axes[0].scatter(brake_points["Distance"], brake_points["Speed"], color=color, marker='v', s=30, zorder=5, label=brake_label)
        
        # 标注油门恢复点（Throttle 从 0 变大于 0 的时刻）
        throttle = telemetry["Throttle"]
        throttle_starts = telemetry[(throttle > 0) & (throttle.shift(fill_value=100) == 0)]
        throttle_label = "Throttle point" if index == 0 else "_nolegend_"
        axes[0].scatter(throttle_starts["Distance"], throttle_starts["Speed"], color=color, marker='^', s=30, zorder=5, label=throttle_label)

    axes[0].set_ylabel("Speed (km/h)")
    axes[1].set_ylabel("Throttle (%)")
    axes[1].set_ylim(-5, 105)
    axes[2].set_ylabel("Brake")
    axes[2].set_xlabel("Distance on track (m)")
    axes[2].set_ylim(-0.1, 1.1)
    axes[2].set_yticks([0, 1], ["Off", "On"])
    for axis in axes:
        axis.grid(True, alpha=0.3)
        axis.legend(loc="best")
    if xlim:
        axes[2].set_xlim(xlim)

    # 绘制弯角编号与参考线
    circuit_info = session.get_circuit_info()
    if circuit_info is not None and hasattr(circuit_info, 'corners'):
        y_max = axes[0].get_ylim()[1]
        for _, corner in circuit_info.corners.iterrows():
            for axis in axes:
                axis.axvline(x=corner.Distance, color='gray', linestyle='--', alpha=0.4, zorder=0)
            axes[0].text(corner.Distance, y_max, str(corner.Number), 
                         rotation=0, ha='center', va='bottom', fontsize=9)

    fig.tight_layout()
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def plot_track_speed_delta(session, reference_lap, comparison_lap, output_path: Path, show: bool) -> None:
    """以第一位车手减第二位车手的速度差为颜色，绘制赛道地图。"""
    reference = reference_lap.get_telemetry().sort_values("Distance")
    comparison = comparison_lap.get_telemetry().sort_values("Distance")
    required_columns = {"Distance", "Speed", "X", "Y"}
    missing_columns = required_columns - (set(reference.columns) & set(comparison.columns))
    if missing_columns:
        raise ValueError(f"无法绘制赛道地图，遥测数据缺少字段：{', '.join(sorted(missing_columns))}")
    distance = reference["Distance"].to_numpy()
    valid = (distance >= comparison["Distance"].min()) & (distance <= comparison["Distance"].max())
    reference = reference.loc[valid].reset_index(drop=True)
    if len(reference) < 2:
        raise ValueError("两位车手没有足够的重叠遥测距离，无法生成速度差地图。")
    distance = reference["Distance"].to_numpy()
    comparison_speed = np.interp(distance, comparison["Distance"], comparison["Speed"])
    # 两圈采样点不完全一致，按共同的赛道距离插值后再比较速度。
    speed_delta = reference["Speed"].to_numpy() - comparison_speed

    # pyrefly: ignore [bad-argument-count, bad-argument-type]
    points = np.column_stack((reference["X"], reference["Y"])).reshape(-1, 1, 2)
    # pyrefly: ignore [bad-index, no-matching-overload]
    segments = np.concatenate([points[:-1], points[1:]], axis=1)    
    delta_by_segment = (speed_delta[:-1] + speed_delta[1:]) / 2
    # 使用 98 分位而非最大值，避免个别遥测尖峰压缩整张地图的颜色对比。
    limit = max(5.0, float(np.nanpercentile(np.abs(delta_by_segment), 98)))

    fig, axis = plt.subplots(figsize=(10, 8))
    collection = LineCollection(
        segments,
        cmap="RdBu_r",
        norm=TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit),
        linewidth=4,
    )
    collection.set_array(delta_by_segment)
    axis.add_collection(collection)
    axis.autoscale()
    axis.set_aspect("equal", adjustable="box")
    axis.axis("off")
    
    # 标注弯角编号
    circuit_info = session.get_circuit_info()
    if circuit_info is not None and hasattr(circuit_info, 'corners'):
        for _, corner in circuit_info.corners.iterrows():
            axis.text(corner.X, corner.Y, str(corner.Number), color='black', 
                      fontsize=9, ha='center', va='center',
                      bbox=dict(boxstyle='circle,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none'))
                      
    reference_driver = reference_lap["Driver"]
    comparison_driver = comparison_lap["Driver"]
    axis.set_title(f"Track speed delta: {reference_driver} − {comparison_driver}")
    colorbar = fig.colorbar(collection, ax=axis, shrink=0.8, pad=0.03)
    colorbar.set_label("Speed delta (km/h)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
