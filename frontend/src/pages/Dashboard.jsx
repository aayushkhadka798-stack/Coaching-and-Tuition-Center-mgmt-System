import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { dashboard } from '../api/authApi'
import { useAuth } from '../context/AuthContext'
import { Badge, Button, Card, Icon } from '../components/ui'
import ConfirmDialog from '../components/shared/ConfirmDialog'
import { DashboardSidebar, DashboardTopbar } from '../components/dashboard/DashboardNavigation'

const roleConfig = {
  admin: {
    label: 'Admin workspace',
    links: [['Dashboard', 'dashboard', 'home'], ['Teachers', 'teachers', 'users'], ['Students', 'students', 'users'], ['Courses', 'courses', 'book'], ['Batches', 'batches', 'calendar'], ['Fees', 'fees', 'wallet'], ['Notices', 'notices', 'bell']],
    metrics: [['Total students', 'students', 'users', 'blue'], ['Active teachers', 'teachers', 'book', 'green'], ['Active batches', 'active_batches', 'calendar', 'orange'], ['Attendance rate', 'attendance_rate', 'chart', 'purple']],
  },
  teacher: {
    label: 'Teacher workspace',
    links: [['Dashboard', 'dashboard', 'home'], ['My batches', 'batches', 'calendar'], ['Attendance', 'attendance', 'users'], ['Exams', 'exams', 'book']],
    metrics: [['My students', '86', '+6.4%', 'users', 'blue'], ['Active batches', '4', '+1', 'calendar', 'green'], ['Classes this week', '18', '+12.0%', 'book', 'orange'], ['Average attendance', '94.2%', '+2.8%', 'chart', 'purple']],
  },
  student: {
    label: 'Student workspace',
    links: [['Dashboard', 'dashboard', 'home'], ['Attendance', 'attendance', 'calendar'], ['Fees', 'fees', 'wallet'], ['Results', 'results', 'chart']],
    metrics: [['Attendance', 'attendance_rate', 'Live', 'calendar', 'blue'], ['Current batches', 'active_batches', 'Live', 'book', 'green'], ['Outstanding fees', 'outstanding_fees', 'NPR', 'wallet', 'orange'], ['Latest result', 'latest_result', 'Live', 'chart', 'purple']],
  },
}

function formatMetric(value, key) {
  if (value === null || value === undefined) return 'No data'
  if (key === 'attendance_rate') return `${value}%`
  if (key === 'monthly_revenue') return `NPR ${Number(value).toLocaleString('en-IN')}`
  if (key === 'outstanding_fees') return `NPR ${Number(value).toLocaleString('en-IN')}`
  if (key === 'latest_result') return `${value}%`
  return Number(value).toLocaleString('en-IN')
}

function MetricCard({ metric, data }) {
  const [title, key, icon, tone] = metric
  const value = formatMetric(data?.metrics?.[key], key)
  return <Card className="metric-card"><div className={`metric-icon ${tone}`}><Icon name={icon} /></div><div className="metric-copy"><p>{title}</p><strong>{value}</strong><span className="metric-change">Live data</span></div></Card>
}

function RevenueChart() {
  return <Card className="chart-card"><div className="section-heading"><div><h2>Performance overview</h2><p>Charts will appear when historical activity is available.</p></div></div><div className="empty-summary"><Icon name="chart" /><p>No historical activity data is available yet.</p></div></Card>
}

function ActivityCard({ data }) {
  const rows = data?.activity || []
  return <Card className="activity-card"><div className="section-heading"><div><h2>Recent activity</h2><p>Latest updates from your workspace</p></div></div>{rows.length ? <div className="activity-list">{rows.map((row) => <div className="activity-row" key={`${row.title}-${row.created_at}`}><div className="activity-avatar"><Icon name="users" size={17} /></div><div><strong>{row.title}</strong><p>{row.detail}</p></div><time>{new Date(row.created_at).toLocaleDateString()}</time></div>)}</div> : <p className="muted">No recent activity yet.</p>}</Card>
}

export default function Dashboard({ role }) {
  const { user, logout } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [mobileOpen, setMobileOpen] = useState(false)
  const [confirmLogout, setConfirmLogout] = useState(false)
  const config = roleConfig[role]
  useEffect(() => { dashboard(role).then(({ data: result }) => setData(result)).catch(() => setError('Could not load live dashboard data.')) }, [role])
  return <div className="dashboard-shell">
    <DashboardSidebar role={role} user={user} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} activePath="dashboard" onLogout={() => setConfirmLogout(true)} />
    <main className="dashboard-main"><DashboardTopbar role={role} user={user} label={config.label} onMenu={() => setMobileOpen(true)} onLogout={() => setConfirmLogout(true)} /><div className="dashboard-content"><div className="welcome-row"><div><Badge>{role.toUpperCase()} PORTAL</Badge><h1>Welcome back, {user?.first_name || user?.email?.split('@')[0] || 'there'}</h1><p>Here is what is happening in your {role} workspace today.</p></div><Button variant="outline"><Icon name="calendar" size={16} /> Pick a date</Button></div>{error && <p className="error">{error}</p>}<div className="metric-grid">{config.metrics.map((metric) => <MetricCard key={metric[0]} metric={metric} data={data} />)}</div><div className="dashboard-grid"><RevenueChart /><Card className="summary-card"><div className="section-heading"><div><h2>Workspace summary</h2><p>Based on available records</p></div></div>{data?.data_availability?.attendance ? <div className="donut-wrap"><div className="donut"><strong>{data.metrics.attendance_rate}%</strong><span>attendance</span></div></div> : <div className="empty-summary"><Icon name="chart" /><p>Attendance data will appear here after attendance records are added.</p></div>}</Card></div><div className="bottom-grid"><ActivityCard data={data} /><Card className="connection-card"><div className="section-heading"><div><h2>Live connection</h2><p>Backend status</p></div><span className="status-dot">● Online</span></div><div className="connection-message"><div className="connection-icon"><Icon name="chart" /></div><strong>{data?.message || 'Dashboard connected'}</strong><p>Center: {data?.center || 'Loading...'}</p></div></Card></div></div></main><ConfirmDialog open={confirmLogout} title="Sign out?" description="Are you sure you want to sign out?" confirmLabel="Sign out" variant="info" onCancel={() => setConfirmLogout(false)} onConfirm={logout} />
  </div>
}
