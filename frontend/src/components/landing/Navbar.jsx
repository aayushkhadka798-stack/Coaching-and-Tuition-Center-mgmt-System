import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { dashboardFor, BRAND_NAME } from '../../utils/constants'

const links = [['Features', 'features'], ['How it works', 'how-it-works'], ['Roles', 'roles'], ['FAQ', 'faq']]

export default function Navbar() {
  const { user } = useAuth()
  const [open, setOpen] = useState(false)
  return <header className="landing-nav"><div className="landing-container nav-inner"><Link className="landing-brand" to="/"><span className="brand-symbol">✦</span>{BRAND_NAME}</Link><button className="nav-toggle" aria-label="Toggle navigation" aria-expanded={open} onClick={() => setOpen(!open)}><span /><span /><span /></button><nav className={open ? 'nav-links is-open' : 'nav-links'}>{links.map(([label, id]) => <a key={id} href={`#${id}`} onClick={() => setOpen(false)}>{label}</a>)}<div className="nav-actions">{user ? <Link className="landing-button landing-button-primary" to={dashboardFor(user.role)}>Go to dashboard</Link> : <><Link className="landing-button landing-button-ghost" to="/login">Log in</Link><Link className="landing-button landing-button-primary" to="/register">Register as a student</Link></>}</div></nav></div></header>
}
