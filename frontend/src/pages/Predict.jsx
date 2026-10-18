import { useEffect, useState } from 'react'
import { getStations, predict, getLiveStation, getMetrics } from '../api'
import { Activity, CloudRain, Cpu } from 'lucide-react'

const riskClass = (label) => {
  if (!label) return 'risk-low'
  const l = label.toLowerCase()
  if (l === 'extreme') return 'risk-extreme'
  if (l === 'high') return 'risk-high'
  if (l === 'moderate') return 'risk-moderate'
  return 'risk-low'
}

const presets = {
  safe: { daily_rainfall_mm: 5, river_level_m: 3.2, antecedent_3day_rain_mm: 12, antecedent_7day_rain_mm: 30, river_level_change_m: 0.05 },
  moderate: { daily_rainfall_mm: 28, river_level_m: 5.8, antecedent_3day_rain_mm: 55, antecedent_7day_rain_mm: 90, river_level_change_m: 0.3 },
  high: { daily_rainfall_mm: 48, river_level_m: 7.5, antecedent_3day_rain_mm: 95, antecedent_7day_rain_mm: 160, river_level_change_m: 0.7 },
  extreme: { daily_rainfall_mm: 75, river_level_m: 11.2, antecedent_3day_rain_mm: 140, antecedent_7day_rain_mm: 220, river_level_change_m: 1.1 },
}

function ProbBars({ probs }) {
  if (!probs) return null
  return (
    <div>
      {Object.entries(probs).map(([label, prob]) => (
        <div key={label} style={{ marginBottom: 6 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
            <span>{label}</span>
            <span>{(prob * 100).toFixed(1)}%</span>
          </div>
          <div style={{ height: 5, background: 'var(--bg)', borderRadius: 3, marginTop: 2 }}>
            <div style={{
              height: '100%', width: `${prob * 100}%`, borderRadius: 3,
              background: label === 'Extreme' ? '#ef4444' : label === 'High' ? '#f97316' : label === 'Moderate' ? '#eab308' : '#22c55e',
            }} />
          </div>
        </div>
      ))}
    </div>
  )
}

export default function Predict() {
  const [stations, setStations] = useState([])
  const [form, setForm] = useState({
    station_id: 1,
    daily_rainfall_mm: 20,
    river_level_m: 5.0,
    antecedent_3day_rain_mm: 40,
    antecedent_7day_rain_mm: 70,
    river_level_change_m: 0.2,
    month: new Date().getMonth() + 1,
  })
  const [result, setResult] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(false)
  const [liveLoading, setLiveLoading] = useState(false)
  const [error, setError] = useState(null)
  const [feedNote, setFeedNote] = useState(null)

  useEffect(() => {
    getStations().then((res) => {
      setStations(res.data)
      if (res.data.length) setForm((f) => ({ ...f, station_id: res.data[0].id }))
    })
    getMetrics().then((r) => setMetrics(r.data)).catch(() => {})
  }, [])

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((f) => ({
      ...f,
      [name]: name === 'station_id' || name === 'month' ? parseInt(value) : parseFloat(value),
    }))
  }

  const applyPreset = (key) => setForm((f) => ({ ...f, ...presets[key] }))

  const loadLive = async () => {
    const st = stations.find((s) => s.id === form.station_id)
    if (!st) return
    setLiveLoading(true)
    setFeedNote(null)
    try {
      const res = await getLiveStation(st.name)
      const d = res.data
      setForm((f) => ({
        ...f,
        daily_rainfall_mm: d.daily_rainfall_mm ?? f.daily_rainfall_mm,
        river_level_m: d.river_level_m ?? f.river_level_m,
        antecedent_3day_rain_mm: d.antecedent_3day_rain_mm ?? f.antecedent_3day_rain_mm,
        antecedent_7day_rain_mm: d.antecedent_7day_rain_mm ?? f.antecedent_7day_rain_mm,
        river_level_change_m: d.river_level_change_m ?? f.river_level_change_m,
        month: d.month ?? f.month,
      }))
      setFeedNote(`Live feed loaded from ${d.source || 'Open-Meteo'} for ${d.station} (${d.fetched_at})`)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLiveLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await predict(form)
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <h1 className="page-title">Flood Risk Prediction</h1>
      <p className="page-subtitle">
        Ensemble model (Random Forest 50% + LSTM 50%). Load live Open-Meteo features or use presets.
      </p>

      {metrics?.chapter4_highlights && (
        <div className="card" style={{ marginBottom: '1.25rem', display: 'flex', gap: '1.5rem', flexWrap: 'wrap', fontSize: '0.9rem' }}>
          <div><strong>Chapter 4 metrics</strong></div>
          <div>RF: <strong>{(metrics.chapter4_highlights.rf_accuracy * 100).toFixed(1)}%</strong></div>
          <div>LSTM: <strong>{(metrics.chapter4_highlights.lstm_accuracy * 100).toFixed(1)}%</strong></div>
          <div>Ensemble: <strong>{(metrics.chapter4_highlights.ensemble_accuracy * 100).toFixed(1)}%</strong></div>
          <div style={{ color: 'var(--muted)' }}>Lead time: {metrics.chapter4_highlights.advance_warning_hours}</div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div className="card">
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Activity size={18} /> Input Features
          </h3>

          <div style={{ display: 'flex', gap: 8, marginBottom: '1rem', flexWrap: 'wrap' }}>
            {Object.keys(presets).map((k) => (
              <button key={k} type="button" className="btn btn-outline" style={{ fontSize: '0.8rem', padding: '0.35rem 0.7rem' }}
                onClick={() => applyPreset(k)}>{k}</button>
            ))}
            <button type="button" className="btn btn-primary" style={{ fontSize: '0.8rem', padding: '0.35rem 0.7rem' }}
              onClick={loadLive} disabled={liveLoading}>
              <CloudRain size={14} /> {liveLoading ? 'Loading…' : 'Load live feed'}
            </button>
          </div>
          {feedNote && <p style={{ fontSize: '0.8rem', color: 'var(--muted)', marginBottom: '0.75rem' }}>{feedNote}</p>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Monitoring Station</label>
              <select name="station_id" value={form.station_id} onChange={handleChange}>
                {stations.map((s) => (
                  <option key={s.id} value={s.id}>{s.name} ({s.state})</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Daily Rainfall (mm)</label>
              <input type="number" step="0.1" name="daily_rainfall_mm" value={form.daily_rainfall_mm} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>River Water Level (m)</label>
              <input type="number" step="0.01" name="river_level_m" value={form.river_level_m} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>3-Day Antecedent Rainfall (mm)</label>
              <input type="number" step="0.1" name="antecedent_3day_rain_mm" value={form.antecedent_3day_rain_mm} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>7-Day Antecedent Rainfall (mm)</label>
              <input type="number" step="0.1" name="antecedent_7day_rain_mm" value={form.antecedent_7day_rain_mm} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>River Level Change (m)</label>
              <input type="number" step="0.01" name="river_level_change_m" value={form.river_level_change_m} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Month (1-12)</label>
              <input type="number" min="1" max="12" name="month" value={form.month} onChange={handleChange} />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
              {loading ? 'Predicting…' : 'Run Ensemble Prediction'}
            </button>
          </form>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Cpu size={18} /> Ensemble Result
          </h3>
          {!result && !error && !loading && (
            <p style={{ color: 'var(--muted)' }}>Submit features to see RF, LSTM and ensemble outputs.</p>
          )}
          {loading && <div className="spinner" />}
          {error && <div style={{ color: '#fca5a5' }}>{error}</div>}

          {result && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: '1rem' }}>
                <span className={`badge ${riskClass(result.risk_label)}`} style={{ fontSize: '1rem', padding: '0.4rem 1rem' }}>
                  {result.risk_label} Risk
                </span>
                {result.alert_triggered && (
                  <span style={{ color: '#f97316', fontWeight: 600, fontSize: '0.9rem' }}>SMS Alert Triggered</span>
                )}
              </div>
              <p style={{ marginBottom: '1rem', lineHeight: 1.6 }}>{result.recommended_action}</p>

              <div style={{ marginBottom: '1rem' }}>
                <div style={{ color: 'var(--muted)', fontSize: '0.75rem', marginBottom: 4 }}>Ensemble probabilities</div>
                <ProbBars probs={result.probabilities} />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '1rem' }}>
                <div style={{ background: 'var(--bg)', padding: '0.75rem', borderRadius: 8 }}>
                  <div style={{ fontWeight: 600, marginBottom: 4 }}>Random Forest</div>
                  <span className={`badge ${riskClass(result.rf?.label)}`}>{result.rf?.label || '—'}</span>
                  <div style={{ marginTop: 8 }}><ProbBars probs={result.rf?.probabilities} /></div>
                </div>
                <div style={{ background: 'var(--bg)', padding: '0.75rem', borderRadius: 8 }}>
                  <div style={{ fontWeight: 600, marginBottom: 4 }}>
                    LSTM {result.lstm?.available === false && <span style={{ color: 'var(--muted)', fontWeight: 400 }}>(fallback)</span>}
                  </div>
                  <span className={`badge ${riskClass(result.lstm?.label)}`}>{result.lstm?.label || '—'}</span>
                  <div style={{ marginTop: 8 }}><ProbBars probs={result.lstm?.probabilities} /></div>
                </div>
              </div>
              {result.model_version && (
                <p style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--muted)' }}>{result.model_version}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  )
}
