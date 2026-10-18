from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.models.db_models import Station
from app.schemas.schemas import StationCreate, StationOut

router = APIRouter(prefix="/stations", tags=["Stations"])


@router.get("/", response_model=List[StationOut])
async def list_stations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Station).where(Station.is_active == True))
    return result.scalars().all()


@router.post("/", response_model=StationOut)
async def create_station(station: StationCreate, db: AsyncSession = Depends(get_db)):
    obj = Station(**station.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("/{station_id}", response_model=StationOut)
async def get_station(station_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Station).where(Station.id == station_id))
    station = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station
