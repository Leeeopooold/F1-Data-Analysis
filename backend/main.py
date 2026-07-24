from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path

from f1_analysis import (
    load_session,
    get_fastest_laps,
    build_summary_dict,
    get_telemetry_data,
    get_race_pace_data,
    get_circuit_corners,
    get_track_speed_delta
)

app = FastAPI(title="F1 Data Analysis API")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE_DIR = Path("../f1_cache")

@app.get("/api/analysis/fastest")
def get_fastest_lap_analysis(
    year: int = Query(2024),
    event: str = Query("Bahrain"),
    session_type: str = Query("Q"),
    drivers: str = Query("VER,LEC")
):
    try:
        driver_list = [d.strip().upper() for d in drivers.split(",")]
        session = load_session(year, event, session_type, CACHE_DIR)
        laps = get_fastest_laps(session, driver_list)
        
        if not laps:
            raise HTTPException(status_code=404, detail="No valid fastest laps found for specified drivers.")
            
        summary = build_summary_dict(laps)
        telemetry = get_telemetry_data(laps)
        corners = get_circuit_corners(session)
        
        # Calculate track speed delta if at least 2 drivers
        speed_delta = {}
        if len(driver_list) >= 2 and driver_list[0] in laps and driver_list[1] in laps:
            speed_delta = get_track_speed_delta(laps[driver_list[0]], laps[driver_list[1]])

        return {
            "summary": summary,
            "telemetry": telemetry,
            "corners": corners,
            "speed_delta": speed_delta
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/race-pace")
def get_race_pace(
    year: int = Query(2024),
    event: str = Query("Bahrain"),
    session_type: str = Query("R"),
    drivers: str = Query("VER,LEC")
):
    try:
        driver_list = [d.strip().upper() for d in drivers.split(",")]
        session = load_session(year, event, session_type, CACHE_DIR)
        
        pace_data = get_race_pace_data(session, driver_list)
        
        return {
            "race_pace": pace_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
