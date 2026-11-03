import { Link } from 'react-router-dom'

export default function CtaSection() {
  return <section className="cta-section"><div className="landing-container cta-inner reveal"><div><span className="section-label">A better next step</span><h2>Ready to bring your center online?</h2><p>Start with a simpler way to manage the work that matters.</p></div><div className="cta-actions"><Link className="landing-button landing-button-light landing-button-large" to="/register">Register as a student →</Link><Link className="landing-button landing-button-outline-light landing-button-large" to="/login">Log in</Link></div></div></section>
}
