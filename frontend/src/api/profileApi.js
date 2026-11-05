import api from './axiosInstance'

export const getProfile = () => api.get('/auth/profile/')
export const updateProfile = (payload) => api.patch('/auth/profile/', payload, {
  headers: { 'Content-Type': 'multipart/form-data' },
})
export const changePassword = (payload) => api.post('/auth/change-password/', payload)
