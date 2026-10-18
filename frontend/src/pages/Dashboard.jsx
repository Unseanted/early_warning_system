import { useEffect, useState } from 'react'
import { getDashboard } from '../api'
import { AlertTriangle, TrendingUp, TrendingDown, Minus, MapPin } from 'lucide-react'

const riskClass = (label) => {
  if (!label) return 'risk-low'
  const l = label.toLowerCase()
  if (l === 'extreme') return 'risk-extreme'
  if (l === 'high') return 'risk-high'
  if (l === 'moderate') return 'risk-moderate'
  return 'risk-low'
}

const TrendIcon = ({ trend }) => {
  if (trend === 'increasing') return <TrendingUp size={16} color="#ef4444" />
  if (trend === 'decreasing') return <TrendingDown size={16} color="#22c55e" />
  return <Minus size={16} color="#94a3b8" />
}

export default function Dashboard() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getDashboard()
      .then((res) => setData(res.data))
      .catch((err) => setError(err.message || 'Failed to load dashboard'))
      .finally(() => setLoading(false))
  }, [])

  const highRisk = data.filter(
    (s) => s.latest_prediction && s.latest_prediction.predicted_risk_class >= 2
  )

  return (
    <>
      <h1 className="page-title">Flood Risk Dashboard</h1>
      <p className="page-subtitle">
        Real-time risk monitoring for Makurdi, Lokoja & Onitsha · Powered by Random Forest ensemble
      </p>

      {highRisk.length > 0 && (
        <div className="alert-banner risk-high">
          <AlertTriangle size={20} />
          <span>
            {highRisk.length} location{highRisk.length > 1 ? 's' : ''} currently at High or Extreme risk.
            SMS alerts have been triggered for subscribed numbers.
          </span>
        </div>
      )}

      {loading && (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
          <div className="spinner" />
        </div>
      )}

      {error && (
        <div className="card" style={{ borderColor: 'var(--danger)', color: '#fca5a5' }}>
          Could not reach backend. Make sure FastAPI is running on port 8000.
          <br />
          <code style={{ fontSize: '0.8rem' }}>{error}</code>
        </div>
      )}

      {!loading && !error && (
        <div className="grid-3">
          {data.map((item) => {
            const pred = item.latest_prediction
            return (
              <div key={item.station.id} className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>{item.station.name}</h3>
                    <p style={{ color: 'var(--muted)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: 4 }}>
                      <MapPin size={14} /> {item.station.state} · {item.station.river_name}
                    </p>
                  </div>
                  {pred ? (
                    <span className={`badge ${riskClass(pred.risk_label)}`}>{pred.risk_label}</span>
                  ) : (
                    <span className="badge risk-low">No data</span>
                  )}
                </div>

                {pred && (
                  <div style={{ marginTop: '1rem' }}>
                    <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.9rem' }}>
                      <div>
                        <div style={{ color: 'var(--muted)', fontSize: '0.75rem' }}>Trend</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 2 }}>
                          <TrendIcon trend={item.trend} /> {item.trend}
                        </div>
                      </div>
                      <div>
                        <div style={{ color: 'var(--muted)', fontSize: '0.75rem' }}>Updated</div>
                        <div style={{ marginTop: 2 }}>
                          {new Date(pred.prediction_timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>

                    {pred.probabilities && (
                      <div style={{ marginTop: '1rem' }}>
                        <div style={{ color: 'var(--muted)', fontSize: '0.75rem', marginBottom: 6 }}>
                          Probability distribution
                        </div>
                        <div style={{ display: 'flex', gap: 6, height: 8, borderRadius: 4, overflow: 'hidden' }}>
                          {['Low', 'Moderate', 'High', 'Extreme'].map((lbl) => {
                            const pct = (pred.probabilities[lbl] || 0) * 100
                            const colors = {
                              Low: '#22c55e',
                              Moderate: '#eab308',
                              High: '#f97316',
                              Extreme: '#ef4444',
                            }
                            return (
                              <div
                                key={lbl}
                                title={`${lbl}: ${pct.toFixed(1)}%`}
                                style={{
                                  width: `${Math.max(pct, 2)}%`,
                                  background: colors[lbl],
                                  borderRadius: 2,
                                }}
                              />
                            )
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {!pred && (
                  <p style={{ marginTop: '1rem', color: 'var(--muted)', fontSize: '0.9rem' }}>
                    Run a prediction from the Predict page to populate risk data.
                  </p>
                )}
              </div>
            )
          })}
        </div>
      )}
    </>
  )
}
