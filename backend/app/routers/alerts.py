from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.db_models import Alert, AlertSubscription, Station
from app.schemas.schemas import AlertCreate, AlertOut, SubscriptionCreate, SubscriptionOut
from app.services.twilio_service import send_sms, build_alert_message

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=List[AlertOut])
async def list_alerts(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).order_by(desc(Alert.created_at)).limit(limit))
    return result.scalars().all()


@router.post("/send", response_model=AlertOut)
async def send_manual_alert(payload: AlertCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Station).where(Station.id == payload.station_id))
    station = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    msg = payload.message or build_alert_message(
        station.name, {0: "Low", 1: "Moderate", 2: "High", 3: "Extreme"}.get(payload.risk_level or 2, "High")
    )
    tw = send_sms(payload.recipient_phone, msg)

    alert = Alert(
        station_id=payload.station_id,
        recipient_phone=payload.recipient_phone,
        message=msg,
        medium="SMS",
        status=tw.get("status", "failed"),
        sent_at=datetime.utcnow() if tw.get("status") in ("sent", "demo_sent") else None,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


@router.post("/subscribe", response_model=SubscriptionOut)
async def subscribe(payload: SubscriptionCreate, db: AsyncSession = Depends(get_db)):
    # Simple open subscription (no auth for demo)
    sub = AlertSubscription(
        user_id=1,  # demo user
        station_id=payload.station_id,
        phone=payload.phone,
        min_risk_level=payload.min_risk_level,
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub


@router.get("/subscriptions", response_model=List[SubscriptionOut])
async def list_subscriptions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlertSubscription).where(AlertSubscription.is_active == True))
    return result.scalars().all()
