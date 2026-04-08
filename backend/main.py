from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from .database import engine, Base, get_db

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
