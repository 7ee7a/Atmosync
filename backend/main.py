from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from .database import engine, Base, get_db
from .services.strasbourg import fetch_openaq_pm25, fetch_sentinel5p_no2_mock

# Create models
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AEROS API")

@app.get("/api/health")
def read_root():
    return {"status": "ok", "message": "AEROS API is running"}

@app.get("/api/db-check")
def read_db_check(db: Session = Depends(get_db)):
    try:
        # Check if PostGIS extension is installed
        result = db.execute(text("SELECT postgis_version()")).scalar()
        return {"status": "ok", "postgis_version": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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

