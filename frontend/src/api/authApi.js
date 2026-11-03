import api from './axiosInstance'
export const register = (payload) => api.post('/auth/register/', payload)
export const login = (payload) => api.post('/auth/login/', payload)
export const adminLogin = (payload) => api.post('/auth/admin/login/', payload)
export const me = () => api.get('/auth/me/')
export const logout = (refresh) => api.post('/auth/logout/', { refresh })
export const dashboard = (role) => api.get(`/${role}/dashboard/`)
