import api from './axiosInstance'

export const listStudents = (params) => api.get('/auth/students/', { params })
export const createStudent = (payload) => api.post('/auth/students/', payload)
export const updateStudent = (id, payload) => api.patch(`/auth/students/${id}/`, payload)
export const deleteStudent = (id) => api.delete(`/auth/students/${id}/`)
