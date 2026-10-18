import { useEffect, useState } from 'react'
import { getAlerts, getStations, sendAlert, subscribe } from '../api'
import { Bell, Send } from 'lucide-react'

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [stations, setStations] = useState([])
  const [form, setForm] = useState({ station_id: 1, recipient_phone: '', message: '', risk_level: 2 })
  const [subForm, setSubForm] = useState({ station_id: 1, phone: '', min_risk_level: 2 })
  const [msg, setMsg] = useState(null)
  const [loading, setLoading] = useState(false)

  const load = () => {
    getAlerts().then((r) => setAlerts(r.data)).catch(() => {})
    getStations().then((r) => {
      setStations(r.data)
      if (r.data.length) {
        setForm((f) => ({ ...f, station_id: r.data[0].id }))
        setSubForm((f) => ({ ...f, station_id: r.data[0].id }))
      }
    })
  }

  useEffect(() => { load() }, [])

  const handleSend = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMsg(null)
    try {
      await sendAlert(form)
      setMsg({ type: 'ok', text: 'Alert sent (or logged in demo mode).' })
      load()
    } catch (err) {
      setMsg({ type: 'err', text: err.response?.data?.detail || err.message })
    } finally {
      setLoading(false)
    }
  }

  const handleSubscribe = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMsg(null)
    try {
      await subscribe(subForm)
      setMsg({ type: 'ok', text: 'Subscription created. High/Extreme predictions will trigger SMS.' })
    } catch (err) {
      setMsg({ type: 'err', text: err.response?.data?.detail || err.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <h1 className="page-title">Alert Management</h1>
      <p className="page-subtitle">
        Send manual SMS alerts or subscribe phone numbers. Twilio credentials required for live delivery; otherwise messages are logged.
      </p>

      {msg && (
        <div className={`alert-banner ${msg.type === 'ok' ? 'risk-low' : 'risk-high'}`} style={{ marginBottom: '1.25rem' }}>
          {msg.text}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Manual send */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Send size={18} /> Send Manual SMS
          </h3>
          <form onSubmit={handleSend}>
            <div className="form-group">
              <label>Station</label>
              <select value={form.station_id} onChange={(e) => setForm({ ...form, station_id: +e.target.value })}>
                {stations.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Recipient Phone (E.164, e.g. +2348012345678)</label>
              <input required value={form.recipient_phone} onChange={(e) => setForm({ ...form, recipient_phone: e.target.value })} placeholder="+234..." />
            </div>
            <div className="form-group">
              <label>Risk Level (for template)</label>
              <select value={form.risk_level} onChange={(e) => setForm({ ...form, risk_level: +e.target.value })}>
                <option value={0}>Low</option>
                <option value={1}>Moderate</option>
                <option value={2}>High</option>
                <option value={3}>Extreme</option>
              </select>
            </div>
            <div className="form-group">
              <label>Custom message (optional)</label>
              <textarea rows={3} value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} placeholder="Leave blank to use auto template" />
            </div>
            <button className="btn btn-primary" disabled={loading}>{loading ? 'Sending…' : 'Send Alert'}</button>
          </form>
        </div>

        {/* Subscribe */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Bell size={18} /> Subscribe to Alerts
          </h3>
          <form onSubmit={handleSubscribe}>
            <div className="form-group">
              <label>Station</label>
              <select value={subForm.station_id} onChange={(e) => setSubForm({ ...subForm, station_id: +e.target.value })}>
                {stations.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Phone Number</label>
              <input required value={subForm.phone} onChange={(e) => setSubForm({ ...subForm, phone: e.target.value })} placeholder="+234..." />
            </div>
            <div className="form-group">
              <label>Minimum Risk to Trigger</label>
              <select value={subForm.min_risk_level} onChange={(e) => setSubForm({ ...subForm, min_risk_level: +e.target.value })}>
                <option value={1}>Moderate and above</option>
                <option value={2}>High and above</option>
                <option value={3}>Extreme only</option>
              </select>
            </div>
            <button className="btn btn-primary" disabled={loading}>Subscribe</button>
          </form>
        </div>
      </div>

      {/* Alert log */}
      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>Recent Alerts</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Station</th>
                <th>Phone</th>
                <th>Status</th>
                <th>Sent At</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              {alerts.length === 0 && (
                <tr><td colSpan={6} style={{ color: 'var(--muted)' }}>No alerts yet.</td></tr>
              )}
              {alerts.map((a) => (
                <tr key={a.id}>
                  <td>{a.id}</td>
                  <td>{a.station_id}</td>
                  <td>{a.recipient_phone}</td>
                  <td>
                    <span className={`badge ${a.status === 'sent' || a.status === 'demo_sent' ? 'risk-low' : 'risk-high'}`}>
                      {a.status}
                    </span>
                  </td>
                  <td>{a.sent_at ? new Date(a.sent_at).toLocaleString() : '—'}</td>
                  <td style={{ maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{a.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}
