import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { dashboardFor } from '../utils/constants'
export default function PublicOnlyRoute() {
  const { user, loading } = useAuth()
  if (loading) return <p className="loading">Loading...</p>
  return user ? <Navigate to={dashboardFor(user.role)} replace /> : <Outlet />
}
