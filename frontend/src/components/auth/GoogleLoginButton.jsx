import { useState } from 'react'
import { GoogleLogin } from '@react-oauth/google'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

function errorMessage(error) {
  return error?.response?.data?.center_code
    || error?.response?.data?.detail
    || 'Invalid credentials.'
}

export default function GoogleLoginButton() {
  const { googleLogin } = useAuth()
  const navigate = useNavigate()
  const [centerCode, setCenterCode] = useState('')
  const [pending, setPending] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (!clientId) return null

  const submit = (credential, code = '') => {
    setLoading(true)
    setError('')
    googleLogin({ credential, center_code: code }).then((data) => {
      if (data.needs_center_code) {
        setPending({ credential, firstName: data.first_name })
      } else {
        navigate(data.user.role === 'teacher' ? '/teacher/dashboard' : '/student/dashboard')
      }
    }).catch((requestError) => setError(errorMessage(requestError))).finally(() => setLoading(false))
  }

  return <div className="google-login">
    <div className="auth-divider"><span>or</span></div>
    <GoogleLogin onSuccess={({ credential }) => submit(credential)} onError={() => setError('Google sign-in was cancelled or failed.')} useOneTap={false} />
    {loading && <p className="field-help">Signing in...</p>}
    {pending && <div className="google-center-step" role="dialog" aria-labelledby="google-center-title">
      <h2 id="google-center-title">Finish creating your account</h2>
      <p>Welcome, {pending.firstName || 'student'}! Enter your center code to finish creating your student account.</p>
      <InputLike value={centerCode} onChange={(event) => setCenterCode(event.target.value)} />
      <div className="google-center-actions">
        <button type="button" className="ui-button ui-button-outline" onClick={() => { setPending(null); setCenterCode(''); setError('') }}>Cancel</button>
        <button type="button" className="ui-button" disabled={loading || !centerCode.trim()} onClick={() => submit(pending.credential, centerCode)}>Continue</button>
      </div>
    </div>}
    {error && <p className="error" role="alert">{error}</p>}
  </div>
}

function InputLike(props) {
  return <input {...props} className="input google-center-input" aria-label="Center code" placeholder="Center code" autoFocus />
}
