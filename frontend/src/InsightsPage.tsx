import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getFinancialInsights, type FinancialInsights } from './api'
import { useAuth } from './AuthContext'
import './styles.css'

function money(value: string | number) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(value) || 0)
}
function monthStart() {
  const d = new Date()
  return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().slice(0, 10)
}
function monthTitle(value: string) {
  return new Intl.DateTimeFormat('pt-BR', { month: 'long', year: 'numeric' }).format(new Date(`${value.slice(0, 7)}-02T12:00:00`))
}
function percent(value: number | null) {
  if (value === null) return 'Sem base anterior'
  return `${value > 0 ? '+' : ''}${value.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%`
}
function changeTone(value: number | null, expenses = false) {
  if (value === null || value === 0) return ''
  return (expenses ? value < 0 : value > 0) ? 'income' : 'expense'
}

export function InsightsPage() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [month, setMonth] = useState(monthStart)
  const [data, setData] = useState<FinancialInsights | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    setLoading(true)
    setError('')
    getFinancialInsights(month)
      .then(result => { if (active) setData(result) })
      .catch(() => { if (active) setError('Não foi possível carregar os insights. Confirme se o backend está atualizado com o Sprint 08.') })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [month])

  const summary = data?.summary
  return <main className="dashboard insights-page">
    <header>
      <div><span className="eyebrow">MYMONEY · ANÁLISE</span><h1>Insights financeiros</h1><p className="muted header-sub">Uma leitura prática de {user?.first_name || user?.username} sobre o período.</p></div>
      <div className="header-actions"><button className="secondary" onClick={() => navigate('/dashboard')}>← Dashboard</button><button className="secondary" onClick={signOut}>Sair</button></div>
    </header>
    <section className="toolbar insights-toolbar"><label>Mês de referência<input type="month" value={month.slice(0, 7)} onChange={e => e.target.value && setMonth(`${e.target.value}-01`)} /></label><span className="muted">{monthTitle(month)}</span></section>
    {error && <div className="error page-error" role="alert">{error}</div>}
    {loading ? <section className="panel"><p className="empty">Calculando seus indicadores…</p></section> : data && <>
      <section className="metrics">
        <Metric title="Receitas" value={money(summary?.income || 0)} tone="income" detail={`${percent(summary?.income_change_percent ?? null)} vs. mês anterior`} />
        <Metric title="Despesas" value={money(summary?.expenses || 0)} tone="expense" detail={`${percent(summary?.expense_change_percent ?? null)} vs. mês anterior`} />
        <Metric title="Resultado do mês" value={money(summary?.net || 0)} tone={Number(summary?.net || 0) >= 0 ? 'income' : 'expense'} detail="Receitas menos despesas" />
      </section>
      <section className="insights-grid">
        <article className="panel"><h3>Principais categorias de despesas</h3>
          {data.top_expense_categories.length ? <div className="insight-list">{data.top_expense_categories.map((item, i) => <div className="insight-row" key={item.category_id || item.category}><span className="rank">{i + 1}</span><div className="insight-grow"><strong>{item.category}</strong><div className="mini-track"><span style={{ width: `${Math.max(0, Math.min(100, Number(item.amount) / Math.max(...data.top_expense_categories.map(x => Number(x.amount)), 1) * 100))}%` }} /></div></div><strong>{money(item.amount)}</strong></div>)}</div> : <Empty text="Nenhuma despesa registrada neste mês." />}
        </article>
        <article className="panel"><h3>Orçamentos por categoria</h3>
          {data.budgets.length ? <div className="insight-list">{data.budgets.map(item => <div className="budget-item" key={item.id}><div className="panel-title-row"><strong>{item.category}</strong><span className={item.percentage >= 100 ? 'expense' : item.percentage >= 80 ? 'budget-warning' : 'muted'}>{item.percentage.toLocaleString('pt-BR', { maximumFractionDigits: 0 })}%</span></div><div className="mini-track"><span className={item.percentage >= 100 ? 'track-critical' : item.percentage >= 80 ? 'track-warning' : ''} style={{ width: `${Math.max(0, Math.min(100, item.percentage))}%` }} /></div><div className="budget-values"><span>Gasto {money(item.spent)}</span><span>Restante {money(item.remaining)}</span></div></div>)}</div> : <Empty text="Você ainda não definiu orçamentos para este mês." />}
        </article>
        <article className="panel"><h3>Metas financeiras</h3>
          {data.goals.length ? <div className="insight-list">{data.goals.map(goal => <div className="budget-item" key={goal.id}><div className="panel-title-row"><strong>{goal.name}</strong><strong>{goal.percentage.toLocaleString('pt-BR', { maximumFractionDigits: 0 })}%</strong></div><div className="mini-track"><span style={{ width: `${Math.max(0, Math.min(100, goal.percentage))}%` }} /></div><div className="budget-values"><span>{money(goal.current_amount)} acumulado</span><span>Meta {money(goal.target_amount)}</span></div>{goal.target_date && <small className="muted">Prazo: {new Date(`${goal.target_date}T12:00:00`).toLocaleDateString('pt-BR')}</small>}</div>)}</div> : <Empty text="Nenhuma meta ativa cadastrada." />}
        </article>
        <article className="panel"><h3>Próximos lançamentos recorrentes</h3>
          {data.upcoming_recurring.length ? <div className="insight-list">{data.upcoming_recurring.map(item => <div className="insight-row recurring-row" key={item.id}><div className="insight-grow"><strong>{item.description}</strong><small className="muted">{item.account} · {new Date(`${item.next_run}T12:00:00`).toLocaleDateString('pt-BR')}</small></div><strong>{money(item.amount)}</strong></div>)}</div> : <Empty text="Nenhum lançamento recorrente previsto para os próximos 30 dias." />}
        </article>
      </section>
      <p className="insights-footnote">Os indicadores são calculados com base nos lançamentos registrados. A variação compara o mês selecionado com o mês imediatamente anterior.</p>
    </>}
  </main>
}

function Metric({ title, value, tone, detail }: { title: string; value: string; tone: string; detail: string }) {
  return <article className="metric"><span>{title}</span><strong className={tone}>{value}</strong><small className={`metric-detail ${tone}`}>{detail}</small></article>
}
function Empty({ text }: { text: string }) { return <p className="empty">{text}</p> }
