import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
export default function ProtectedRoute({ allowedRoles }) {
  const { user, loading } = useAuth()
  if (loading) return <p className="loading">Loading...</p>
  if (!user) return <Navigate to={allowedRoles?.includes('admin') ? '/admin/login' : '/login'} replace />
  return allowedRoles.includes(user.role) ? <Outlet /> : <Navigate to="/unauthorized" replace />
}
