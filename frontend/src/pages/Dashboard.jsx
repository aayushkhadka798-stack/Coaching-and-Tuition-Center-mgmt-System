import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { dashboard } from '../api/authApi'
import { useAuth } from '../context/AuthContext'
import { Badge, Button, Card, Icon } from '../components/ui'

const roleConfig = {
  admin: {
    label: 'Admin workspace',
    links: [['Dashboard', 'dashboard', 'home'], ['Teachers', 'teachers', 'users'], ['Students', 'students', 'users'], ['Courses', 'courses', 'book'], ['Batches', 'batches', 'calendar'], ['Fees', 'fees', 'wallet'], ['Notices', 'notices', 'bell']],
    metrics: [['Total students', '1,248', '+12.5%', 'users', 'blue'], ['Active teachers', '48', '+8.2%', 'book', 'green'], ['Monthly revenue', '$48,392', '+9.4%', 'wallet', 'orange'], ['Attendance rate', '92.8%', '+3.1%', 'chart', 'purple']],
  },
  teacher: {
    label: 'Teacher workspace',
    links: [['Dashboard', 'dashboard', 'home'], ['My batches', 'batches', 'calendar'], ['Attendance', 'attendance', 'users'], ['Exams', 'exams', 'book']],
    metrics: [['My students', '86', '+6.4%', 'users', 'blue'], ['Active batches', '4', '+1', 'calendar', 'green'], ['Classes this week', '18', '+12.0%', 'book', 'orange'], ['Average attendance', '94.2%', '+2.8%', 'chart', 'purple']],
  },
  student: {
    label: 'Student workspace',
    links: [['Dashboard', 'dashboard', 'home'], ['Attendance', 'attendance', 'calendar'], ['Fees', 'fees', 'wallet'], ['Results', 'results', 'chart']],
    metrics: [['Attendance', '94.2%', '+2.8%', 'calendar', 'blue'], ['Current courses', '5', '+1', 'book', 'green'], ['Pending fees', '$240', 'Due soon', 'wallet', 'orange'], ['Average result', '88.6%', '+4.2%', 'chart', 'purple']],
  },
}

const chartPoints = '0,130 58,166 116,103 174,72 232,124 290,92 348,139 406,84 464,112 522,42 580,94 638,112'

function MetricCard({ metric }) {
  const [title, value, change, icon, tone] = metric
  return <Card className="metric-card"><div className={`metric-icon ${tone}`}><Icon name={icon} /></div><div className="metric-copy"><p>{title}</p><strong>{value}</strong><span className="metric-change">{change}</span></div><Link to="#" className="metric-link">View details <Icon name="arrow" size={14} /></Link></Card>
}

function RevenueChart() {
  return <Card className="chart-card"><div className="section-heading"><div><h2>Performance overview</h2><p>Activity across the last 12 months</p></div><div className="chart-tabs"><button className="active">Month</button><button>Quarter</button><button>Year</button></div></div><div className="line-chart"><div className="chart-y"><span>100%</span><span>75%</span><span>50%</span><span>25%</span><span>0%</span></div><svg viewBox="0 0 660 190" role="img" aria-label="Performance trend"><path className="chart-grid" d="M0 10H660M0 52H660M0 94H660M0 136H660M0 178H660" /><polyline className="chart-line" points={chartPoints} /><polyline className="chart-area" points={`0,178 ${chartPoints} 638,178`} />{chartPoints.split(' ').map((point) => { const [x, y] = point.split(','); return <circle key={point} cx={x} cy={y} r="4" className="chart-dot" /> })}</svg><div className="chart-x"><span>Jan</span><span>Mar</span><span>May</span><span>Jul</span><span>Sep</span><span>Nov</span></div></div></Card>
}

function ActivityCard({ role }) {
  const rows = role === 'student' ? [['Mathematics', 'Assignment submitted', 'Today'], ['Physics', 'Attendance marked', 'Yesterday'], ['English', 'New result published', '2 days ago']] : role === 'teacher' ? [['Batch A-12', 'Attendance completed', 'Today'], ['Batch B-04', 'Exam scheduled', 'Yesterday'], ['Batch A-08', 'New student joined', '2 days ago']] : [['New student registration', 'A student joined Main Center', 'Today'], ['Fee payment received', 'Monthly fee recorded', 'Yesterday'], ['Teacher account created', 'New teacher added', '2 days ago']]
  return <Card className="activity-card"><div className="section-heading"><div><h2>Recent activity</h2><p>Latest updates from your workspace</p></div><Button variant="ghost">View all</Button></div><div className="activity-list">{rows.map(([name, detail, time]) => <div className="activity-row" key={name}><div className="activity-avatar"><Icon name={role === 'admin' ? 'users' : 'book'} size={17} /></div><div><strong>{name}</strong><p>{detail}</p></div><time>{time}</time><Icon name="more" size={18} /></div>)}</div></Card>
}

export default function Dashboard({ role }) {
  const { user, logout } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [mobileOpen, setMobileOpen] = useState(false)
  const config = roleConfig[role]
  useEffect(() => { dashboard(role).then(({ data: result }) => setData(result)).catch(() => setError('Could not load live dashboard data.')) }, [role])
  return <div className="dashboard-shell">
    <aside className={`dashboard-sidebar ${mobileOpen ? 'open' : ''}`}><div className="brand"><span className="brand-mark">✦</span><strong>Coaching<span>Hub</span></strong><button className="sidebar-close" onClick={() => setMobileOpen(false)}>×</button></div><p className="side-label">Workspace</p><nav>{config.links.map(([label, path, icon]) => <Link className={path === 'dashboard' ? 'selected' : ''} key={path} to={`/${role}/${path}`} onClick={() => setMobileOpen(false)}><Icon name={icon} size={17} />{label}</Link>)}</nav><div className="sidebar-footer"><div className="mini-avatar">{(user?.first_name || user?.email || 'U')[0].toUpperCase()}</div><div><strong>{user?.first_name || user?.email?.split('@')[0]}</strong><span>{role}</span></div><button onClick={logout} aria-label="Sign out">↗</button></div></aside>
    <main className="dashboard-main"><header className="dashboard-topbar"><button className="mobile-menu" onClick={() => setMobileOpen(true)}><Icon name="menu" /></button><div className="breadcrumbs"><span>Home</span><b>›</b><strong>{config.label}</strong></div><div className="top-actions"><button aria-label="Search"><Icon name="search" /></button><button aria-label="Notifications"><Icon name="bell" /><i /></button><Button variant="outline" onClick={logout}>Sign out</Button></div></header><div className="dashboard-content"><div className="welcome-row"><div><Badge>{role.toUpperCase()} PORTAL</Badge><h1>Welcome back, {user?.first_name || user?.email?.split('@')[0] || 'there'}</h1><p>Here is what is happening in your {role} workspace today.</p></div><Button variant="outline"><Icon name="calendar" size={16} /> Pick a date</Button></div>{error && <p className="error">{error}</p>}<div className="metric-grid">{config.metrics.map((metric) => <MetricCard key={metric[0]} metric={metric} />)}</div><div className="dashboard-grid"><RevenueChart /><Card className="summary-card"><div className="section-heading"><div><h2>Workspace summary</h2><p>Current progress</p></div></div><div className="donut-wrap"><div className="donut"><strong>{role === 'admin' ? '78%' : role === 'teacher' ? '92%' : '88%'}</strong><span>overall</span></div></div><div className="legend"><span><i className="dot blue" />Completed <b>{role === 'admin' ? '64%' : '72%'}</b></span><span><i className="dot purple" />In progress <b>{role === 'admin' ? '14%' : '20%'}</b></span><span><i className="dot gray" />Remaining <b>{role === 'admin' ? '22%' : '8%'}</b></span></div></Card></div><div className="bottom-grid"><ActivityCard role={role} /><Card className="connection-card"><div className="section-heading"><div><h2>Live connection</h2><p>Backend status</p></div><span className="status-dot">● Online</span></div><div className="connection-message"><div className="connection-icon"><Icon name="chart" /></div><strong>{data?.message || 'Dashboard connected'}</strong><p>Center: {data?.center || 'Loading...'}</p></div></Card></div></div></main>
  </div>
}
