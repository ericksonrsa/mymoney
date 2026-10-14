import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { login, logout, me, register, tokenStore, type User } from './api'

type RegisterPayload = { username: string; email: string; password: string; password_confirm: string }
type AuthContextValue = { user: User | null; loading: boolean; signIn: (username: string, password: string) => Promise<void>; signUp: (payload: RegisterPayload) => Promise<void>; signOut: () => void }

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const refresh = sessionStorage.getItem('mymoney_refresh_token')
    if (!refresh) {
      setLoading(false)
      return
    }
    me().then(setUser).catch(() => logout()).finally(() => setLoading(false))
  }, [])

  async function signIn(username: string, password: string) {
    await login(username, password)
    setUser(await me())
  }

  async function signUp(payload: RegisterPayload) {
    await register(payload)
    await signIn(payload.username, payload.password)
  }

  function signOut() {
    logout()
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider')
  return context
}

export { tokenStore }
