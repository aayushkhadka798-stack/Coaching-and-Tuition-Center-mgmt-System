import { useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import Navbar from '../../components/landing/Navbar'
import Hero from '../../components/landing/Hero'
import ProblemSection from '../../components/landing/ProblemSection'
import FeaturesSection from '../../components/landing/FeaturesSection'
import HowItWorks from '../../components/landing/HowItWorks'
import RolesSection from '../../components/landing/RolesSection'
import FaqSection from '../../components/landing/FaqSection'
import CtaSection from '../../components/landing/CtaSection'
import Footer from '../../components/landing/Footer'
import '../../styles/landing.css'

export default function LandingPage() {
  const { loading } = useAuth()

  useEffect(() => {
    if (loading) return undefined
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
          observer.unobserve(entry.target)
        }
      })
    }, { threshold: 0.12 })
    document.querySelectorAll('.landing-page .reveal').forEach((element) => observer.observe(element))
    return () => observer.disconnect()
  }, [loading])

  return <div className="landing-page"><Navbar /><main><Hero /><ProblemSection /><FeaturesSection /><HowItWorks /><RolesSection /><FaqSection /><CtaSection /></main><Footer /></div>
}
