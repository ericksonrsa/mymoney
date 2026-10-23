import { FormEvent, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createInvoice, deleteInvoice, listInvoices, listTransactions, updateInvoice, type Invoice, type Transaction } from './api'
import './styles.css'

function money(value: number | string) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(value) || 0)
}
function today() { return new Date().toISOString().slice(0, 10) }
function firstDay() { const d = new Date(); return new Date(d.getFullYear(), d.getMonth(), 1).toISOString().slice(0, 10) }

export function InvoicePage() {
  const navigate = useNavigate()
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [selected, setSelected] = useState<string[]>([])
  const [title, setTitle] = useState('')
  const [periodStart, setPeriodStart] = useState(firstDay())
  const [periodEnd, setPeriodEnd] = useState(today())
  const [dueDate, setDueDate] = useState('')
  const [notes, setNotes] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [showCreate, setShowCreate] = useState(false)

  async function load() {
    try {
      setError('')
      const [invoiceData, transactionData] = await Promise.all([
        listInvoices(statusFilter || undefined),
        listTransactions({ date_from: periodStart, date_to: periodEnd }),
      ])
      setInvoices(invoiceData)
      setTransactions(transactionData)
    } catch {
      setError('Não foi possível carregar as faturas. Verifique sua conexão e tente novamente.')
    }
  }
  useEffect(() => { void load() }, [statusFilter, periodStart, periodEnd])

  const totals = useMemo(() => invoices.reduce((acc, invoice) => ({
    open: acc.open + (invoice.status === 'OPEN' ? Number(invoice.net_total) : 0),
    paid: acc.paid + (invoice.status === 'PAID' ? Number(invoice.net_total) : 0),
    count: acc.count + 1,
  }), { open: 0, paid: 0, count: 0 }), [invoices])

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!selected.length) { setError('Selecione ao menos um lançamento para consolidar.'); return }
    setBusy(true); setError('')
    try {
      await createInvoice({ title, period_start: periodStart, period_end: periodEnd, due_date: dueDate || null, notes, transactions: selected })
      setShowCreate(false); setTitle(''); setNotes(''); setDueDate(''); setSelected([])
      await load()
    } catch (e: any) {
      const data = e?.response?.data
      setError(data ? Object.values(data).flat().join(' ') : 'Não foi possível criar a fatura.')
    } finally { setBusy(false) }
  }

  async function changeStatus(invoice: Invoice) {
    try {
      await updateInvoice(invoice.id, { status: invoice.status === 'PAID' ? 'OPEN' : 'PAID' })
      await load()
    } catch { setError('Não foi possível atualizar o status da fatura.') }
  }
  async function remove(invoice: Invoice) {
    if (!window.confirm(`Excluir a fatura “${invoice.title}”? Os lançamentos originais serão mantidos.`)) return
    try { await deleteInvoice(invoice.id); await load() } catch { setError('Não foi possível excluir a fatura.') }
  }

  return <main className="dashboard invoice-page">
    <header>
      <div><span className="eyebrow">MYMONEY · ORGANIZAÇÃO FINANCEIRA</span><h1>Faturas</h1><p className="muted header-sub">Consolide vários lançamentos de crédito e débito em um único demonstrativo.</p></div>
      <div className="header-actions"><button className="secondary" onClick={() => navigate('/dashboard')}>Voltar ao painel</button><button onClick={() => { setShowCreate(v => !v); setError('') }}>+ Nova fatura</button></div>
    </header>
    <section className="metrics">
      <Metric title="Faturas listadas" value={String(totals.count)} />
      <Metric title="Saldo líquido em aberto" value={money(totals.open)} negative={totals.open > 0} positive={totals.open < 0} />
      <Metric title="Saldo líquido pago" value={money(totals.paid)} positive />
      <Metric title="Lançamentos disponíveis" value={String(transactions.filter(t => t.transaction_type !== 'TRANSFER').length)} />
    </section>
    <section className="toolbar invoice-toolbar">
      <label>Status<select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}><option value="">Todas</option><option value="OPEN">Em aberto</option><option value="PAID">Pagas</option><option value="CANCELLED">Canceladas</option></select></label>
      <label>Período de lançamentos — início<input type="date" value={periodStart} onChange={e => setPeriodStart(e.target.value)} /></label>
      <label>Fim<input type="date" value={periodEnd} onChange={e => setPeriodEnd(e.target.value)} /></label>
    </section>
    {error && <div className="error page-error">{error}</div>}
    {showCreate && <section className="panel invoice-create">
      <div className="panel-title-row"><div><h3>Nova fatura consolidada</h3><p className="muted">Escolha os lançamentos existentes. Eles não serão duplicados nem alterados.</p></div><button className="secondary" onClick={() => setShowCreate(false)}>Fechar</button></div>
      <form className="modal-form" onSubmit={submit}>
        <label>Nome da fatura<input value={title} onChange={e => setTitle(e.target.value)} maxLength={140} placeholder="Ex.: Fatura principal — outubro" required /></label>
        <div className="management-form-row">
          <label>Início do período<input type="date" value={periodStart} onChange={e => setPeriodStart(e.target.value)} required /></label>
          <label>Fim do período<input type="date" value={periodEnd} onChange={e => setPeriodEnd(e.target.value)} min={periodStart} required /></label>
          <label>Vencimento (opcional)<input type="date" value={dueDate} onChange={e => setDueDate(e.target.value)} /></label>
        </div>
        <label>Observações<input value={notes} onChange={e => setNotes(e.target.value)} maxLength={300} /></label>
        <div className="invoice-select-head"><strong>Selecione os lançamentos</strong><span>{selected.length} selecionado(s)</span></div>
        <div className="invoice-transaction-picker">
          {transactions.filter(t => t.transaction_type !== 'TRANSFER').map(t => <label className="invoice-check-row" key={t.id}>
            <input type="checkbox" checked={selected.includes(t.id)} onChange={e => setSelected(current => e.target.checked ? [...current, t.id] : current.filter(id => id !== t.id))} />
            <span><strong>{t.description}</strong><small>{t.transaction_date} · {t.category_name || 'Sem categoria'} · {t.account_name}</small></span>
            <b className={t.transaction_type === 'INCOME' ? 'income' : 'expense'}>{t.transaction_type === 'INCOME' ? '+' : '−'} {money(t.amount)}</b>
          </label>)}
          {!transactions.filter(t => t.transaction_type !== 'TRANSFER').length && <p className="empty">Não há lançamentos de receita ou despesa nesse período.</p>}
        </div>
        <div className="management-form-actions"><button className="secondary" type="button" onClick={() => setShowCreate(false)}>Cancelar</button><button disabled={busy}>{busy ? 'Consolidando…' : `Criar fatura · ${selected.length} lançamento(s)`}</button></div>
      </form>
    </section>}
    <section className="invoice-list">
      {invoices.map(invoice => <article className="panel invoice-card" key={invoice.id}>
        <div className="invoice-card-header"><div><span className={`invoice-status ${invoice.status.toLowerCase()}`}>{invoice.status === 'OPEN' ? 'Em aberto' : invoice.status === 'PAID' ? 'Paga' : 'Cancelada'}</span><h2>{invoice.title}</h2><p className="muted">Período: {invoice.period_start} a {invoice.period_end}{invoice.due_date ? ` · Vencimento: ${invoice.due_date}` : ''}</p></div><div className="invoice-total"><small>Saldo líquido (débitos − créditos)</small><strong>{money(invoice.net_total)}</strong></div></div>
        <div className="invoice-breakdown"><div><small>Créditos / receitas</small><strong className="income">{money(invoice.credit_total)}</strong></div><div><small>Débitos / despesas</small><strong className="expense">{money(invoice.debit_total)}</strong></div><div><small>Lançamentos</small><strong>{invoice.transaction_count}</strong></div></div>
        {invoice.notes && <p className="invoice-notes">{invoice.notes}</p>}
        <details className="invoice-details"><summary>Ver lançamentos consolidados</summary><div className="list">{invoice.transaction_items.map(item => <div className="row" key={item.id}><div><strong>{item.description}</strong><small>{item.transaction_date} · {item.account_name} · {item.category_name || 'Sem categoria'}</small></div><strong className={item.transaction_type === 'INCOME' ? 'income' : 'expense'}>{item.transaction_type === 'INCOME' ? '+' : '−'} {money(item.amount)}</strong></div>)}</div></details>
        <div className="invoice-actions">{invoice.status !== 'CANCELLED' && <button className="secondary" onClick={() => void changeStatus(invoice)}>{invoice.status === 'PAID' ? 'Reabrir fatura' : 'Marcar como paga'}</button>}<button className="secondary danger" onClick={() => void remove(invoice)}>Excluir fatura</button></div>
      </article>)}
      {!invoices.length && !error && <article className="panel management-empty"><div className="empty-icon">▤</div><h3>Nenhuma fatura por aqui</h3><p>Crie uma fatura para reunir receitas e despesas existentes, visualizar créditos, débitos e o saldo líquido.</p><button onClick={() => setShowCreate(true)}>Criar primeira fatura</button></article>}
    </section>
  </main>
}

function Metric({ title, value, positive, negative }: { title: string; value: string; positive?: boolean; negative?: boolean }) {
  return <article className="metric"><span>{title}</span><strong className={positive ? 'income' : negative ? 'expense' : ''}>{value}</strong></article>
}
