import { Link } from 'react-router-dom'
export default function Unauthorized() { return <main className="auth-page"><section className="card"><h1>Access denied</h1><p>You do not have permission to view this page.</p><Link to="/login">Return to login</Link></section></main> }
