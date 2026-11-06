import api from './axiosInstance'

export const listTeachers = (params) => api.get('/teachers/', { params })
export const createTeacher = (payload) => api.post('/teachers/', payload)
export const updateTeacher = (id, payload) => api.patch(`/teachers/${id}/`, payload)
export const deleteTeacher = (id) => api.delete(`/teachers/${id}/`)
export const resetTeacherPassword = (id, payload = {}) => api.post(`/teachers/${id}/reset-password/`, payload)
