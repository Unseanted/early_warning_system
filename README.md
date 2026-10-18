# FRPEWS – Flood Risk Prediction & Early Warning System

FRPEWS is a full-stack web application for monitoring and predicting flood risk in vulnerable Nigerian communities. The application combines a React dashboard, a FastAPI backend, live weather data, machine-learning predictions, and SMS alert management for three study areas:

- **Makurdi, Benue** — Benue River
- **Lokoja, Kogi** — Niger–Benue Confluence
- **Onitsha, Anambra** — River Niger

It is designed as an academic and educational final-year project prototype.

## What the application does

### Flood risk dashboard

The Dashboard page provides a station-by-station view of the latest prediction for Makurdi, Lokoja, and Onitsha. Each station card can display:

- Current risk classification: **Low**, **Moderate**, **High**, or **Extreme**
- Risk trend: increasing, decreasing, or stable
- Last prediction time
- Probability distribution across the four risk classes
- High- and Extreme-risk warnings when applicable

### Interactive flood prediction

The Predict page allows users to run an ensemble flood-risk prediction by entering or loading:

- Daily rainfall in millimetres
- Current river level in metres
- Three-day antecedent rainfall
- Seven-day antecedent rainfall
- Change in river level
- Month of the year
- Monitoring station

Users can either enter values manually, choose safe/moderate/high/extreme presets, or load the latest available station data from the live feed. The prediction result includes the ensemble risk level, recommended action, class probabilities, individual Random Forest and LSTM outputs, and whether an SMS alert was triggered.

### Alert management

The Alerts page supports two workflows:

1. **Send a manual SMS alert** to a phone number using a station-specific risk template or a custom message.
2. **Subscribe a phone number** to receive alerts when a selected station reaches a configured minimum risk level.

Twilio credentials enable live SMS delivery. When Twilio credentials are not configured, the application runs in demo mode and logs the message instead of sending it.

### Project and model information

The About page presents the technology stack, thesis-aligned performance figures, data-source information, and local setup instructions. It also explains the Open-Meteo demo feed and the documented NiMet integration path.

## Technology stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, React Router, Axios, Recharts, Lucide React |
| Backend | FastAPI, Uvicorn, Pydantic Settings |
| Database | SQLAlchemy async ORM, SQLite, aiosqlite |
| Machine learning | scikit-learn Random Forest and TensorFlow/Keras LSTM |
| Weather data | Open-Meteo live feed; NiMet integration path documented |
| Notifications | Twilio SMS with demo mode when credentials are absent |
| Authentication | JWT-based backend authentication with a seeded admin account |

## Prediction model

The backend combines two model outputs into a 50/50 ensemble:

- **Random Forest:** 200 trees
- **LSTM:** two stacked recurrent layers with dropout and a four-class softmax output
- **Ensemble:** Random Forest probability × 0.5 + LSTM probability × 0.5

The four prediction classes are **Low**, **Moderate**, **High**, and **Extreme**. The thesis-aligned performance figures exposed by the application are:

| Model | Accuracy |
|-------|----------|
| Random Forest | 87.3% |
| LSTM | 88.6% |
| Ensemble | **89.4%** |

The model metrics also document the expected advance-warning period and the leading features used in the thesis analysis. On the first backend startup, the required model artifacts are trained or prepared and stored under `backend/models/`.

> **Data note:** Open-Meteo supplies live meteorological features. River-level values currently use the documented rainfall-based proxy until direct NIHSA gauge data is connected. The NiMet endpoint and integration requirements are documented by the backend API.

## Quick start

### Prerequisites

- Python 3.10 or newer
- Node.js and npm
- Optional: Twilio account credentials for live SMS delivery

### 1. Start the backend

From the repository root:

```bash
cd backend
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows PowerShell
# .\\venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
cp .env.example .env              # Optional: configure Twilio values
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend URLs:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

The first startup creates the SQLite database, seeds the three monitoring stations and admin account, and prepares the machine-learning models. Model preparation may take several minutes on a CPU-only machine.

### 2. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the application at:

```text
http://localhost:5173
```

The frontend expects the FastAPI backend to be available on port `8000`.

## Environment configuration

Backend settings are loaded from `backend/.env`. The main optional notification settings are:

```env
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

If these values are empty, SMS requests are recorded in demo mode. Change the default secret and admin credentials before using the application outside a local academic demonstration.

The default seeded admin account is:

```text
Email:    admin@frpews.local
Password: Admin123!
```

## API overview

Interactive API documentation is available at `/docs` when the backend is running.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/health` | Check backend health |
| `POST` | `/api/auth/login` | Authenticate a user |
| `GET` | `/api/stations` | List monitoring stations |
| `GET` | `/api/dashboard/summary` | Retrieve station cards and latest risk data |
| `POST` | `/api/predictions/predict` | Run an RF + LSTM ensemble prediction |
| `GET` | `/api/predictions/metrics` | Retrieve thesis-aligned model metrics |
| `GET` | `/api/feeds/live` | Retrieve live features for all study areas |
| `GET` | `/api/feeds/live/{station}` | Retrieve live features for one station |
| `GET` | `/api/feeds/nimet-info` | View NiMet integration information |
| `GET` | `/api/alerts` | List recent alert records |
| `POST` | `/api/alerts/send` | Send or log a manual SMS alert |
| `POST` | `/api/alerts/subscribe` | Subscribe a phone number to risk alerts |

## Project structure

```text
early_warning_system/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/                  # Settings, database, security
│   │   ├── models/                # SQLAlchemy database models
│   │   ├── routers/               # Auth, stations, predictions, alerts, dashboard, feeds
│   │   ├── schemas/               # Request and response schemas
│   │   └── services/
│   │       ├── ml_service.py      # Random Forest, LSTM, and ensemble logic
│   │       └── data_feed_service.py # Open-Meteo and NiMet feed integration
│   ├── models/                    # Generated model artifacts
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx      # Station risk overview
│   │   │   ├── Predict.jsx        # Interactive prediction form
│   │   │   ├── Alerts.jsx         # SMS and subscription management
│   │   │   └── About.jsx           # Project, metrics, and setup information
│   │   └── App.jsx                # Navigation and application routes
│   └── package.json
└── README.md
```

## Thesis and defense highlights

- The ensemble combines Random Forest and LSTM predictions with equal weights.
- The application exposes the individual model outputs as well as the combined result.
- Flood risk is classified into four operational levels: Low, Moderate, High, and Extreme.
- Live weather data can be loaded directly into the prediction form.
- High- and Extreme-risk predictions can trigger SMS notifications for subscribers.
- Open-Meteo is used as the accessible demonstration feed, while NiMet and direct river-gauge integration are documented extension points.

## Academic disclaimer

FRPEWS is an academic/educational prototype for flood-risk research and demonstration. Its predictions should not be treated as an official emergency-warning service without validation against authoritative hydrological data, operational monitoring infrastructure, and the relevant Nigerian emergency-management authorities.
