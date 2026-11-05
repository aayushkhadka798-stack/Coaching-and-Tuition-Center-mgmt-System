import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { dashboardFor, BRAND_NAME } from '../../utils/constants'
import { UserRound } from 'lucide-react'

const links = [['Features', 'features'], ['How it works', 'how-it-works'], ['Roles', 'roles'], ['FAQ', 'faq']]

export default function Navbar() {
  const { user } = useAuth()
  const [open, setOpen] = useState(false)
  const name = user?.first_name || user?.email?.split('@')[0]
  return <header className="landing-nav"><div className="landing-container nav-inner"><Link className="landing-brand" to="/"><img src="/tuition-hub-logo.png" alt="Tuition Hub" /></Link><button className="nav-toggle" aria-label="Toggle navigation" aria-expanded={open} onClick={() => setOpen(!open)}><span /><span /><span /></button><nav className={open ? 'nav-links is-open' : 'nav-links'}>{links.map(([label, id]) => <a key={id} href={`#${id}`} onClick={() => setOpen(false)}>{label}</a>)}<div className="nav-actions">{user ? <><span className="landing-user"><UserRound size={15} />Hi, {name}</span><Link className="landing-button landing-button-ghost" to={`/${user.role}/profile`}>Profile</Link><Link className="landing-button landing-button-primary" to={dashboardFor(user.role)}>Dashboard</Link></> : <><Link className="landing-button landing-button-ghost" to="/login">Log in</Link><Link className="landing-button landing-button-primary" to="/register">Register as a student</Link></>}</div></nav></div></header>
}
