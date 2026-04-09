import random
from datetime import datetime, timezone
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def fetch_openaq_pm25() -> Dict[str, Any]:
    """
    Simulated mock for OpenAQ PM2.5 data in Strasbourg for offline demo.
    """
    center_lat, center_lon = 48.5734, 7.7521
    points = []
    
    # Generate 5 random sensor points around Strasbourg
    for i in range(5):
        lat = center_lat + random.uniform(-0.05, 0.05)
        lon = center_lon + random.uniform(-0.05, 0.05)
        
        points.append({
            "location": f"Simulated Sensor Alpha-{i}",
            "coordinates": {"latitude": lat, "longitude": lon},
            "value": round(random.uniform(5.0, 35.0), 2),
            "unit": "µg/m³",
            "lastUpdated": datetime.now(timezone.utc).isoformat()
        })
        
    return {"status": "success", "data": points}

def fetch_sentinel5p_no2_mock() -> Dict[str, Any]:
    """
    Placeholder for fetching Sentinel-5P NO2 data using Google Earth Engine.
    For now, returns a mock 2D array representing a grid of pollution values
    around Strasbourg.
    """
    # In a real scenario, we would `ee.Initialize()` and perform image collection analysis.
    
    # Returning a 5x5 Grid for demo purposes.
    mock_grid = [
        [1.2, 1.3, 1.4, 1.3, 1.1],
        [1.3, 1.5, 1.8, 1.5, 1.2],
        [1.5, 1.9, 2.5, 1.8, 1.4],
        [1.4, 1.7, 2.1, 1.6, 1.3],
        [1.1, 1.2, 1.4, 1.2, 1.0]
    ]
    
    return {
        "status": "success",
        "source": "Sentinel-5P NO2 (Mock)",
        "bounds": {
            "center": [48.5734, 7.7521],
            "radius_km": 10
        },
        "grid": mock_grid,
        "unit": "mol/m^2"
    }
