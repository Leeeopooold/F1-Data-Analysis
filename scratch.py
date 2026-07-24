import fastf1
import pandas as pd
from fastf1 import Cache
Cache.enable_cache('e:/F1/f1_cache')

session = fastf1.get_session(2026, "British Grand Prix", "R")
session.load()
ver_laps = session.laps.pick_driver('VER')
print("Session Name:", session.event['EventName'], session.name)
print("Total Laps for VER:", len(ver_laps))
print("Results:", session.results[['Abbreviation', 'Position', 'Status']])
