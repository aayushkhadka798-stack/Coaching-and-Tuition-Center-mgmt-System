import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

export default function Hero() {
  const captions = ['Learn. Grow. Succeed.', 'Make every lesson count.', 'Your center, moving forward.']
  const [captionIndex, setCaptionIndex] = useState(0)

  useEffect(() => {
    const timer = window.setInterval(() => {
      setCaptionIndex((current) => (current + 1) % captions.length)
    }, 2800)
    return () => window.clearInterval(timer)
  }, [])

  return <section className="landing-hero"><div className="landing-container hero-grid"><div className="hero-copy reveal"><span className="hero-kicker">Built for growing learning centers</span><h1>Run your coaching center with <span>clarity.</span></h1><p>Manage students, batches, attendance, fees, exams and notices in one place — without paper registers and scattered spreadsheets.</p><div className="hero-actions"><Link className="landing-button landing-button-primary landing-button-large" to="/register">Get started <span aria-hidden="true">→</span></Link><Link className="landing-button landing-button-ghost landing-button-large" to="/login">Log in</Link></div><div className="hero-note"><span>✓</span> Simple enough for every center team</div></div><div className="hero-visual reveal"><div className="mascot-stage"><img className="hero-mascot" src="/mascot-bookworm.png" alt="Cheerful student mascot reading a book" /><span className="mascot-caption" aria-live="polite">{captions[captionIndex]}</span></div></div></div><div className="hero-stripe" /></section>
}
