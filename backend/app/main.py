from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.db_models import User, Station
from app.routers import auth, stations, predictions, alerts, dashboard, data_feeds
from app.services.ml_service import ensure_models_trained

settings = get_settings()


async def seed_data():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == settings.admin_email))
        if not result.scalar_one_or_none():
            admin = User(
                email=settings.admin_email,
                hashed_password=get_password_hash(settings.admin_password),
                full_name="FRPEWS Admin",
                role="admin",
                phone="+2348000000000",
            )
            db.add(admin)

        stations_data = [
            {"name": "Makurdi", "state": "Benue", "latitude": 7.73, "longitude": 8.52, "river_name": "Benue River"},
            {"name": "Lokoja", "state": "Kogi", "latitude": 7.80, "longitude": 6.74, "river_name": "Niger-Benue Confluence"},
            {"name": "Onitsha", "state": "Anambra", "latitude": 6.17, "longitude": 6.78, "river_name": "River Niger"},
        ]
        for s in stations_data:
            exists = await db.execute(select(Station).where(Station.name == s["name"]))
            if not exists.scalar_one_or_none():
                db.add(Station(**s))
        await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_data()
    ensure_models_trained()
    print("[FRPEWS] Backend ready – RF+LSTM ensemble loaded, DB seeded.")
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description=(
        "Machine-learning Flood Risk Prediction & Early Warning System for Nigerian communities.\n\n"
        "**Thesis prototype** – Random Forest + LSTM ensemble, Open-Meteo/NiMet-style feeds, Twilio SMS.\n\n"
        "Study areas: Makurdi (Benue), Lokoja (Kogi), Onitsha (Anambra).\n\n"
        "Interactive API docs: `/docs` (Swagger) · `/redoc`"
    ),
    version="1.1.0",
    lifespan=lifespan,
    contact={"name": "FRPEWS Project", "email": "admin@frpews.local"},
    license_info={"name": "Academic / Educational use"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(stations.router, prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(data_feeds.router, prefix="/api")


@app.get("/", tags=["System"])
async def root():
    return {
        "name": settings.app_name,
        "version": "1.1.0",
        "status": "online",
        "docs": "/docs",
        "redoc": "/redoc",
        "study_areas": ["Makurdi (Benue)", "Lokoja (Kogi)", "Onitsha (Anambra)"],
        "models": ["RandomForest", "LSTM", "Ensemble (0.5/0.5)"],
        "feeds": "/api/feeds/live",
        "metrics": "/api/predictions/metrics",
    }


@app.get("/health", tags=["System"])
async def health():
    return {"status": "healthy"}
