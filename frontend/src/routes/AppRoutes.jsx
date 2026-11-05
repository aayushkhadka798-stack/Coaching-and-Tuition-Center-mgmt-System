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
import TeachersPage from '../pages/admin/teachers/TeachersPage'
import ResourceListPage from '../pages/admin/academics/ResourceListPage'
import StudentsPage from '../pages/admin/students/StudentsPage'
import EnrollmentsPage from '../pages/admin/enrollments/EnrollmentsPage'
import ProfilePage from '../pages/ProfilePage'
import ForgotPassword from '../pages/auth/ForgotPassword'
import FeesPage from '../pages/student/FeesPage'
import PaymentsPage from '../pages/admin/payments/PaymentsPage'
export default function AppRoutes() {
  return <BrowserRouter><Routes>
    <Route path="/" element={<LandingPage />} />
    <Route element={<PublicOnlyRoute />}><Route path="/login" element={<Login />} /><Route path="/register" element={<Register />} /><Route path="/forgot-password" element={<ForgotPassword />} /><Route path="/admin/login" element={<AdminLogin />} /></Route>
    <Route path="/unauthorized" element={<Unauthorized />} />
    <Route element={<ProtectedRoute allowedRoles={['admin', 'teacher', 'student']} />}><Route path="/admin/profile" element={<ProfilePage />} /><Route path="/teacher/profile" element={<ProfilePage />} /><Route path="/student/profile" element={<ProfilePage />} /></Route>
    <Route element={<ProtectedRoute allowedRoles={['admin']} />}><Route path="/admin/dashboard" element={<Dashboard role="admin" />} /></Route>
    <Route element={<ProtectedRoute allowedRoles={['admin']} />}><Route path="/admin/teachers" element={<TeachersPage />} /><Route path="/admin/students" element={<StudentsPage />} /><Route path="/admin/courses" element={<ResourceListPage type="courses" />} /><Route path="/admin/batches" element={<ResourceListPage type="batches" />} /><Route path="/admin/enrollments" element={<EnrollmentsPage />} /><Route path="/admin/fees" element={<ModulePage role="admin" title="Fees" description="Manage fee records." />} /><Route path="/admin/payments" element={<PaymentsPage />} /><Route path="/admin/notices" element={<ModulePage role="admin" title="Notices" description="Publish center notices." />} /></Route>
    <Route element={<ProtectedRoute allowedRoles={['teacher']} />}><Route path="/teacher/dashboard" element={<Dashboard role="teacher" />} /><Route path="/teacher/batches" element={<ModulePage role="teacher" title="Batches" description="View assigned batches." />} /><Route path="/teacher/attendance" element={<ModulePage role="teacher" title="Attendance" description="Attendance tools will appear here." />} /><Route path="/teacher/exams" element={<ModulePage role="teacher" title="Exams" description="Exam tools will appear here." />} /></Route>
    <Route element={<ProtectedRoute allowedRoles={['student']} />}><Route path="/student/dashboard" element={<Dashboard role="student" />} /><Route path="/student/attendance" element={<ModulePage role="student" title="Attendance" description="Review your attendance." />} /><Route path="/student/fees" element={<FeesPage />} /><Route path="/student/results" element={<ModulePage role="student" title="Results" description="Review your results." />} /></Route>
    <Route path="*" element={<Navigate to="/login" replace />} />
  </Routes></BrowserRouter>
}
