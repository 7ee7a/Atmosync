from fastapi import FastAPI
from typing import Dict, Any
from services.strasbourg import fetch_openaq_pm25, fetch_sentinel5p_no2_mock
from services.exposure import calculate_route_exposure

app = FastAPI(title="AEROS API")

@app.get("/api/health")
def read_root():
    return {"status": "ok", "message": "AEROS API is running"}

@app.get("/api/db-check")
def read_db_check():
    return {"status": "ok", "message": "Database is running in mock offline mode"}

@app.get("/api/data/atmosphere")
async def read_atmosphere_data():
    # Fetch OpenAQ PM2.5 async
    openaq_data = await fetch_openaq_pm25()
    
    # Fetch Sentinel-5P NO2 mock
    sentinel_data = fetch_sentinel5p_no2_mock()
    
    return {
        "region": "Strasbourg, France",
        "coordinates": {"lat": 48.5734, "lon": 7.7521},
        "openaq_pm25": openaq_data,
        "sentinel5p_no2": sentinel_data
    }

@app.post("/api/exposure/compute")
async def compute_exposure(route_geojson: Dict[str, Any]):
    """
    Accepts a GeoJSON LineString (e.g. standard walking route) and calculates
    cumulative exposure mapping against AtmosphericGrid data.
    """
    try:
        result = calculate_route_exposure(route_geojson)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
