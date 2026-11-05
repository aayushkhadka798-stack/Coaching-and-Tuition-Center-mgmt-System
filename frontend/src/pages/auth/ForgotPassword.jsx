import { useState } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'
import { Button, Card, Input } from '../../components/ui'
import { InputOTP } from '../../components/ui/InputOTP'
import { requestForgotPassword, resetForgotPassword } from '../../api/passwordApi'
import { saveAuth } from '../../utils/storage'
import { dashboardFor } from '../../utils/constants'
import AuthLayout from '../../components/auth/AuthLayout'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [otp, setOtp] = useState('')
  const [password, setPassword] = useState('')
  const [password2, setPassword2] = useState('')
  const [sent, setSent] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const request = (event) => {
    event.preventDefault(); setBusy(true); setError('')
    requestForgotPassword(email).then(() => { setSent(true); toast.success('If the account exists, an OTP was sent to the email.') }).catch((e) => setError(e.response?.data?.detail || 'Unable to send OTP.')).finally(() => setBusy(false))
  }
  const reset = (event) => {
    event.preventDefault(); setBusy(true); setError('')
    resetForgotPassword({ email, otp, new_password: password, new_password2: password2 }).then(({ data }) => { saveAuth(data); window.location.href = dashboardFor(data.user.role) }).catch((e) => setError(e.response?.data?.detail || 'Unable to reset password.')).finally(() => setBusy(false))
  }
  return <AuthLayout><Card><p className="eyebrow">ACCOUNT RECOVERY</p><h1>Forgot password?</h1><p className="auth-subtitle">We will send a six-digit verification code to your email.</p>{!sent ? <form onSubmit={request}><label><span>Email</span><Input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label>{error && <p className="error">{error}</p>}<Button disabled={busy}>{busy ? 'Sending...' : 'Send OTP'}</Button></form> : <form onSubmit={reset}><p className="muted">Enter the code sent to {email}.</p><InputOTP value={otp} onChange={setOtp} /><label><span>New password</span><Input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} /></label><label><span>Confirm new password</span><Input type="password" required value={password2} onChange={(e) => setPassword2(e.target.value)} /></label>{error && <p className="error">{error}</p>}<Button disabled={busy || otp.length !== 6}>{busy ? 'Resetting...' : 'Reset password'}</Button></form>}<p><Link to="/login">Back to login</Link></p></Card></AuthLayout>
}
