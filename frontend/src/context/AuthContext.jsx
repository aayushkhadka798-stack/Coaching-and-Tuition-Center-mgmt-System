import { createContext, useContext, useEffect, useState } from 'react'
import * as authApi from '../api/authApi'
import { clearAuth, getAuth, saveAuth } from '../utils/storage'
import { dashboardFor } from '../utils/constants'

const AuthContext = createContext(null)
export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(getAuth)
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    if (!auth?.access) return setLoading(false)
    authApi.me().then(({ data: user }) => setAuth((current) => ({ ...current, user }))).catch(() => { clearAuth(); setAuth(null) }).finally(() => setLoading(false))
  }, [])
  const completeLogin = ({ data }) => { saveAuth(data); setAuth(data); return dashboardFor(data.user.role) }
  const googleLogin = (payload) => authApi.googleLogin(payload).then((response) => {
    if (response.data.needs_center_code) return response.data
    if (response.data.user?.role === 'admin') throw new Error('Invalid credentials.')
    completeLogin(response)
    return response.data
  })
  const refreshUser = () => authApi.me().then(({ data: user }) => {
    setAuth((current) => {
      const next = { ...current, user }
      saveAuth(next)
      return next
    })
    return user
  })
  const logout = async () => { if (auth?.refresh) await authApi.logout(auth.refresh).catch(() => {}); clearAuth(); setAuth(null) }
  return <AuthContext.Provider value={{ ...auth, loading, login: (p) => authApi.login(p).then(completeLogin), adminLogin: (p) => authApi.adminLogin(p).then(completeLogin), googleLogin, refreshUser, register: (p) => authApi.register(p), logout }}>{children}</AuthContext.Provider>
}
export const useAuth = () => useContext(AuthContext)
