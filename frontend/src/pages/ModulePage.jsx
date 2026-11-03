import { Link } from 'react-router-dom'
import { Badge, Button, Card } from '../components/ui'
import { useAuth } from '../context/AuthContext'

export default function ModulePage({ role, title, description }) {
  const { logout } = useAuth()
  return <main className="dashboard"><header><div><Badge>{role.toUpperCase()} PORTAL</Badge><h1>{title}</h1><p className="muted">{description}</p></div><Button variant="outline" onClick={logout}>Sign out</Button></header><Card><h2>Coming soon</h2><p>This protected route is connected and ready for the {title.toLowerCase()} module.</p><Link to={`/${role}/dashboard`}>Back to dashboard</Link></Card></main>
}
