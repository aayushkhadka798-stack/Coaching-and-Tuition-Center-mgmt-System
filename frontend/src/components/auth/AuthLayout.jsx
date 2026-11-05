import { Link } from 'react-router-dom'
import { BRAND_NAME } from '../../utils/constants'

export default function AuthLayout({ children }) {
  return <main className="auth-page"><section className="auth-mascot-panel"><Link className="auth-brand" to="/"><img src="/tuition-hub-logo.png" alt="Tuition Hub" /></Link><div className="auth-mascot-copy"><span>Learn with confidence</span><h2>Your learning journey starts here.</h2><p>One simple place for students, teachers, and centers to stay connected.</p></div><img className="auth-mascot" src="/mascot-auth.png" alt="Student using a laptop" /></section><section className="auth-form-panel">{children}<small className="auth-project-note">{BRAND_NAME} · Coaching center management</small></section></main>
}
