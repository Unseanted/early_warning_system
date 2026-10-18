from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
import json
from datetime import datetime

from app.core.database import get_db
from app.models.db_models import Station, Prediction, Alert, AlertSubscription
from app.schemas.schemas import PredictionInput, PredictionOut
from app.services.ml_service import predict_risk, get_metrics
from app.services.twilio_service import send_sms, build_alert_message

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post(
    "/predict",
    response_model=PredictionOut,
    summary="Run ensemble flood-risk prediction (RF + LSTM)",
    description="Accepts meteorological/hydrological features and returns ensemble risk class with RF and LSTM breakdowns. High/Extreme triggers SMS to subscribers.",
)
async def create_prediction(payload: PredictionInput, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Station).where(Station.id == payload.station_id))
    station = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    ml_result = predict_risk(
        daily_rainfall_mm=payload.daily_rainfall_mm,
        river_level_m=payload.river_level_m,
        antecedent_3day_rain_mm=payload.antecedent_3day_rain_mm,
        antecedent_7day_rain_mm=payload.antecedent_7day_rain_mm,
        river_level_change_m=payload.river_level_change_m,
        month=payload.month,
    )

    risk_class = ml_result["predicted_risk_class"]
    risk_label = ml_result["risk_label"]
    alert_triggered = risk_class >= 2

    pred = Prediction(
        station_id=payload.station_id,
        daily_rainfall_mm=payload.daily_rainfall_mm,
        river_level_m=payload.river_level_m,
        antecedent_3day_rain_mm=payload.antecedent_3day_rain_mm,
        rf_probabilities=json.dumps(ml_result.get("rf", {}).get("probabilities", {})),
        ensemble_probabilities=json.dumps(ml_result["probabilities"]),
        predicted_risk_class=risk_class,
        risk_label=risk_label,
        alert_triggered=alert_triggered,
    )
    db.add(pred)
    await db.commit()
    await db.refresh(pred)

    if alert_triggered:
        subs = await db.execute(
            select(AlertSubscription).where(
                AlertSubscription.station_id == payload.station_id,
                AlertSubscription.is_active == True,
                AlertSubscription.min_risk_level <= risk_class,
            )
        )
        for sub in subs.scalars().all():
            msg = build_alert_message(station.name, risk_label)
            tw_result = send_sms(sub.phone, msg)
            alert = Alert(
                prediction_id=pred.id,
                station_id=payload.station_id,
                recipient_phone=sub.phone,
                message=msg,
                medium="SMS",
                status=tw_result.get("status", "failed"),
                sent_at=datetime.utcnow() if tw_result.get("status") in ("sent", "demo_sent") else None,
            )
            db.add(alert)
        await db.commit()

    return PredictionOut(
        id=pred.id,
        station_id=pred.station_id,
        prediction_timestamp=pred.prediction_timestamp,
        predicted_risk_class=risk_class,
        risk_label=risk_label,
        probabilities=ml_result["probabilities"],
        alert_triggered=alert_triggered,
        recommended_action=ml_result["recommended_action"],
        rf=ml_result.get("rf"),
        lstm=ml_result.get("lstm"),
        ensemble_weights=ml_result.get("ensemble_weights"),
        model_version=ml_result.get("model_version"),
    )


@router.get("/latest", response_model=List[PredictionOut])
async def latest_predictions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Prediction).order_by(desc(Prediction.prediction_timestamp)).limit(20)
    )
    preds = result.scalars().all()
    out = []
    for p in preds:
        probs = json.loads(p.ensemble_probabilities or "{}")
        out.append(
            PredictionOut(
                id=p.id,
                station_id=p.station_id,
                prediction_timestamp=p.prediction_timestamp,
                predicted_risk_class=p.predicted_risk_class,
                risk_label=p.risk_label,
                probabilities=probs,
                alert_triggered=p.alert_triggered,
                recommended_action="",
            )
        )
    return out


@router.get("/station/{station_id}", response_model=List[PredictionOut])
async def station_predictions(station_id: int, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Prediction)
        .where(Prediction.station_id == station_id)
        .order_by(desc(Prediction.prediction_timestamp))
        .limit(limit)
    )
    preds = result.scalars().all()
    return [
        PredictionOut(
            id=p.id,
            station_id=p.station_id,
            prediction_timestamp=p.prediction_timestamp,
            predicted_risk_class=p.predicted_risk_class,
            risk_label=p.risk_label,
            probabilities=json.loads(p.ensemble_probabilities or "{}"),
            alert_triggered=p.alert_triggered,
            recommended_action="",
        )
        for p in preds
    ]


@router.get(
    "/metrics",
    summary="Model performance metrics (Chapter 4 results)",
    description="Returns RF, LSTM and ensemble accuracy figures aligned with thesis evaluation.",
)
async def model_metrics():
    return get_metrics()
