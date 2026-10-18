"""
Live meteorological feeds for study areas.
Uses Open-Meteo (free) as a realistic public substitute for NiMet station data.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Any
from app.services.data_feed_service import (
    get_station_live_features,
    get_all_stations_live,
    get_nimet_info,
    STATION_COORDS,
)

router = APIRouter(prefix="/feeds", tags=["Data Feeds (NiMet / Open-Meteo)"])


@router.get(
    "/live",
    summary="Live features for all study areas",
    description="Fetches current rainfall, temperature, humidity from Open-Meteo for Makurdi, Lokoja, Onitsha and derives model-ready features (including river-level proxy).",
)
async def live_all():
    return await get_all_stations_live()


@router.get(
    "/live/{station_name}",
    summary="Live features for one study area",
)
async def live_one(station_name: str):
    name = station_name.title()
    if name not in STATION_COORDS:
        raise HTTPException(status_code=404, detail=f"Unknown station. Choose: {list(STATION_COORDS.keys())}")
    try:
        return await get_station_live_features(name)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream weather API error: {e}")


@router.get(
    "/nimet-info",
    summary="NiMet integration notes for defense",
)
async def nimet_info():
    return get_nimet_info()


@router.get("/stations-coords")
async def stations_coords():
    return STATION_COORDS
