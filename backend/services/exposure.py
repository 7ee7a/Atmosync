from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.shape import to_shape
from shapely.geometry import shape, LineString
import json

from ..models import AtmosphericGrid

def calculate_route_exposure(route_geojson: dict, db: Session):
    """
    Given a GeoJSON LineString representing a walking route, calculate the cumulative
    pollution exposure index by sampling underlying AtmosphericGrid polygons.
    """
    
    # 1. Parse route GeoJSON and create Shapely LineString
    try:
        if route_geojson.get("type") == "Feature":
            geom_dict = route_geojson["geometry"]
        else:
            geom_dict = route_geojson
            
        route_shape = shape(geom_dict)
        if not isinstance(route_shape, LineString):
            raise ValueError("Provided GeoJSON must be a LineString.")
    except Exception as e:
        raise ValueError(f"Invalid GeoJSON: {e}")
        
    # Serialize to WKT to use in PostGIS query
    route_wkt = route_shape.wkt
    
    # 2. Query intersecting AtmosphericGrid polygons
    # ST_Intersects uses the index correctly.
    query = db.query(AtmosphericGrid).filter(
        func.ST_Intersects(
            AtmosphericGrid.geom, 
            func.ST_GeomFromText(route_wkt, 4326)
        )
    )
    
    grids = query.all()
    
    if not grids:
        return {
            "exposure_index": 0.0,
            "risk_classification": "Unknown - No Data",
            "segments_analyzed": 0
        }
        
    total_weighted_pollution = 0.0
    total_length = 0.0
    
    # 3. Calculate intersections and weights using Shapely
    for grid in grids:
        grid_shape = to_shape(grid.geom)
        
        # Intersect the route with this polygon grid
        intersection = route_shape.intersection(grid_shape)
        
        if not intersection.is_empty:
            segment_length = intersection.length
            total_weighted_pollution += (segment_length * float(grid.value))
            total_length += segment_length
            
    if total_length == 0:
        return {
            "exposure_index": 0.0,
            "risk_classification": "Low",
            "segments_analyzed": len(grids)
        }
        
    exposure_index = total_weighted_pollution / total_length
    
    # 4. Classify Risk
    if exposure_index < 12.0:
        risk = "Low"
    elif exposure_index < 35.4:
        risk = "Medium"
    else:
        risk = "High"
        
    return {
        "exposure_index": round(exposure_index, 2),
        "risk_classification": risk,
        "segments_analyzed": len(grids),
        "route_length_deg": round(total_length, 5)
    }
