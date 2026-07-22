import fastf1
fastf1.Cache.enable_cache('f1_cache')
session = fastf1.get_session(2024, 'Bahrain', 'Q')
session.load(telemetry=True, weather=True, messages=False)
lap = session.laps.pick_driver('VER').pick_fastest()

print(f"Driver: VER")
# pyrefly: ignore [unsupported-operation]
print(f"Tyre Compound: {lap['Compound']}")
# pyrefly: ignore [unsupported-operation]
print(f"Tyre Life: {lap['TyreLife']}")
# pyrefly: ignore [missing-attribute]
weather = lap.get_weather_data()
print("Weather Data:")
print(weather)
