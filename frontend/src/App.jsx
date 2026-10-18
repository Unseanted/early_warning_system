import { Routes, Route, NavLink } from 'react-router-dom'
import { Waves } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Predict from './pages/Predict'
import Alerts from './pages/Alerts'
import About from './pages/About'

function App() {
  return (
    <>
      <nav className="navbar">
        <div className="container navbar-inner">
          <NavLink to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700 }}>
            <Waves size={22} color="#3b82f6" />
            FRPEWS
          </NavLink>
          <div className="nav-links">
            <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : '')}>Dashboard</NavLink>
            <NavLink to="/predict" className={({ isActive }) => (isActive ? 'active' : '')}>Predict</NavLink>
            <NavLink to="/alerts" className={({ isActive }) => (isActive ? 'active' : '')}>Alerts</NavLink>
            <NavLink to="/about" className={({ isActive }) => (isActive ? 'active' : '')}>About</NavLink>
          </div>
        </div>
      </nav>

      <main className="container" style={{ paddingBottom: '3rem' }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/predict" element={<Predict />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>

      <footer className="footer">
        <div className="container">
          FRPEWS – Flood Risk Prediction & Early Warning System · Thesis Prototype · Nigeria
        </div>
      </footer>
    </>
  )
}

export default App
