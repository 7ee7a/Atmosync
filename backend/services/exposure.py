from shapely.geometry import shape, LineString, Polygon
import json
from .strasbourg import fetch_sentinel5p_no2_mock

def calculate_route_exposure(route_geojson: dict):
    """
    Given a GeoJSON LineString representing a walking route, calculate the cumulative
    pollution exposure index by sampling underlying mocked NO2 grids dynamically in memory.
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
        
    # 2. Setup mock grids instead of DB queries
    data = fetch_sentinel5p_no2_mock()
    grid = data.get("sentinel5p_no2", data).get("grid", [])
    bounds = data.get("sentinel5p_no2", data).get("bounds", {"center": [48.5734, 7.7521], "radius_km": 10})
    
    center_lat, center_lon = bounds["center"]
    offset_deg = bounds["radius_km"] / 111.0 # Approximate km to deg
    
    rows = len(grid)
    if rows == 0:
        return {"exposure_index": 0.0, "risk_classification": "Unknown", "segments_analyzed": 0}
        
    cols = len(grid[0])
    cell_height = offset_deg * 2 / rows
    cell_width = offset_deg * 2 / cols
    
    total_weighted_pollution = 0.0
    total_length = 0.0
    segments_analyzed = 0
    
    # 3. Calculate intersections and weights using Shapely
    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            
            # Map row/col to coordinate bounding box
            lat = center_lat + (offset_deg * ((r / (rows - 1)) - 0.5))
            lon = center_lon + (offset_deg * ((c / (cols - 1)) - 0.5))
            
            # Create a localized cell polygon
            minx = lon - cell_width / 2
            maxx = lon + cell_width / 2
            miny = lat - cell_height / 2
            maxy = lat + cell_height / 2
            
            cell_poly = Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)])
            
            # Intersect
            intersection = route_shape.intersection(cell_poly)
            if not intersection.is_empty:
                segment_length = intersection.length
                total_weighted_pollution += (segment_length * float(val))
                total_length += segment_length
                segments_analyzed += 1
            
    if total_length == 0:
        return {
            "exposure_index": 0.0,
            "risk_classification": "Low",
            "segments_analyzed": segments_analyzed,
            "route_length_deg": 0.0
        }
        
    exposure_index = total_weighted_pollution / total_length
    
    # 4. Classify Risk
    if exposure_index < 1.25:
        risk = "Low"
    elif exposure_index < 1.55:
        risk = "Medium"
    else:
        risk = "High"
        
    return {
        "exposure_index": round(exposure_index, 3),
        "risk_classification": risk,
        "segments_analyzed": segments_analyzed,
        "route_length_deg": round(total_length, 5)
    }
