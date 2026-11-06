import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { dashboardFor, BRAND_NAME } from '../../utils/constants'
import { ChevronDown, Monitor, Moon, Sun, UserRound } from 'lucide-react'

const links = [['Features', 'features'], ['How it works', 'how-it-works'], ['Roles', 'roles'], ['FAQ', 'faq']]

export default function Navbar() {
  const { user } = useAuth()
  const [open, setOpen] = useState(false)
  const [theme, setTheme] = useState(() => window.localStorage.getItem('tuition-hub-theme') || 'system')
  const [themeOpen, setThemeOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const name = user?.first_name || user?.email?.split('@')[0]

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)')
    const applyTheme = () => {
      const resolved = theme === 'system' ? (media.matches ? 'dark' : 'light') : theme
      document.querySelector('.landing-page')?.setAttribute('data-theme', resolved)
    }
    applyTheme()
    media.addEventListener?.('change', applyTheme)
    return () => media.removeEventListener?.('change', applyTheme)
  }, [theme])

  const changeTheme = (nextTheme) => {
    setTheme(nextTheme)
    window.localStorage.setItem('tuition-hub-theme', nextTheme)
    setThemeOpen(false)
  }

  const ThemeIcon = theme === 'light' ? Sun : theme === 'dark' ? Moon : Monitor
  return <header className={`landing-nav ${scrolled ? 'is-scrolled' : ''}`}><div className="landing-container nav-inner"><Link className="landing-brand" to="/"><img src="/tuition-hub-logo.png" alt="Tuition Hub" /></Link><button className="nav-toggle" aria-label="Toggle navigation" aria-expanded={open} onClick={() => setOpen(!open)}><span /><span /><span /></button><nav className={open ? 'nav-links is-open' : 'nav-links'}>{links.map(([label, id]) => <a key={id} href={`#${id}`} onClick={() => setOpen(false)}>{label}</a>)}<div className="nav-actions"><div className="theme-menu"><button className="theme-trigger" onClick={() => setThemeOpen(!themeOpen)} aria-label="Choose color theme" aria-expanded={themeOpen} aria-haspopup="menu"><ThemeIcon size={15} /><ChevronDown size={13} /></button>{themeOpen && <div className="theme-dropdown" role="menu"><button className={theme === 'light' ? 'active' : ''} onClick={() => changeTheme('light')} role="menuitem"><Sun size={15} />Light</button><button className={theme === 'system' ? 'active' : ''} onClick={() => changeTheme('system')} role="menuitem"><Monitor size={15} />System</button><button className={theme === 'dark' ? 'active' : ''} onClick={() => changeTheme('dark')} role="menuitem"><Moon size={15} />Dark</button></div>}</div>{user ? <><span className="landing-user"><UserRound size={15} />Hi, {name}</span><Link className="landing-button landing-button-ghost" to={`/${user.role}/profile`}>Profile</Link><Link className="landing-button landing-button-primary" to={dashboardFor(user.role)}>Dashboard</Link></> : <><Link className="landing-button landing-button-ghost" to="/login">Log in</Link><Link className="landing-button landing-button-primary" to="/register">Register as a student</Link></>}</div></nav></div></header>
}
