import axios from 'axios'
import { clearAuth, getAuth, saveAuth } from '../utils/storage'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api' })
api.interceptors.request.use((config) => {
  const auth = getAuth()
  if (auth?.access) config.headers.Authorization = `Bearer ${auth.access}`
  return config
})
api.interceptors.response.use((response) => response, async (error) => {
  const original = error.config
  const auth = getAuth()
  if (error.response?.status === 401 && auth?.refresh && !original._retry && !original.url.includes('token/refresh')) {
    original._retry = true
    try {
      const { data } = await axios.post(`${api.defaults.baseURL}/auth/token/refresh/`, { refresh: auth.refresh })
      saveAuth({ ...auth, ...data })
      original.headers.Authorization = `Bearer ${data.access}`
      return api(original)
    } catch {
      clearAuth()
    }
  }
  return Promise.reject(error)
})
export default api
