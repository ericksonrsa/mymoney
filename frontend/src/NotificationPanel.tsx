import { useCallback, useEffect, useState } from 'react'
import { generateNotifications, listNotifications, markNotificationRead, type NotificationItem } from './api'

function dateLabel(value: string) {
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(value))
}

export function NotificationPanel() {
  const [items, setItems] = useState<NotificationItem[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [unreadOnly, setUnreadOnly] = useState(false)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const result = await listNotifications(unreadOnly)
      setItems(result.results || [])
      setUnreadCount(result.unread_count || 0)
    } catch {
      setError('Não foi possível carregar as notificações. Verifique se a API está disponível.')
    } finally {
      setLoading(false)
    }
  }, [unreadOnly])

  useEffect(() => { void load() }, [load])

  async function generate() {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      const result = await generateNotifications()
      setMessage(result.created ? `${result.created} alerta(s) novo(s) criado(s).` : 'Nenhum alerta novo neste momento.')
      await load()
    } catch {
      setError('Não foi possível gerar alertas financeiros.')
    } finally {
      setBusy(false)
    }
  }

  async function toggleRead(item: NotificationItem) {
    try {
      await markNotificationRead(item.id, !item.is_read)
      await load()
    } catch {
      setError('Não foi possível atualizar esta notificação.')
    }
  }

  return <section className="panel notification-panel">
    <div className="panel-title-row notification-title">
      <div><h3>Central de notificações</h3><p className="muted compact-muted">{unreadCount} não lida(s)</p></div>
      <div className="notification-actions">
        <button className="secondary" onClick={() => setUnreadOnly(!unreadOnly)}>{unreadOnly ? 'Ver todas' : 'Só não lidas'}</button>
        <button disabled={busy} onClick={generate}>{busy ? 'Verificando…' : 'Verificar alertas'}</button>
      </div>
    </div>
    {message && <p className="success-message" role="status">{message}</p>}
    {error && <p className="error" role="alert">{error}</p>}
    {loading ? <p className="empty">Carregando notificações…</p> : items.length ? <div className="notification-list">
      {items.slice(0, 6).map(item => <article className={`notification-item ${item.is_read ? 'is-read' : 'is-unread'}`} key={item.id}>
        <span className={`severity-dot severity-${item.severity.toLowerCase()}`} />
        <div className="notification-copy">
          <div className="notification-heading"><strong>{item.title}</strong>{!item.is_read && <span className="unread-label">Nova</span>}</div>
          <p>{item.message}</p><small>{dateLabel(item.created_at)}</small>
        </div>
        <button className="secondary notification-read" onClick={() => toggleRead(item)}>{item.is_read ? 'Marcar não lida' : 'Marcar lida'}</button>
      </article>)}
      {items.length > 6 && <p className="muted compact-muted">Exibindo as 6 notificações mais recentes.</p>}
    </div> : <p className="empty">{unreadOnly ? 'Você não tem notificações não lidas.' : 'Nenhuma notificação por enquanto. Use “Verificar alertas” para avaliar seus orçamentos e metas.'}</p>}
  </section>
}
