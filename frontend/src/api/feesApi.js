import api from './axiosInstance'
export const listFees = () => api.get('/fees/')
export const listPayments = () => api.get('/fees/payments/')
export const initiateEsewa = (payload) => api.post('/fees/payments/esewa/initiate/', payload)
export const verifyEsewa = (payload) => api.post('/fees/payments/esewa/verify/', payload)
