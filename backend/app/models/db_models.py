from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=True)
    role = Column(String(20), default="community")  # admin | data_manager | community
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    river_name = Column(String(80), nullable=True)
    is_active = Column(Boolean, default=True)


class EnvironmentalData(Base):
    __tablename__ = "environmental_data"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    daily_rainfall_mm = Column(Float, default=0.0)
    temp_max_c = Column(Float, nullable=True)
    relative_humidity_pct = Column(Float, nullable=True)
    river_level_m = Column(Float, nullable=False)
    antecedent_3day_rain_mm = Column(Float, default=0.0)
    antecedent_7day_rain_mm = Column(Float, default=0.0)
    river_level_change_m = Column(Float, default=0.0)
    month = Column(Integer, nullable=True)
    flood_risk_class = Column(Integer, default=0)  # 0=Low,1=Moderate,2=High,3=Extreme
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    prediction_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    daily_rainfall_mm = Column(Float)
    river_level_m = Column(Float)
    antecedent_3day_rain_mm = Column(Float)
    rf_probabilities = Column(Text)  # JSON string
    ensemble_probabilities = Column(Text)
    predicted_risk_class = Column(Integer)  # 0-3
    risk_label = Column(String(20))
    alert_triggered = Column(Boolean, default=False)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    medium = Column(String(20), default="SMS")
    status = Column(String(20), default="pending")  # pending | sent | failed
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AlertSubscription(Base):
    __tablename__ = "alert_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    phone = Column(String(20), nullable=False)
    min_risk_level = Column(Integer, default=2)  # trigger from High onwards
    is_active = Column(Boolean, default=True)
