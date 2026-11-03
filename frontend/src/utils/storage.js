const KEY = 'coaching_auth'
export const getAuth = () => { try { return JSON.parse(localStorage.getItem(KEY)) } catch { return null } }
export const saveAuth = (value) => { try { localStorage.setItem(KEY, JSON.stringify(value)) } catch { /* storage unavailable */ } }
export const clearAuth = () => { try { localStorage.removeItem(KEY) } catch { /* storage unavailable */ } }
