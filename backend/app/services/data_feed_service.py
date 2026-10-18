"""
Meteorological data feeds for FRPEWS study areas.

Primary source: Open-Meteo (free, no API key) – used as a realistic public
substitute for NiMet/NIHSA station data during development and defense demos.
Coordinates match thesis study areas: Makurdi, Lokoja, Onitsha.

NiMet official API (https://api.nimet.gov.ng) requires registration/API key;
when a key is provided via NIMET_API_KEY it can be extended here.
"""
from __future__ import annotations
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.core.config import get_settings

# Thesis study-area coordinates
STATION_COORDS = {
    "Makurdi": {"lat": 7.73, "lon": 8.52, "state": "Benue"},
    "Lokoja": {"lat": 7.80, "lon": 6.74, "state": "Kogi"},
    "Onitsha": {"lat": 6.17, "lon": 6.78, "state": "Anambra"},
}


async def fetch_open_meteo_forecast(lat: float, lon: float, days: int = 7) -> Dict[str, Any]:
    """Current + daily forecast from Open-Meteo (no key required)."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,rain",
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min,rain_sum",
        "timezone": "Africa/Lagos",
        "forecast_days": days,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()


async def fetch_open_meteo_historical(
    lat: float, lon: float, start: str, end: str
) -> Dict[str, Any]:
    """
    Historical daily rainfall & temperature (ERA5-based).
    start/end format: YYYY-MM-DD
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": "precipitation_sum,temperature_2m_max,relative_humidity_2m_mean",
        "timezone": "Africa/Lagos",
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()


async def get_station_live_features(station_name: str) -> Dict[str, Any]:
    """
    Build model-ready feature vector from live Open-Meteo data for a study area.
    River level is estimated from recent rainfall (proxy) for demo purposes;
    in production this would come from NIHSA gauge stations.
    """
    coords = STATION_COORDS.get(station_name)
    if not coords:
        raise ValueError(f"Unknown station: {station_name}")

    data = await fetch_open_meteo_forecast(coords["lat"], coords["lon"], days=7)
    current = data.get("current", {})
    daily = data.get("daily", {})

    precip_today = float(current.get("precipitation") or current.get("rain") or 0.0)
    temp = float(current.get("temperature_2m") or 28.0)
    humidity = float(current.get("relative_humidity_2m") or 70.0)

    # Last 3 and 7 days rain from daily series (if available)
    rains = daily.get("precipitation_sum") or [0.0] * 7
    ante_3d = float(sum(rains[:3])) if rains else precip_today * 2.5
    ante_7d = float(sum(rains[:7])) if rains else precip_today * 5.0

    # Simple hydrological proxy for river level (thesis uses real NIHSA gauges)
    # Base levels approximate typical dry-season stages at each site
    base_level = {"Makurdi": 4.2, "Lokoja": 5.5, "Onitsha": 4.8}.get(station_name, 4.5)
    river_level = round(base_level + ante_3d * 0.04 + precip_today * 0.02, 2)
    level_change = round(precip_today * 0.015, 3)

    return {
        "source": "Open-Meteo (public feed – NiMet-compatible variables)",
        "station": station_name,
        "state": coords["state"],
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "daily_rainfall_mm": round(precip_today, 2),
        "temp_max_c": round(temp, 1),
        "relative_humidity_pct": round(humidity, 1),
        "antecedent_3day_rain_mm": round(ante_3d, 2),
        "antecedent_7day_rain_mm": round(ante_7d, 2),
        "river_level_m": river_level,
        "river_level_change_m": level_change,
        "month": datetime.utcnow().month,
        "forecast_daily_rain_mm": [round(float(x or 0), 2) for x in rains[:7]],
        "note": "River level is a rainfall-based proxy for demo. Live NIHSA gauges would replace this in field deployment.",
    }


async def get_all_stations_live() -> List[Dict[str, Any]]:
    results = []
    for name in STATION_COORDS:
        try:
            results.append(await get_station_live_features(name))
        except Exception as e:
            results.append({"station": name, "error": str(e)})
    return results


def get_nimet_info() -> Dict[str, Any]:
    """Documentation block for defense: how NiMet would be integrated."""
    settings = get_settings()
    return {
        "nimet_base_url": "https://api.nimet.gov.ng/api",
        "status": "API key required – register at nimet.gov.ng",
        "api_key_configured": bool(getattr(settings, "nimet_api_key", None)),
        "endpoints_of_interest": [
            "GET /historical-data/:date",
            "GET /forecast/{location}",
        ],
        "current_demo_source": "Open-Meteo (ERA5 + NWP) – free, no key, same variables (rainfall, temp, humidity)",
        "thesis_alignment": "NiMet station records + CHIRPS gap-filling + NIHSA river gauges (Chapter 3.5)",
    }
