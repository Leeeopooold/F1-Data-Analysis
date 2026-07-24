"""数据加载、指标计算和供 API 使用的分析功能。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence, Dict, List

import fastf1
import numpy as np
import pandas as pd


# --- 数据读取 -------------------------------------------------

def load_session(year: int, event: str, session_type: str, cache_dir: Path):
    """加载一个 FastF1 session；缓存目录不存在时自动创建。"""
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))
    session = fastf1.get_session(year, event, session_type)
    session.load(telemetry=True, weather=True, messages=False)
    return session


def get_fastest_laps(session, drivers: Sequence[str]) -> dict[str, Any]:
    """取得每位车手的最快有效圈。"""
    fastest_laps = {}
    for driver in drivers:
        try:
            lap = session.laps.pick_driver(driver).pick_fastest()
            if lap is None or pd.isna(lap["LapTime"]):
                continue
            fastest_laps[driver] = lap
        except Exception:
            continue
    return fastest_laps


# --- 辅助函数 -------------------------------------------------

def _format_timedelta_seconds(value) -> float | None:
    if pd.isna(value):
        return None
    return value.total_seconds()


def _brake_event_count(telemetry: pd.DataFrame) -> int:
    brake = telemetry["Brake"].fillna(False).astype(bool)
    return int((brake & ~brake.shift(fill_value=False)).sum())


def _gear_shift_count(telemetry: pd.DataFrame) -> int:
    gears = telemetry["nGear"].ffill().fillna(0)
    return int(gears.ne(gears.shift()).sum() - 1)


# --- 单圈分析 (Fastest Lap API) --------------------------------

def build_summary_dict(laps: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """生成最快圈量化摘要。"""
    rows = []
    if not laps:
        return rows
    reference_lap_time = next(iter(laps.values()))["LapTime"]
    
    for driver, lap in laps.items():
        telemetry = lap.get_telemetry()
        lap_time = lap["LapTime"]
        weather = lap.get_weather_data()
        rows.append(
            {
                "Driver": driver,
                "LapTime": _format_timedelta_seconds(lap_time),
                "DeltaToRef": _format_timedelta_seconds(lap_time - reference_lap_time),
                "Sector1": _format_timedelta_seconds(lap["Sector1Time"]),
                "Sector2": _format_timedelta_seconds(lap["Sector2Time"]),
                "Sector3": _format_timedelta_seconds(lap["Sector3Time"]),
                "Compound": lap["Compound"],
                "TyreLife": int(lap["TyreLife"]) if pd.notna(lap["TyreLife"]) else None,
                "AirTemp": float(weather["AirTemp"]) if pd.notna(weather["AirTemp"]) else None,
                "TrackTemp": float(weather["TrackTemp"]) if pd.notna(weather["TrackTemp"]) else None,
                "TopSpeed": float(telemetry["Speed"].max()),
                "AvgSpeed": float(telemetry["Speed"].mean()),
                "FullThrottle": float((telemetry["Throttle"] >= 99).mean() * 100),
                "BrakeApplications": _brake_event_count(telemetry),
                "GearShifts": _gear_shift_count(telemetry),
            }
        )
    return rows


def get_telemetry_data(laps: Mapping[str, Any]) -> Dict[str, Any]:
    """提取遥测数据用于前端绘制。"""
    result = {}
    for driver, lap in laps.items():
        telemetry = lap.get_telemetry()
        result[driver] = {
            "Distance": telemetry["Distance"].tolist(),
            "Speed": telemetry["Speed"].tolist(),
            "Throttle": telemetry["Throttle"].tolist(),
            "Brake": telemetry["Brake"].astype(int).tolist(),
            "nGear": telemetry["nGear"].fillna(0).astype(int).tolist()
        }
    return result


def get_track_speed_delta(reference_lap: Any, comparison_lap: Any) -> Dict[str, Any]:
    """计算两位车手的速度差，并包含赛道坐标信息。"""
    reference = reference_lap.get_telemetry().sort_values("Distance")
    comparison = comparison_lap.get_telemetry().sort_values("Distance")
    
    required_columns = {"Distance", "Speed", "X", "Y"}
    missing_columns = required_columns - (set(reference.columns) & set(comparison.columns))
    if missing_columns:
        return {}
        
    distance = reference["Distance"].to_numpy()
    valid = (distance >= comparison["Distance"].min()) & (distance <= comparison["Distance"].max())
    reference = reference.loc[valid].reset_index(drop=True)
    if len(reference) < 2:
        return {}
        
    distance = reference["Distance"].to_numpy()
    comparison_speed = np.interp(distance, comparison["Distance"], comparison["Speed"])
    speed_delta = reference["Speed"].to_numpy() - comparison_speed
    
    # 将 NumPy 类型转为原生 list
    return {
        "Distance": distance.tolist(),
        "X": reference["X"].tolist(),
        "Y": reference["Y"].tolist(),
        "SpeedDelta": speed_delta.tolist(),
        "ReferenceDriver": reference_lap["Driver"],
        "ComparisonDriver": comparison_lap["Driver"]
    }


def get_circuit_corners(session) -> List[Dict[str, Any]]:
    """提取弯角信息（编号、距离、坐标）。"""
    circuit_info = session.get_circuit_info()
    corners = []
    if circuit_info is not None and hasattr(circuit_info, 'corners'):
        for _, corner in circuit_info.corners.iterrows():
            corners.append({
                "Number": corner.Number,
                "Distance": corner.Distance,
                "X": corner.X,
                "Y": corner.Y
            })
    return corners


# --- 长距离 / 正赛分析 (Race Pace API) --------------------------

def get_race_pace_data(session, drivers: Sequence[str]) -> Dict[str, Any]:
    """提取车手的所有有效圈数用于分析 Race Pace 和轮胎衰退。"""
    all_laps = session.laps.pick_drivers(drivers)
    
    # 过滤明显的非正常圈 (进出站、SC、VSC)
    # is_accurate 通常能过滤掉大部分 In/Out Laps 和黄旗圈
    accurate_laps = all_laps.pick_accurate()
    
    result = {}
    for driver in drivers:
        driver_laps = accurate_laps.pick_driver(driver)
        
        laps_data = []
        for _, lap in driver_laps.iterrows():
            if pd.isna(lap["LapTime"]):
                continue
            
            laps_data.append({
                "LapNumber": int(lap["LapNumber"]),
                "LapTime": lap["LapTime"].total_seconds(),
                "Compound": lap["Compound"],
                "TyreLife": int(lap["TyreLife"]) if pd.notna(lap["TyreLife"]) else None,
                "Stint": int(lap["Stint"]) if pd.notna(lap["Stint"]) else None,
            })
            
        result[driver] = laps_data
        
    return result
