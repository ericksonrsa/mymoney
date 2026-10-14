import { FormEvent, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'
import './styles.css'

export function AuthPage() {
  const { user, loading, signIn, signUp } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  if (loading) return <div className="screen"><div className="loader">Carregando...</div></div>
  if (user) return <Navigate to="/dashboard" replace />

  async function submit(event: FormEvent) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      if (mode === 'login') await signIn(username, password)
      else await signUp({ username, email, password, password_confirm: confirm })
      navigate('/dashboard')
    } catch (err: any) {
      const data = err?.response?.data
      setError(data ? Object.values(data).flat().join(' ') : 'Não foi possível concluir a operação.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="auth-shell">
      <section className="brand-panel">
        <div className="brand-mark">M</div>
        <p className="eyebrow">MYMONEY</p>
        <h1>Seu dinheiro.<br />Sob seu controle.</h1>
        <p className="brand-copy">Uma visão simples, segura e inteligente das suas finanças.</p>
      </section>
      <section className="auth-panel">
        <div className="auth-card">
          <div className="mobile-brand">MYMONEY</div>
          <h2>{mode === 'login' ? 'Bem-vindo de volta' : 'Criar sua conta'}</h2>
          <p className="muted">{mode === 'login' ? 'Entre para acessar seu painel financeiro.' : 'Comece a organizar suas finanças.'}</p>
          <form onSubmit={submit}>
            <label>Usuário<input value={username} onChange={e => setUsername(e.target.value)} autoComplete="username" required /></label>
            {mode === 'register' && <label>E-mail<input type="email" value={email} onChange={e => setEmail(e.target.value)} autoComplete="email" required /></label>}
            <label>Senha<input type="password" value={password} onChange={e => setPassword(e.target.value)} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} required minLength={8} /></label>
            {mode === 'register' && <label>Confirme a senha<input type="password" value={confirm} onChange={e => setConfirm(e.target.value)} autoComplete="new-password" required minLength={8} /></label>}
            {error && <div className="error">{error}</div>}
            <button disabled={busy}>{busy ? 'Aguarde...' : mode === 'login' ? 'Entrar' : 'Criar conta'}</button>
          </form>
          <button className="link-button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}>
            {mode === 'login' ? 'Ainda não tenho uma conta' : 'Já tenho uma conta'}
          </button>
        </div>
      </section>
    </main>
  )
}

export function Dashboard() {
  const { user, signOut } = useAuth()
  return <main className="dashboard"><header><div><span className="eyebrow">MYMONEY</span><h1>Olá, {user?.first_name || user?.username} 👋</h1></div><button className="secondary" onClick={signOut}>Sair</button></header><section className="welcome"><p className="eyebrow">PAINEL FINANCEIRO</p><h2>Seu espaço financeiro está pronto.</h2><p>A autenticação foi concluída com sucesso. Os módulos de contas, categorias, transações e dashboard entram nas próximas sprints.</p></section></main>
}
