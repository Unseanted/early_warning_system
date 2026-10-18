from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: str = "community"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    phone: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


# ---------- Stations ----------
class StationCreate(BaseModel):
    name: str
    state: str
    latitude: float
    longitude: float
    river_name: Optional[str] = None


class StationOut(BaseModel):
    id: int
    name: str
    state: str
    latitude: float
    longitude: float
    river_name: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


# ---------- Prediction ----------
class PredictionInput(BaseModel):
    station_id: int
    daily_rainfall_mm: float = Field(..., ge=0, description="24h rainfall accumulation (mm)")
    river_level_m: float = Field(..., ge=0, description="River stage at nearest gauge (m)")
    antecedent_3day_rain_mm: float = Field(0, ge=0)
    antecedent_7day_rain_mm: float = Field(0, ge=0)
    temp_max_c: Optional[float] = None
    relative_humidity_pct: Optional[float] = None
    river_level_change_m: float = 0.0
    month: Optional[int] = Field(None, ge=1, le=12)


class ModelBranchOut(BaseModel):
    class_: int = Field(..., alias="class")
    label: str
    probabilities: Dict[str, float]
    available: Optional[bool] = True

    class Config:
        populate_by_name = True


class PredictionOut(BaseModel):
    id: int
    station_id: int
    prediction_timestamp: datetime
    predicted_risk_class: int
    risk_label: str
    probabilities: Dict[str, float]
    alert_triggered: bool
    recommended_action: str
    rf: Optional[Dict[str, Any]] = None
    lstm: Optional[Dict[str, Any]] = None
    ensemble_weights: Optional[Dict[str, float]] = None
    model_version: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Alerts ----------
class AlertCreate(BaseModel):
    station_id: int
    recipient_phone: str
    message: Optional[str] = None
    risk_level: Optional[int] = None


class AlertOut(BaseModel):
    id: int
    station_id: int
    recipient_phone: str
    message: str
    medium: str
    status: str
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    station_id: int
    phone: str
    min_risk_level: int = 2


class SubscriptionOut(BaseModel):
    id: int
    station_id: int
    phone: str
    min_risk_level: int
    is_active: bool

    class Config:
        from_attributes = True


# ---------- Dashboard ----------
class StationRiskSummary(BaseModel):
    station: StationOut
    latest_prediction: Optional[PredictionOut]
    trend: str
