import api from './axiosInstance'

export const initiateEsewaPayment = (feeId, amount) => api.post(`/fees/${feeId}/esewa/initiate/`, { amount })
export const verifyEsewaPayment = (data) => api.post('/payments/esewa/verify/', { data })
export const failEsewaPayment = (transaction_uuid) => api.post('/payments/esewa/failure/', { transaction_uuid })
export const listOnlinePayments = (params) => api.get('/admin/esewa-transactions/', { params })
