from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
import json

from app.core.database import get_db
from app.models.db_models import Station, Prediction
from app.schemas.schemas import StationRiskSummary, StationOut, PredictionOut

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=List[StationRiskSummary])
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    stations = (await db.execute(select(Station).where(Station.is_active == True))).scalars().all()
    summaries = []

    for st in stations:
        pred_result = await db.execute(
            select(Prediction)
            .where(Prediction.station_id == st.id)
            .order_by(desc(Prediction.prediction_timestamp))
            .limit(2)
        )
        preds = pred_result.scalars().all()
        latest = preds[0] if preds else None
        prev = preds[1] if len(preds) > 1 else None

        trend = "stable"
        if latest and prev:
            if latest.predicted_risk_class > prev.predicted_risk_class:
                trend = "increasing"
            elif latest.predicted_risk_class < prev.predicted_risk_class:
                trend = "decreasing"

        latest_out = None
        if latest:
            latest_out = PredictionOut(
                id=latest.id,
                station_id=latest.station_id,
                prediction_timestamp=latest.prediction_timestamp,
                predicted_risk_class=latest.predicted_risk_class,
                risk_label=latest.risk_label,
                probabilities=json.loads(latest.ensemble_probabilities or "{}"),
                alert_triggered=latest.alert_triggered,
                recommended_action="",
            )

        summaries.append(
            StationRiskSummary(
                station=StationOut.model_validate(st),
                latest_prediction=latest_out,
                trend=trend,
            )
        )
    return summaries
