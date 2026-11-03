import { Link } from 'react-router-dom'
import { BRAND_NAME } from '../../utils/constants'

const currentYear = new Date().getFullYear()

export default function Footer() {
  return <footer className="landing-footer"><div className="landing-container footer-inner"><div><Link className="landing-brand" to="/"><span className="brand-symbol">✦</span>{BRAND_NAME}</Link><p>Coaching & Tuition Center Management System</p><small>Second Year Project</small></div><div className="footer-links"><span>Explore</span><a href="#features">Features</a><a href="#how-it-works">How it works</a><a href="#faq">FAQ</a></div><div className="footer-links"><span>Account</span><Link to="/login">Log in</Link><Link to="/register">Register</Link></div></div><div className="landing-container footer-bottom"><span>© {currentYear} {BRAND_NAME}</span><span>Built for learning centers in Nepal</span></div></footer>
}
