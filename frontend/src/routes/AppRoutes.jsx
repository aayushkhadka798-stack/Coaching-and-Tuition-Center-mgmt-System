import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Login from '../pages/auth/Login'
import Register from '../pages/auth/Register'
import AdminLogin from '../pages/auth/AdminLogin'
import Unauthorized from '../pages/auth/Unauthorized'
import Dashboard from '../pages/Dashboard'
import ModulePage from '../pages/ModulePage'
import ProtectedRoute from './ProtectedRoute'
import PublicOnlyRoute from './PublicOnlyRoute'
import LandingPage from '../pages/landing/LandingPage'
export default function AppRoutes() {
  return <BrowserRouter><Routes>
    <Route path="/" element={<LandingPage />} />
    <Route element={<PublicOnlyRoute />}><Route path="/login" element={<Login />} /><Route path="/register" element={<Register />} /><Route path="/admin/login" element={<AdminLogin />} /></Route>
    <Route path="/unauthorized" element={<Unauthorized />} />
    <Route element={<ProtectedRoute allowedRoles={['admin']} />}><Route path="/admin/dashboard" element={<Dashboard role="admin" />} /></Route>
    <Route element={<ProtectedRoute allowedRoles={['admin']} />}><Route path="/admin/teachers" element={<ModulePage role="admin" title="Teachers" description="Manage teachers in your center." />} /><Route path="/admin/students" element={<ModulePage role="admin" title="Students" description="View students in your center." />} /><Route path="/admin/courses" element={<ModulePage role="admin" title="Courses" description="Manage center courses." />} /><Route path="/admin/batches" element={<ModulePage role="admin" title="Batches" description="Manage learning batches." />} /><Route path="/admin/fees" element={<ModulePage role="admin" title="Fees" description="Manage fee records." />} /><Route path="/admin/notices" element={<ModulePage role="admin" title="Notices" description="Publish center notices." />} /></Route>
    <Route element={<ProtectedRoute allowedRoles={['teacher']} />}><Route path="/teacher/dashboard" element={<Dashboard role="teacher" />} /><Route path="/teacher/batches" element={<ModulePage role="teacher" title="Batches" description="View assigned batches." />} /><Route path="/teacher/attendance" element={<ModulePage role="teacher" title="Attendance" description="Attendance tools will appear here." />} /><Route path="/teacher/exams" element={<ModulePage role="teacher" title="Exams" description="Exam tools will appear here." />} /></Route>
    <Route element={<ProtectedRoute allowedRoles={['student']} />}><Route path="/student/dashboard" element={<Dashboard role="student" />} /><Route path="/student/attendance" element={<ModulePage role="student" title="Attendance" description="Review your attendance." />} /><Route path="/student/fees" element={<ModulePage role="student" title="Fees" description="Review your fees." />} /><Route path="/student/results" element={<ModulePage role="student" title="Results" description="Review your results." />} /></Route>
    <Route path="*" element={<Navigate to="/login" replace />} />
  </Routes></BrowserRouter>
}
