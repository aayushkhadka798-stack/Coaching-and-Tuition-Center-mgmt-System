import api from './axiosInstance'

export const listTeachers = (params) => api.get('/auth/teachers/', { params })
export const createTeacher = (payload) => api.post('/auth/teachers/', payload)
export const updateTeacher = (id, payload) => api.patch(`/auth/teachers/${id}/`, payload)
export const deleteTeacher = (id) => api.delete(`/auth/teachers/${id}/`)
export const resetTeacherPassword = (id, payload = {}) => api.post(`/auth/teachers/${id}/reset-password/`, payload)
