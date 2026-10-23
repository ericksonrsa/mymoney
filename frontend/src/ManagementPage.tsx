import { FormEvent, useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'
import {
  createBudget, createGoal, createRecurring, deleteBudget, deleteGoal, deleteRecurring,
  generateRecurring, listAccounts, listBudgets, listCategories, listGoals, listRecurring,
  updateBudget, updateGoal, updateRecurring,
  type Account, type Budget, type Category, type FinancialGoal, type RecurringTransaction,
} from './api'
import './styles.css'

type Editor = { kind: 'budget' | 'goal' | 'recurring'; item?: Budget | FinancialGoal | RecurringTransaction } | null
const currentMonth = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}` }
const today = () => new Date().toISOString().slice(0, 10)
const monthDate = (month: string) => `${month}-01`
const money = (v: string | number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(v) || 0)
const dateLabel = (v: string | null) => v ? new Date(`${v}T12:00:00`).toLocaleDateString('pt-BR') : 'Sem prazo'

export function ManagementPage() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [tab, setTab] = useState<'budgets' | 'goals' | 'recurring'>('budgets')
  const [month, setMonth] = useState(currentMonth)
  const [budgets, setBudgets] = useState<Budget[]>([])
  const [goals, setGoals] = useState<FinancialGoal[]>([])
  const [recurring, setRecurring] = useState<RecurringTransaction[]>([])
  const [accounts, setAccounts] = useState<Account[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [editor, setEditor] = useState<Editor>(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const [b, g, r, a, c] = await Promise.all([listBudgets(monthDate(month)), listGoals(), listRecurring(), listAccounts(), listCategories()])
      setBudgets(b); setGoals(g); setRecurring(r); setAccounts(a); setCategories(c)
    } catch { setError('Não foi possível carregar a gestão financeira. Verifique se o backend dos Sprints 05 e 06 está atualizado.') }
    finally { setLoading(false) }
  }, [month])
  useEffect(() => { void load() }, [load])

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!editor) return
    const f = new FormData(event.currentTarget)
    setBusy(true); setError(''); setMessage('')
    try {
      if (editor.kind === 'budget') {
        const payload = { category: String(f.get('category')), month: monthDate(String(f.get('month'))), amount: String(f.get('amount')), notes: String(f.get('notes') || '') }
        if (editor.item) await updateBudget(editor.item.id, payload); else await createBudget(payload)
      } else if (editor.kind === 'goal') {
        const payload = { name: String(f.get('name')), target_amount: String(f.get('target_amount')), current_amount: String(f.get('current_amount') || '0'), target_date: String(f.get('target_date') || '') || null, notes: String(f.get('notes') || '') }
        if (editor.item) await updateGoal(editor.item.id, payload); else await createGoal(payload)
      } else {
        const payload = { account: String(f.get('account')), category: String(f.get('category')), transaction_type: String(f.get('transaction_type')) as 'INCOME' | 'EXPENSE', description: String(f.get('description')), amount: String(f.get('amount')), frequency: String(f.get('frequency')) as 'WEEKLY' | 'MONTHLY' | 'YEARLY', next_run: String(f.get('next_run')), end_date: String(f.get('end_date') || '') || null, notes: String(f.get('notes') || '') }
        if (editor.item) await updateRecurring(editor.item.id, payload); else await createRecurring(payload)
      }
      setEditor(null); setMessage('Alterações salvas com sucesso.'); await load()
    } catch (e: any) {
      const data = e?.response?.data
      setError(data ? Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(' ') : String(v)}`).join(' · ') : 'Não foi possível salvar. Confira os campos e tente novamente.')
    } finally { setBusy(false) }
  }

  async function remove(kind: 'budget' | 'goal' | 'recurring', id: string, label: string) {
    if (!window.confirm(`Excluir “${label}”? Esta ação não pode ser desfeita.`)) return
    setError(''); setMessage('')
    try {
      if (kind === 'budget') await deleteBudget(id)
      else if (kind === 'goal') await deleteGoal(id)
      else await deleteRecurring(id)
      setMessage('Registro excluído.'); await load()
    } catch { setError('Não foi possível excluir o registro.') }
  }
  async function toggleRecurring(item: RecurringTransaction) {
    try { await updateRecurring(item.id, { is_active: !item.is_active }); setMessage(item.is_active ? 'Recorrência pausada.' : 'Recorrência ativada.'); await load() }
    catch { setError('Não foi possível alterar o status da recorrência.') }
  }
  async function runRecurring() {
    setBusy(true); setError(''); setMessage('')
    try { const result = await generateRecurring(); setMessage(`${result.created} lançamento(s) gerado(s).`); await load() }
    catch { setError('Não foi possível gerar os lançamentos recorrentes.') }
    finally { setBusy(false) }
  }

  return <main className="dashboard management-page">
    <header><div><span className="eyebrow">MYMONEY · PLANEJAMENTO</span><h1>Planejamento financeiro</h1><p className="muted header-sub">Olá, {user?.first_name || user?.username}. Organize limites, metas e compromissos recorrentes.</p></div><div className="header-actions"><button className="secondary" onClick={() => navigate('/dashboard')}>← Dashboard</button><button className="secondary" onClick={() => navigate('/insights')}>Insights ↗</button><button className="secondary" onClick={signOut}>Sair</button></div></header>
    <section className="toolbar management-toolbar">
      {tab === 'budgets' ? <label>Mês de referência<input type="month" value={month} onChange={e => e.target.value && setMonth(e.target.value)} /></label> : <span className="muted">Acompanhe e atualize seus planos financeiros.</span>}
      <div className="management-actions">
        {tab === 'recurring' && <button className="secondary" disabled={busy} onClick={() => void runRecurring()}>↻ Gerar lançamentos vencidos</button>}
        <button onClick={() => setEditor({ kind: tab === 'budgets' ? 'budget' : tab === 'goals' ? 'goal' : 'recurring' })}>+ {tab === 'budgets' ? 'Novo orçamento' : tab === 'goals' ? 'Nova meta' : 'Nova recorrência'}</button>
      </div>
    </section>
    <nav className="management-tabs" aria-label="Seções de planejamento">
      <button className={tab === 'budgets' ? 'active' : ''} onClick={() => setTab('budgets')}>Orçamentos <span>{budgets.length}</span></button>
      <button className={tab === 'goals' ? 'active' : ''} onClick={() => setTab('goals')}>Metas financeiras <span>{goals.length}</span></button>
      <button className={tab === 'recurring' ? 'active' : ''} onClick={() => setTab('recurring')}>Transações recorrentes <span>{recurring.length}</span></button>
    </nav>
    {error && <div className="error page-error" role="alert">{error}</div>}
    {message && <p className="success-message" role="status">{message}</p>}
    {loading ? <section className="panel"><p className="empty">Carregando seus registros…</p></section> : <>
      {tab === 'budgets' && <section className="management-list">
        {budgets.map(item => <article className="panel management-card" key={item.id}><div className="management-card-head"><div><span className="eyebrow">ORÇAMENTO MENSAL</span><h3>{item.category_name}</h3></div><strong className={item.percentage >= 100 ? 'expense' : item.percentage >= 80 ? 'budget-warning' : ''}>{item.percentage.toLocaleString('pt-BR', { maximumFractionDigits: 0 })}%</strong></div><div className="mini-track budget-large"><span className={item.percentage >= 100 ? 'track-critical' : item.percentage >= 80 ? 'track-warning' : ''} style={{ width: `${Math.max(0, Math.min(100, item.percentage))}%` }} /></div><div className="budget-values"><span>Gasto <strong>{money(item.spent)}</strong></span><span>Limite <strong>{money(item.amount)}</strong></span><span>Restante <strong className={Number(item.remaining) < 0 ? 'expense' : ''}>{money(item.remaining)}</strong></span></div>{item.notes && <p className="muted management-note">{item.notes}</p>}<div className="management-card-actions"><button className="secondary" onClick={() => setEditor({ kind: 'budget', item })}>Editar</button><button className="secondary danger" onClick={() => void remove('budget', item.id, item.category_name)}>Excluir</button></div></article>)}
        {!budgets.length && <EmptyState title="Nenhum orçamento neste mês" detail="Defina limites por categoria para acompanhar seus gastos e receber alertas." />}
      </section>}
      {tab === 'goals' && <section className="management-list">
        {goals.map(item => <article className="panel management-card" key={item.id}><div className="management-card-head"><div><span className="eyebrow">{item.is_active ? 'META ATIVA' : 'META PAUSADA'}</span><h3>{item.name}</h3></div><strong>{item.percentage.toLocaleString('pt-BR', { maximumFractionDigits: 0 })}%</strong></div><div className="mini-track budget-large"><span style={{ width: `${Math.max(0, Math.min(100, item.percentage))}%` }} /></div><div className="budget-values"><span>Acumulado <strong>{money(item.current_amount)}</strong></span><span>Objetivo <strong>{money(item.target_amount)}</strong></span><span>Faltam <strong>{money(item.remaining)}</strong></span></div><p className="muted management-note">Prazo: {dateLabel(item.target_date)}{item.notes ? ` · ${item.notes}` : ''}</p><div className="management-card-actions"><button className="secondary" onClick={() => setEditor({ kind: 'goal', item })}>Editar</button><button className="secondary danger" onClick={() => void remove('goal', item.id, item.name)}>Excluir</button></div></article>)}
        {!goals.length && <EmptyState title="Transforme planos em metas" detail="Cadastre um objetivo, valor desejado e prazo para acompanhar seu progresso." />}
      </section>}
      {tab === 'recurring' && <section className="management-list">
        {recurring.map(item => <article className="panel management-card" key={item.id}><div className="management-card-head"><div><span className="eyebrow">{item.is_active ? 'RECORRÊNCIA ATIVA' : 'RECORRÊNCIA PAUSADA'}</span><h3>{item.description}</h3><p className="muted recurring-sub">{item.account_name} · {item.category_name || 'Sem categoria'}</p></div><strong className={item.transaction_type === 'EXPENSE' ? 'expense' : 'income'}>{item.transaction_type === 'EXPENSE' ? '−' : '+'}{money(item.amount)}</strong></div><div className="recurring-meta"><span><small>Frequência</small><strong>{item.frequency === 'WEEKLY' ? 'Semanal' : item.frequency === 'YEARLY' ? 'Anual' : 'Mensal'}</strong></span><span><small>Próxima execução</small><strong>{dateLabel(item.next_run)}</strong></span><span><small>Fim</small><strong>{dateLabel(item.end_date)}</strong></span></div><div className="management-card-actions"><button className="secondary" onClick={() => setEditor({ kind: 'recurring', item })}>Editar</button><button className="secondary" onClick={() => void toggleRecurring(item)}>{item.is_active ? 'Pausar' : 'Ativar'}</button><button className="secondary danger" onClick={() => void remove('recurring', item.id, item.description)}>Excluir</button></div></article>)}
        {!recurring.length && <EmptyState title="Automatize os lançamentos previsíveis" detail="Cadastre contas fixas, salário ou outras movimentações para organizar os próximos vencimentos." />}
      </section>}
    </>}
    {editor && <div className="overlay"><section className="modal management-modal"><div className="modal-head"><div><span className="eyebrow">MYMONEY · PLANEJAMENTO</span><h2>{editor.item ? 'Editar' : 'Novo'} {editor.kind === 'budget' ? 'orçamento' : editor.kind === 'goal' ? 'meta financeira' : 'lançamento recorrente'}</h2></div><button className="close" type="button" onClick={() => setEditor(null)}>×</button></div>
      <form className="modal-form" onSubmit={submit}>
        {editor.kind === 'budget' && <><label>Categoria de despesa<select name="category" defaultValue={(editor.item as Budget | undefined)?.category || ''} required><option value="">Selecione uma categoria</option>{categories.filter(c => c.category_type === 'EXPENSE' && c.is_active).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></label><label>Mês<input type="month" name="month" defaultValue={(editor.item as Budget | undefined)?.month.slice(0, 7) || month} required /></label><label>Limite (R$)<input name="amount" type="number" min="0.01" step="0.01" defaultValue={(editor.item as Budget | undefined)?.amount || ''} required /></label><label>Observações<input name="notes" defaultValue={(editor.item as Budget | undefined)?.notes || ''} maxLength={200} /></label></>}
        {editor.kind === 'goal' && <><label>Nome da meta<input name="name" defaultValue={(editor.item as FinancialGoal | undefined)?.name || ''} maxLength={120} placeholder="Ex.: Reserva de emergência" required /></label><div className="management-form-row"><label>Valor desejado (R$)<input name="target_amount" type="number" min="0.01" step="0.01" defaultValue={(editor.item as FinancialGoal | undefined)?.target_amount || ''} required /></label><label>Valor acumulado (R$)<input name="current_amount" type="number" min="0" step="0.01" defaultValue={(editor.item as FinancialGoal | undefined)?.current_amount || '0'} required /></label></div><label>Prazo (opcional)<input name="target_date" type="date" min={today()} defaultValue={(editor.item as FinancialGoal | undefined)?.target_date || ''} /></label><label>Observações<input name="notes" maxLength={200} defaultValue={(editor.item as FinancialGoal | undefined)?.notes || ''} /></label></>}
        {editor.kind === 'recurring' && <><label>Descrição<input name="description" maxLength={200} defaultValue={(editor.item as RecurringTransaction | undefined)?.description || ''} required /></label><div className="management-form-row"><label>Tipo<select name="transaction_type" defaultValue={(editor.item as RecurringTransaction | undefined)?.transaction_type || 'EXPENSE'}><option value="EXPENSE">Despesa</option><option value="INCOME">Receita</option></select></label><label>Valor (R$)<input name="amount" type="number" min="0.01" step="0.01" defaultValue={(editor.item as RecurringTransaction | undefined)?.amount || ''} required /></label></div><label>Conta<select name="account" defaultValue={(editor.item as RecurringTransaction | undefined)?.account || ''} required><option value="">Selecione uma conta</option>{accounts.filter(a => a.is_active).map(a => <option key={a.id} value={a.id}>{a.name}</option>)}</select></label><label>Categoria<select name="category" defaultValue={(editor.item as RecurringTransaction | undefined)?.category || ''} required><option value="">Selecione uma categoria</option>{categories.filter(c => c.is_active).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}</select></label><div className="management-form-row"><label>Frequência<select name="frequency" defaultValue={(editor.item as RecurringTransaction | undefined)?.frequency || 'MONTHLY'}><option value="WEEKLY">Semanal</option><option value="MONTHLY">Mensal</option><option value="YEARLY">Anual</option></select></label><label>Próxima execução<input name="next_run" type="date" defaultValue={(editor.item as RecurringTransaction | undefined)?.next_run || today()} required /></label></div><label>Data final (opcional)<input name="end_date" type="date" defaultValue={(editor.item as RecurringTransaction | undefined)?.end_date || ''} /></label><label>Observações<input name="notes" maxLength={200} defaultValue={(editor.item as RecurringTransaction | undefined)?.notes || ''} /></label></>}
        <div className="management-form-actions"><button className="secondary" type="button" onClick={() => setEditor(null)}>Cancelar</button><button disabled={busy}>{busy ? 'Salvando…' : 'Salvar'}</button></div>
      </form>
    </section></div>}
  </main>
}

function EmptyState({ title, detail }: { title: string; detail: string }) {
  return <article className="panel management-empty"><div className="empty-icon">✦</div><h3>{title}</h3><p>{detail}</p></article>
}
