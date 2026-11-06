import { Link } from 'react-router-dom'
import { Badge, Button, Card } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import { useState } from 'react'
import ConfirmDialog from '../components/shared/ConfirmDialog'
import AdminPageShell from '../components/dashboard/AdminPageShell'
import PageHeader from '../components/shared/PageHeader'

export default function ModulePage({ role, title, description }) {
  if (role === 'admin') return <AdminModulePage title={title} description={description} />
  const { logout } = useAuth()
  const [confirmLogout, setConfirmLogout] = useState(false)
  return <><main className="dashboard"><header><div><Badge>{role.toUpperCase()} PORTAL</Badge><h1>{title}</h1><p className="muted">{description}</p></div><Button variant="outline" onClick={() => setConfirmLogout(true)}>Sign out</Button></header><Card><h2>Coming soon</h2><p>This protected route is connected and ready for the {title.toLowerCase()} module.</p><Link to={`/${role}/dashboard`}>Back to dashboard</Link></Card></main><ConfirmDialog open={confirmLogout} title="Sign out?" description="Are you sure you want to sign out?" confirmLabel="Sign out" variant="info" onCancel={() => setConfirmLogout(false)} onConfirm={logout} /></>
}

function AdminModulePage({ title, description }) {
  return <AdminPageShell activePath={title.toLowerCase()} title={title}><PageHeader title={title} description={description} /><Card className="module-placeholder"><div className="module-placeholder-icon">✦</div><h2>{title} workspace</h2><p>This section is connected and ready for center-managed records.</p><Link className="ui-button ui-button-outline" to="/admin/dashboard">Back to dashboard</Link></Card></AdminPageShell>
}
