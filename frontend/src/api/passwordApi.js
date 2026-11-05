import api from './axiosInstance'
export const requestForgotPassword = (email) => api.post('/auth/password/forgot/request/', { email })
export const resetForgotPassword = (payload) => api.post('/auth/password/forgot/reset/', payload)
export const requestPasswordChange = (current_password) => api.post('/auth/password/change/request/', { current_password })
export const confirmPasswordChange = (payload) => api.post('/auth/password/change/confirm/', payload)
