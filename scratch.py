import fastf1
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
fastf1.Cache.enable_cache('f1_cache')
session = fastf1.get_session(2024, 'Bahrain', 'Q')
session.load(telemetry=True, weather=False, messages=False)

circuit_info = session.get_circuit_info()
driver_laps = session.laps.pick_driver('VER')
if driver_laps.empty:
    raise ValueError("未找到车手 VER 的圈速数据。")

lap = driver_laps.pick_fastest()
if lap is None or pd.isna(lap["LapTime"]):
    raise ValueError("未找到车手 VER 的有效最快圈。")

telemetry = lap.get_telemetry()

# Test plotting logic
fig, ax = plt.subplots()
distance = telemetry["Distance"]
speed = telemetry["Speed"]
ax.plot(distance, speed)

brake = telemetry["Brake"].fillna(False).astype(bool)
brake_points = telemetry[brake & ~brake.shift(fill_value=False)]
ax.scatter(brake_points["Distance"], brake_points["Speed"], color='red', marker='v', s=50, label='Brake', zorder=5)

throttle = telemetry["Throttle"]
throttle_starts = telemetry[(throttle > 0) & (throttle.shift(fill_value=100) == 0)]
ax.scatter(throttle_starts["Distance"], throttle_starts["Speed"], color='green', marker='^', s=50, label='Throttle', zorder=5)

if circuit_info is not None and hasattr(circuit_info, 'corners'):
    for _, corner in circuit_info.corners.iterrows():
        ax.axvline(x=corner.Distance, color='gray', linestyle='--', alpha=0.5)
        ax.text(corner.Distance, ax.get_ylim()[1], str(corner.Number), 
                rotation=0, ha='center', va='bottom', fontsize=8)

fig.savefig('output/scratch_telemetry.png')

# Test map logic
fig_map, ax_map = plt.subplots()
ax_map.plot(telemetry["X"], telemetry["Y"])
if circuit_info is not None and hasattr(circuit_info, 'corners'):
    for _, corner in circuit_info.corners.iterrows():
        ax_map.text(corner.X, corner.Y, str(corner.Number), color='black', 
                    fontsize=10, ha='center', va='center',
                    bbox=dict(boxstyle='circle', facecolor='white', alpha=0.7, edgecolor='none'))

fig_map.savefig('output/scratch_map.png')
print("Scratch completed successfully.")
