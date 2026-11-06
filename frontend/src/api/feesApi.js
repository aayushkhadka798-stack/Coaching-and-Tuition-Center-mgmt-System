import api from './axiosInstance'
export const listFees = () => api.get('/fees/')
export const listStudentPayments = () => api.get('/student/payments/')
export const listPayments = () => api.get('/fees/payments/')
export const initiateEsewa = (payload) => api.post('/fees/payments/esewa/initiate/', payload)
export const verifyEsewa = (payload) => api.post('/fees/payments/esewa/verify/', payload)
export const failEsewa = (payload) => api.post('/fees/payments/esewa/failure/', payload)
export const listEsewaTransactions = (params) => api.get('/fees/admin/esewa-transactions/', { params })
