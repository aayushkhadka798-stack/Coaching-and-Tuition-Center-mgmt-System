import { Link } from 'react-router-dom'
import { Icon, Button } from '../ui'
import { BRAND_NAME } from '../../utils/constants'

export const roleNavigation = {
  admin: {
    label: 'Admin workspace',
    links: [['Dashboard', 'dashboard', 'home'], ['Teachers', 'teachers', 'users'], ['Students', 'students', 'users'], ['Courses', 'courses', 'book'], ['Batches', 'batches', 'calendar'], ['Fees', 'fees', 'wallet'], ['Payments', 'payments', 'wallet'], ['Notices', 'notices', 'bell']],
  },
  teacher: {
    label: 'Teacher workspace',
    links: [['Dashboard', 'dashboard', 'home'], ['My batches', 'batches', 'calendar'], ['Attendance', 'attendance', 'users'], ['Exams', 'exams', 'book']],
  },
  student: {
    label: 'Student workspace',
    links: [['Dashboard', 'dashboard', 'home'], ['Attendance', 'attendance', 'calendar'], ['Fees', 'fees', 'wallet'], ['Results', 'results', 'chart']],
  },
}

const displayName = (user) => user?.first_name || user?.email?.split('@')[0] || 'User'

export function DashboardSidebar({ role, user, mobileOpen, setMobileOpen, activePath, onLogout }) {
  const config = roleNavigation[role]
  return <aside className={`dashboard-sidebar ${mobileOpen ? 'open' : ''}`}>
    <div className="brand"><span className="brand-mark">✦</span><strong>{BRAND_NAME}</strong><button className="sidebar-close" onClick={() => setMobileOpen(false)} aria-label="Close navigation">×</button></div>
    <p className="side-label">Workspace</p>
    <nav>
      {config.links.map(([label, path, icon]) => <Link className={activePath === path ? 'selected' : ''} key={path} to={`/${role}/${path}`} onClick={() => setMobileOpen(false)}><Icon name={icon} size={17} />{label}</Link>)}
      <Link className={activePath === 'profile' ? 'selected' : ''} to={`/${role}/profile`} onClick={() => setMobileOpen(false)}><Icon name="user" size={17} />Profile</Link>
    </nav>
    <div className="sidebar-footer">
      <div className="mini-avatar">{displayName(user)[0].toUpperCase()}</div>
      <Link className="profile-link" to={`/${role}/profile`} onClick={() => setMobileOpen(false)}><strong>{displayName(user)}</strong><span>{role} · Profile</span></Link>
      <button onClick={onLogout} aria-label="Sign out">↗</button>
    </div>
  </aside>
}

export function DashboardTopbar({ role, user, onMenu, onLogout, label }) {
  return <header className="dashboard-topbar">
    <button className="mobile-menu" onClick={onMenu} aria-label="Open navigation"><Icon name="menu" /></button>
    <div className="breadcrumbs"><Link to={`/${role}/dashboard`}>Home</Link><b>›</b><strong>{label}</strong></div>
    <div className="top-actions">
      <Link className="top-user-link" to={`/${role}/profile`}><span className="top-user-avatar">{displayName(user)[0].toUpperCase()}</span><span>{displayName(user)}</span></Link>
      <button aria-label="Search"><Icon name="search" /></button>
      <button aria-label="Notifications"><Icon name="bell" /><i /></button>
      <Button variant="outline" onClick={onLogout}>Sign out</Button>
    </div>
  </header>
}
