import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('frpews_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const getDashboard = () => api.get('/dashboard/summary')
export const getStations = () => api.get('/stations/')
export const predict = (data) => api.post('/predictions/predict', data)
export const getStationPredictions = (id) => api.get(`/predictions/station/${id}`)
export const getMetrics = () => api.get('/predictions/metrics')
export const getAlerts = () => api.get('/alerts/')
export const sendAlert = (data) => api.post('/alerts/send', data)
export const subscribe = (data) => api.post('/alerts/subscribe', data)
export const login = (data) => api.post('/auth/login', data)
export const register = (data) => api.post('/auth/register', data)
export const getLiveFeeds = () => api.get('/feeds/live')
export const getLiveStation = (name) => api.get(`/feeds/live/${name}`)
export const getNimetInfo = () => api.get('/feeds/nimet-info')

export default api
