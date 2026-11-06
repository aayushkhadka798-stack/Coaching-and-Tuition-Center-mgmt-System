import { useState } from 'react'
import { DashboardSidebar, DashboardTopbar, roleNavigation } from './DashboardNavigation'
import ConfirmDialog from '../shared/ConfirmDialog'
import { useAuth } from '../../context/AuthContext'

export default function AdminPageShell({ activePath, title, children }) {
  const { user, logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [confirmLogout, setConfirmLogout] = useState(false)

  return <div className="dashboard-shell">
    <DashboardSidebar role="admin" user={user} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} activePath={activePath} onLogout={() => setConfirmLogout(true)} />
    <main className="dashboard-main">
      <DashboardTopbar role="admin" user={user} label={`${roleNavigation.admin.label} · ${title}`} onMenu={() => setMobileOpen(true)} onLogout={() => setConfirmLogout(true)} />
      <div className="dashboard-content">{children}</div>
    </main>
    <ConfirmDialog open={confirmLogout} title="Sign out?" description="Are you sure you want to sign out?" confirmLabel="Sign out" variant="info" onCancel={() => setConfirmLogout(false)} onConfirm={logout} />
  </div>
}
