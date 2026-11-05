import api from './axiosInstance'

export const listCourses = (params) => api.get('/academics/courses/', { params })
export const createCourse = (payload) => api.post('/academics/courses/', payload)
export const updateCourse = (id, payload) => api.patch(`/academics/courses/${id}/`, payload)
export const deleteCourse = (id) => api.delete(`/academics/courses/${id}/`)
export const listBatches = (params) => api.get('/academics/batches/', { params })
export const createBatch = (payload) => api.post('/academics/batches/', payload)
export const updateBatch = (id, payload) => api.patch(`/academics/batches/${id}/`, payload)
export const deleteBatch = (id) => api.delete(`/academics/batches/${id}/`)
export const listEnrollments = (params) => api.get('/academics/enrollments/', { params })
export const createEnrollment = (payload) => api.post('/academics/enrollments/', payload)
export const updateEnrollment = (id, payload) => api.patch(`/academics/enrollments/${id}/`, payload)
