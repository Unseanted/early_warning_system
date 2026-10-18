# FRPEWS – Flood Risk Prediction & Early Warning System

Full-stack thesis prototype for **vulnerable Nigerian communities** (Makurdi, Lokoja, Onitsha).

| Component | Implementation |
|-----------|----------------|
| Models | **Random Forest** (200 trees) + **LSTM** (2× layers) → **ensemble 0.5/0.5** |
| Accuracy (Ch. 4) | RF 87.3% · LSTM 88.6% · Ensemble **89.4%** |
| Frontend | React 18 + Vite |
| Backend | FastAPI · SQLAlchemy · SQLite |
| Data feeds | **Open-Meteo** (live, no key) · NiMet API path documented |
| Alerts | Twilio SMS (demo mode without credentials) |

---

## Quick start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt   # includes tensorflow
cp .env.example .env              # optional Twilio / NIMET keys
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**
- Metrics: **http://localhost:8000/api/predictions/metrics**
- Live feeds: **http://localhost:8000/api/feeds/live**

First startup trains RF + LSTM (may take 1–3 minutes on CPU). Models are saved under `backend/models/`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173**

---

## API overview (also in /docs)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/predictions/predict` | Ensemble prediction (RF + LSTM) |
| GET | `/api/predictions/metrics` | Chapter 4 performance figures |
| GET | `/api/feeds/live` | Live Open-Meteo features for all study areas |
| GET | `/api/feeds/live/{Makurdi\|Lokoja\|Onitsha}` | Single-station live features |
| GET | `/api/feeds/nimet-info` | How NiMet would be wired with an API key |
| GET | `/api/dashboard/summary` | Station risk cards |
| POST | `/api/alerts/send` | Manual SMS |
| POST | `/api/alerts/subscribe` | Subscribe phone to High/Extreme alerts |

---

## Defense talking points

1. **Ensemble** matches thesis §4.4.3 (weights 0.5/0.5; ensemble outperforms either model alone).
2. **LSTM** architecture: 30-day lookback → 2 stacked LSTM (128→64) + Dropout + Dense → 4-class softmax (§3.3.2.2).
3. **Feature importance**: river level > 3-day rain > daily rain > 7-day rain (§4.4.1).
4. **Live feeds**: Open-Meteo supplies rainfall/temp/humidity for the three coordinates; river level is a documented rainfall proxy until NIHSA gauges are connected.
5. **NiMet**: Official API exists (`api.nimet.gov.ng`) and requires a key; `/api/feeds/nimet-info` documents the integration path.
6. **SMS last-mile**: Twilio templates for High/Extreme; demo mode logs messages when credentials are absent.

---

## Project layout
```
frpews/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/  models/  routers/  schemas/  services/
│   │   └── services/ml_service.py      # RF + LSTM + ensemble
│   │   └── services/data_feed_service.py  # Open-Meteo / NiMet notes
│   ├── models/          # created at first run
│   └── requirements.txt
├── frontend/
│   └── src/pages/       # Dashboard, Predict, Alerts, About
└── README.md
```

Default admin: `admin@frpews.local` / `Admin123!`

Academic / educational use – Final Year Project prototype.
