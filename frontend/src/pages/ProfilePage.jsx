import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { Camera, LockKeyhole, Save, UserRound } from 'lucide-react'
import { getProfile, updateProfile } from '../api/profileApi'
import { useAuth } from '../context/AuthContext'
import { Button, Card, Input } from '../components/ui'
import ConfirmDialog from '../components/shared/ConfirmDialog'
import { DashboardSidebar, DashboardTopbar, roleNavigation } from '../components/dashboard/DashboardNavigation'
import { requestPasswordChange, confirmPasswordChange } from '../api/passwordApi'
import { InputOTP } from '../components/ui/InputOTP'

const apiOrigin = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api').replace(/\/api\/?$/, '')

export default function ProfilePage() {
  const { refreshUser, logout } = useAuth()
  const [profile, setProfile] = useState(null)
  const [photo, setPhoto] = useState(null)
  const [passwords, setPasswords] = useState({ current_password: '', new_password: '', new_password2: '' })
  const [saving, setSaving] = useState(false)
  const [changing, setChanging] = useState(false)
  const [passwordOtp, setPasswordOtp] = useState('')
  const [passwordOtpSent, setPasswordOtpSent] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [confirmLogout, setConfirmLogout] = useState(false)

  useEffect(() => {
    getProfile().then(({ data }) => setProfile(data)).catch(() => toast.error('Unable to load your profile.'))
  }, [])

  if (!profile) return <main className="dashboard"><Card><p className="muted">Loading profile...</p></Card></main>

  const photoUrl = profile.profile_photo ? (profile.profile_photo.startsWith('http') ? profile.profile_photo : `${apiOrigin}${profile.profile_photo}`) : null
  const setField = (name, value) => setProfile((current) => ({ ...current, [name]: value }))
  const save = (event) => {
    event.preventDefault()
    const form = new FormData()
    ;['first_name', 'last_name', 'phone', 'qualification', 'specialization', 'joined_date', 'guardian_name', 'guardian_phone', 'address', 'date_of_birth'].forEach((key) => {
      if (profile[key] !== undefined && profile[key] !== null) form.append(key, profile[key])
    })
    if (photo) form.append('profile_photo', photo)
    setSaving(true)
    updateProfile(form).then(({ data }) => { setProfile(data); setPhoto(null); refreshUser?.(); toast.success('Profile updated.') }).catch((error) => toast.error(error.response?.data?.detail || error.response?.data?.profile_photo?.[0] || 'Unable to update profile.')).finally(() => setSaving(false))
  }
  const requestPasswordOtp = (event) => {
    event.preventDefault()
    setChanging(true)
    requestPasswordChange(passwords.current_password).then(() => { setPasswordOtpSent(true); toast.success('Verification code sent to your email.') }).catch((error) => toast.error(error.response?.data?.detail || 'Unable to send verification code.')).finally(() => setChanging(false))
  }
  const updatePassword = (event) => {
    event.preventDefault()
    setChanging(true)
    confirmPasswordChange({ otp: passwordOtp, new_password: passwords.new_password, new_password2: passwords.new_password2 }).then(() => { setPasswords({ current_password: '', new_password: '', new_password2: '' }); setPasswordOtp(''); setPasswordOtpSent(false); toast.success('Password changed successfully.') }).catch((error) => toast.error(error.response?.data?.detail || 'Unable to change password.')).finally(() => setChanging(false))
  }
  const role = profile.role
  const config = roleNavigation[role]
  return <div className="dashboard-shell">
    <DashboardSidebar role={role} user={profile} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} activePath="profile" onLogout={() => setConfirmLogout(true)} />
    <main className="dashboard-main"><DashboardTopbar role={role} user={profile} label={`${config.label} · Profile`} onMenu={() => setMobileOpen(true)} onLogout={() => setConfirmLogout(true)} /><div className="dashboard-content profile-page">
    <header className="profile-header"><div><p className="eyebrow">{profile.role.toUpperCase()} PORTAL</p><h1>My profile</h1><p className="muted">Manage your account details and password.</p></div></header>
    <div className="profile-grid">
      <Card><div className="profile-card-title"><UserRound size={20} /><h2>Personal details</h2></div><form onSubmit={save} className="profile-form"><div className="profile-photo-wrap">{photoUrl ? <img src={photoUrl} alt="Profile" className="profile-photo" /> : <div className="profile-photo profile-placeholder">{(profile.first_name || profile.email || 'U')[0].toUpperCase()}</div>}<label className="photo-upload" title="Upload profile photo"><Camera size={16} /><input type="file" accept="image/png,image/jpeg,image/webp" onChange={(event) => setPhoto(event.target.files?.[0] || null)} /></label></div><div className="profile-fields"><label><span>First name</span><Input value={profile.first_name || ''} onChange={(event) => setField('first_name', event.target.value)} /></label><label><span>Last name</span><Input value={profile.last_name || ''} onChange={(event) => setField('last_name', event.target.value)} /></label><label><span>Email</span><Input value={profile.email} disabled /></label><label><span>Phone</span><Input value={profile.phone || ''} onChange={(event) => setField('phone', event.target.value)} /></label>{profile.role === 'teacher' && <><label><span>Qualification</span><Input value={profile.qualification || ''} onChange={(event) => setField('qualification', event.target.value)} /></label><label><span>Specialization</span><Input value={profile.specialization || ''} onChange={(event) => setField('specialization', event.target.value)} /></label><label><span>Joined date</span><Input type="date" value={profile.joined_date || ''} onChange={(event) => setField('joined_date', event.target.value)} /></label></>}{profile.role === 'student' && <><label><span>Date of birth</span><Input type="date" value={profile.date_of_birth || ''} onChange={(event) => setField('date_of_birth', event.target.value)} /></label><label><span>Guardian name</span><Input value={profile.guardian_name || ''} onChange={(event) => setField('guardian_name', event.target.value)} /></label><label><span>Guardian phone</span><Input value={profile.guardian_phone || ''} onChange={(event) => setField('guardian_phone', event.target.value)} /></label><label className="full-field"><span>Address</span><textarea value={profile.address || ''} onChange={(event) => setField('address', event.target.value)} /></label></>}</div><Button disabled={saving}><Save size={16} />{saving ? 'Saving...' : 'Save profile'}</Button></form></Card>
      <Card><div className="profile-card-title"><LockKeyhole size={20} /><h2>Change password</h2></div><form onSubmit={passwordOtpSent ? updatePassword : requestPasswordOtp} className="profile-form">{!passwordOtpSent && <label><span>Current password</span><Input required type="password" value={passwords.current_password} onChange={(event) => setPasswords({ ...passwords, current_password: event.target.value })} /></label>}{passwordOtpSent && <><p className="muted">Enter the six-digit code sent to your email.</p><InputOTP value={passwordOtp} onChange={setPasswordOtp} /></>}<label><span>New password</span><Input required type="password" value={passwords.new_password} onChange={(event) => setPasswords({ ...passwords, new_password: event.target.value })} /></label><label><span>Confirm new password</span><Input required type="password" value={passwords.new_password2} onChange={(event) => setPasswords({ ...passwords, new_password2: event.target.value })} /></label><Button disabled={changing || (passwordOtpSent && passwordOtp.length !== 6)}>{changing ? 'Please wait...' : passwordOtpSent ? 'Confirm password change' : 'Send verification code'}</Button></form></Card>
    </div>
    </div></main><ConfirmDialog open={confirmLogout} title="Sign out?" description="Are you sure you want to sign out?" confirmLabel="Sign out" variant="info" onCancel={() => setConfirmLogout(false)} onConfirm={logout} />
  </div>
}
