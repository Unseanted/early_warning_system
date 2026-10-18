import { useEffect, useState } from 'react'
import { getMetrics, getNimetInfo } from '../api'

export default function About() {
  const [metrics, setMetrics] = useState(null)
  const [nimet, setNimet] = useState(null)

  useEffect(() => {
    getMetrics().then((r) => setMetrics(r.data)).catch(() => {})
    getNimetInfo().then((r) => setNimet(r.data)).catch(() => {})
  }, [])

  return (
    <>
      <h1 className="page-title">About FRPEWS</h1>
      <p className="page-subtitle">Flood Risk Prediction & Early Warning System – Final Year Project Prototype</p>

      <div className="card" style={{ maxWidth: 860, lineHeight: 1.7, marginBottom: '1.25rem' }}>
        <h3 style={{ marginBottom: '0.75rem' }}>Project Context</h3>
        <p style={{ color: 'var(--muted)', marginBottom: '1rem' }}>
          Full-stack implementation of the thesis architecture: Random Forest + LSTM ensemble,
          web dashboard, Twilio SMS alerts, and live meteorological feeds for Makurdi, Lokoja and Onitsha.
        </p>

        <h3 style={{ marginBottom: '0.75rem' }}>Tech Stack</h3>
        <ul style={{ color: 'var(--muted)', paddingLeft: '1.25rem', marginBottom: '1rem' }}>
          <li><strong>Frontend:</strong> React 18 + Vite</li>
          <li><strong>Backend:</strong> FastAPI + SQLAlchemy (async SQLite)</li>
          <li><strong>ML:</strong> scikit-learn RandomForest + TensorFlow/Keras LSTM → ensemble</li>
          <li><strong>Data feeds:</strong> Open-Meteo (public) · NiMet API ready when key available</li>
          <li><strong>SMS:</strong> Twilio (demo mode without credentials)</li>
        </ul>

        <h3 style={{ marginBottom: '0.75rem' }}>Chapter 4 Performance (thesis-aligned)</h3>
        {metrics?.chapter4_highlights ? (
          <ul style={{ color: 'var(--muted)', paddingLeft: '1.25rem', marginBottom: '1rem' }}>
            <li>RF accuracy: {(metrics.chapter4_highlights.rf_accuracy * 100).toFixed(1)}%</li>
            <li>LSTM accuracy: {(metrics.chapter4_highlights.lstm_accuracy * 100).toFixed(1)}%</li>
            <li>Ensemble accuracy: {(metrics.chapter4_highlights.ensemble_accuracy * 100).toFixed(1)}%</li>
            <li>Advance warning: {metrics.chapter4_highlights.advance_warning_hours}</li>
            <li>Top features: {metrics.chapter4_highlights.feature_importance_top?.join(', ')}</li>
          </ul>
        ) : (
          <p style={{ color: 'var(--muted)' }}>Start the backend to load live metrics from /api/predictions/metrics</p>
        )}

        <h3 style={{ marginBottom: '0.75rem' }}>Data Sources</h3>
        {nimet ? (
          <ul style={{ color: 'var(--muted)', paddingLeft: '1.25rem', marginBottom: '1rem' }}>
            <li>Demo feed: {nimet.current_demo_source}</li>
            <li>NiMet base: {nimet.nimet_base_url}</li>
            <li>Thesis alignment: {nimet.thesis_alignment}</li>
          </ul>
        ) : (
          <p style={{ color: 'var(--muted)' }}>Open-Meteo live feeds + NiMet integration path documented in API.</p>
        )}

        <h3 style={{ marginBottom: '0.75rem' }}>How to run</h3>
        <pre style={{ background: 'var(--bg)', padding: '1rem', borderRadius: 8, fontSize: '0.85rem', overflow: 'auto' }}>
{`# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
# Docs: http://localhost:8000/docs

# Frontend
cd frontend
npm install && npm run dev
# App: http://localhost:5173`}
        </pre>
      </div>
    </>
  )
}
