import api from './axiosInstance'

export const listStudents = (params) => api.get('/auth/students/', { params })
export const createStudent = (payload) => api.post('/auth/students/', payload)
export const updateStudent = (id, payload) => api.patch(`/auth/students/${id}/`, payload)
export const deleteStudent = (id) => api.delete(`/auth/students/${id}/`)
export const listStudentEnrollments = () => api.get('/student/enrollments/')
export const listStudentTimetable = () => api.get('/student/timetable/')
export const listStudentAttendance = (params) => api.get('/student/attendance/', { params })
export const getStudentAttendanceSummary = () => api.get('/student/attendance/summary/')
export const listStudentResults = (params) => api.get('/student/results/', { params })
export const listStudentNotices = () => api.get('/student/notices/')
export const markStudentNoticeRead = (id) => api.post(`/student/notices/${id}/read/`)
