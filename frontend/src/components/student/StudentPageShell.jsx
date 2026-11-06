import { useState } from 'react'
import { DashboardSidebar, DashboardTopbar, roleNavigation } from '../dashboard/DashboardNavigation'
import ConfirmDialog from '../shared/ConfirmDialog'
import { useAuth } from '../../context/AuthContext'

export default function StudentPageShell({ activePath, title, children }) {
  const { user, logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [confirmLogout, setConfirmLogout] = useState(false)
  return <div className="dashboard-shell"><DashboardSidebar role="student" user={user} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} activePath={activePath} onLogout={() => setConfirmLogout(true)} /><main className="dashboard-main"><DashboardTopbar role="student" user={user} label={`${roleNavigation.student.label} · ${title}`} onMenu={() => setMobileOpen(true)} onLogout={() => setConfirmLogout(true)} /><div className="dashboard-content">{children}</div></main><ConfirmDialog open={confirmLogout} title="Sign out?" description="Are you sure you want to sign out?" confirmLabel="Sign out" variant="info" onCancel={() => setConfirmLogout(false)} onConfirm={logout} /></div>
}
