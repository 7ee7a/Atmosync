import React, { useState, useEffect, useMemo } from 'react';
import Map, { Source, Layer, Marker } from 'react-map-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { Activity, MapPin, Zap, AlertTriangle, Crosshair } from 'lucide-react';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

export default function App() {
  const [viewState, setViewState] = useState({
    longitude: 7.7521,
    latitude: 48.5734,
    zoom: 11,
    pitch: 45
  });

  const [atmosphereData, setAtmosphereData] = useState(null);
  const [routePoints, setRoutePoints] = useState([]);
  const [exposureData, setExposureData] = useState(null);
  const [isComputing, setIsComputing] = useState(false);

  useEffect(() => {
    fetch('/api/data/atmosphere')
      .then(res => res.json())
      .then(data => {
        setAtmosphereData(data);
      })
      .catch(err => console.error("Failed to fetch atmosphere data:", err));
  }, []);

  // Convert the Sentinel-5P mock grid into a GeoJSON Points FeatureCollection for heatmap
  const heatmapGeoJSON = useMemo(() => {
    if (!atmosphereData || !atmosphereData.sentinel5p_no2) return null;
    const { grid, bounds } = atmosphereData.sentinel5p_no2;
    const centerLat = bounds.center[0];
    const centerLon = bounds.center[1];
    const offsetDeg = (bounds.radius_km / 111.0); // Rough km to deg

    const features = [];
    const rows = grid.length;
    for (let r = 0; r < rows; r++) {
      const cols = grid[r].length;
      for (let c = 0; c < cols; c++) {
        // Map row/col to coordinate centered on Strasbourg
        const lat = centerLat + (offsetDeg * ((r / (rows - 1)) - 0.5));
        const lon = centerLon + (offsetDeg * ((c / (cols - 1)) - 0.5));
        features.push({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [lon, lat] },
          properties: { value: grid[r][c] }
        });
      }
    }
    return { type: 'FeatureCollection', features };
  }, [atmosphereData]);

  // Handle map clicks to draw routes
  const handleMapClick = (evt) => {
    const coords = [evt.lngLat.lng, evt.lngLat.lat];
    setRoutePoints(prev => {
      // If we already have 2 points, reset to just this new click
      if (prev.length >= 2) {
        setExposureData(null);
        return [coords];
      }
      return [...prev, coords];
    });
  };

  // Compute exposure when we have exactly 2 points
  useEffect(() => {
    if (routePoints.length === 2 && !exposureData) {
      setIsComputing(true);
      const geojsonLineString = {
        type: "Feature",
        geometry: {
          type: "LineString",
          coordinates: routePoints
        },
        properties: {}
      };

      fetch('/api/exposure/compute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(geojsonLineString)
      })
        .then(res => res.json())
        .then(res => {
          if (res.status === 'success') {
            setExposureData(res.data);
          } else {
            console.error("Compute error:", res);
          }
        })
        .catch(err => console.error("Endpoint crash:", err))
        .finally(() => setIsComputing(false));
    }
  }, [routePoints, exposureData]);

  const routeGeoJSON = useMemo(() => {
    if (routePoints.length < 2) return null;
    return {
      type: 'FeatureCollection',
      features: [{
        type: 'Feature',
        geometry: {
          type: 'LineString',
          coordinates: routePoints
        }
      }]
    };
  }, [routePoints]);

  return (
    <div className="relative w-screen h-screen bg-background overflow-hidden font-mono text-text">
      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        onClick={handleMapClick}
        mapboxAccessToken={MAPBOX_TOKEN}
        mapStyle="mapbox://styles/mapbox/dark-v11"
      >
        {/* Render Atmospheric Heatmap */}
        {heatmapGeoJSON && (
          <Source type="geojson" data={heatmapGeoJSON}>
            <Layer 
              id="atmosphere-heatmap"
              type="heatmap"
              paint={{
                'heatmap-weight': ['interpolate', ['linear'], ['get', 'value'], 0, 0, 3, 1],
                'heatmap-intensity': 1,
                'heatmap-color': [
                  'interpolate',
                  ['linear'],
                  ['heatmap-density'],
                  0, 'rgba(0,0,0,0)',
                  0.2, '#3b0f70', // Magma purple
                  0.4, '#8c2981',
                  0.6, '#de4968',
                  0.8, '#fe9f6d',
                  1, '#00FFFF' // Blending to neon cyan for extreme
                ],
                'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 2, 11, 40],
                'heatmap-opacity': 0.7
              }}
            />
          </Source>
        )}

        {/* Render Route Segment */}
        {routeGeoJSON && (
          <Source type="geojson" data={routeGeoJSON}>
            <Layer
              id="route-line"
              type="line"
              paint={{
                'line-color': '#00FFFF',
                'line-width': 4,
                'line-dasharray': [2, 2]
              }}
            />
          </Source>
        )}

        {/* Render Point Markers */}
        {routePoints.map((pt, i) => (
          <Marker key={i} longitude={pt[0]} latitude={pt[1]} anchor="center">
            <div className="w-4 h-4 bg-accent rounded-full border-2 border-background animate-pulse shadow-[0_0_10px_#00FFFF]" />
          </Marker>
        ))}
      </Map>

      {/* Telemetry UI Panel */}
      <div className="absolute top-6 left-6 w-96 backdrop-blur-md bg-background/80 border border-white/10 rounded-2xl p-6 shadow-2xl z-10 space-y-6">
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-3">
            <Activity className="text-accent w-6 h-6" />
            <h1 className="text-xl font-bold tracking-widest text-white">AEROS</h1>
          </div>
          <span className="text-xs font-semibold px-2 py-1 bg-white/10 rounded tracking-wider">TELEMETRY</span>
        </div>

        <div className="space-y-4 text-sm">
          <div className="flex justify-between items-center">
            <span className="text-white/60">SYSTEM STATUS</span>
            <span className="text-accent flex items-center gap-2">
              <div className="w-2 h-2 bg-accent rounded-full animate-ping" />
              ONLINE
            </span>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-white/60">ATMOSPHERE MOCK</span>
            <span className="text-white">
              {atmosphereData ? 'LOADED' : 'FETCHING...'}
            </span>
          </div>

          <div className="pt-4 border-t border-white/5 space-y-2">
            <h2 className="text-white/80 font-semibold mb-3 flex items-center gap-2">
              <Crosshair className="w-4 h-4" /> PATH TARGETING
            </h2>
            <div className="flex items-center gap-3">
              <div className={`w-2 h-2 rounded-full ${routePoints.length > 0 ? 'bg-accent' : 'bg-white/20'}`} />
              <span className={routePoints.length > 0 ? 'text-white' : 'text-white/40'}>Start Alpha</span>
            </div>
            <div className="flex items-center gap-3">
              <div className={`w-2 h-2 rounded-full ${routePoints.length > 1 ? 'bg-accent' : 'bg-white/20'}`} />
              <span className={routePoints.length > 1 ? 'text-white' : 'text-white/40'}>End Omega</span>
            </div>
          </div>
        </div>

        {(exposureData || isComputing) && (
          <div className="mt-6 pt-4 border-t border-white/10">
            <h2 className="text-xs text-white/50 mb-3 tracking-widest">EXPOSURE METRICS</h2>
            {isComputing ? (
              <div className="text-accent animate-pulse flex items-center gap-2">
                <Activity className="w-4 h-4" /> COMPUTING INDEX...
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex justify-between items-end">
                  <span className="text-3xl font-bold text-white">{exposureData.exposure_index}</span>
                  <span className="text-white/60 pb-1">IDX</span>
                </div>
                
                <div className={`flex items-center gap-2 px-3 py-2 rounded-lg bg-opacity-20 border
                  ${exposureData.risk_classification === 'High' ? 'bg-red-500 border-red-500/50 text-red-500' : 
                    exposureData.risk_classification === 'Medium' ? 'bg-yellow-500 border-yellow-500/50 text-yellow-500' : 
                    'bg-green-500 border-green-500/50 text-green-500'}`}
                >
                  <AlertTriangle className="w-5 h-5" />
                  <span className="font-bold tracking-wider">{exposureData.risk_classification.toUpperCase()} RISK</span>
                </div>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
