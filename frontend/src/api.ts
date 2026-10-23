import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'
export const api = axios.create({ baseURL: API_URL, headers: { 'Content-Type': 'application/json' } })
let accessToken: string | null = null
export const tokenStore = { get: () => accessToken, set: (token: string | null) => { accessToken = token } }
api.interceptors.request.use((config) => { const token = tokenStore.get(); if (token) config.headers.Authorization = `Bearer ${token}`; return config })

export type AuthTokens = { access: string; refresh: string }
export type User = { id: number; username: string; email: string; first_name: string; last_name: string }
export type Account = { id: string; name: string; institution: string; account_type: string; opening_balance: string; balance: string; color: string; is_active: boolean }
export type Category = { id: string; name: string; category_type: 'INCOME' | 'EXPENSE'; icon: string; color: string; is_active: boolean }
export type Transaction = { id: string; account: string; account_name: string; destination_account: string | null; destination_account_name: string | null; category: string | null; category_name: string | null; transaction_type: 'INCOME' | 'EXPENSE' | 'TRANSFER'; description: string; amount: string; transaction_date: string; notes: string }
export type DashboardData = { balance: number; income: number; expenses: number; transfers: number; accounts_count: number; categories_count: number; transactions_count: number; period: { date_from: string; date_to: string }; category_expenses: { category: string; amount: number }[]; cash_flow: { month: string; income: number; expenses: number; net: number }[]; net_worth: { month: string; value: number }[] }

let refreshPromise: Promise<string | null> | null = null
async function refreshAccessToken(): Promise<string | null> { if (!refreshPromise) refreshPromise = (async () => { const refresh = sessionStorage.getItem('mymoney_refresh_token'); if (!refresh) return null; try { const { data } = await axios.post<AuthTokens>(`${API_URL}/auth/token/refresh/`, { refresh }); tokenStore.set(data.access); if (data.refresh) sessionStorage.setItem('mymoney_refresh_token', data.refresh); return data.access } catch { tokenStore.set(null); sessionStorage.removeItem('mymoney_refresh_token'); return null } finally { refreshPromise = null } })(); return refreshPromise }
api.interceptors.response.use(r => r, async (error) => { const original = error.config; if (error.response?.status !== 401 || original?._retry) return Promise.reject(error); original._retry = true; const token = await refreshAccessToken(); if (!token) return Promise.reject(error); original.headers.Authorization = `Bearer ${token}`; return api(original) })

export async function login(username: string, password: string) { const { data } = await api.post<AuthTokens>('/auth/login/', { username, password }); tokenStore.set(data.access); sessionStorage.setItem('mymoney_refresh_token', data.refresh); return data }
export async function register(payload: { username: string; email: string; password: string; password_confirm: string; first_name?: string; last_name?: string }) { const { data } = await api.post<User>('/auth/register/', payload); return data }
export async function me() { const { data } = await api.get<User>('/auth/me/'); return data }
export async function listAccounts() { const { data } = await api.get<Account[]>('/finance/accounts/'); return data }
export async function listCategories(type?: 'INCOME' | 'EXPENSE') { const { data } = await api.get<Category[]>('/finance/categories/', { params: type ? { type } : undefined }); return data }
export async function listTransactions(params?: Record<string, string>) { const { data } = await api.get<Transaction[]>('/finance/transactions/', { params }); return data }
export async function createAccount(payload: Partial<Account>) { const { data } = await api.post<Account>('/finance/accounts/', payload); return data }
export async function createCategory(payload: Partial<Category>) { const { data } = await api.post<Category>('/finance/categories/', payload); return data }
export async function createTransaction(payload: Partial<Transaction>) { const { data } = await api.post<Transaction>('/finance/transactions/', payload); return data }
export async function updateTransaction(id: string, payload: Partial<Transaction>) { const { data } = await api.patch<Transaction>(`/finance/transactions/${id}/`, payload); return data }
export async function deleteTransaction(id: string) { await api.delete(`/finance/transactions/${id}/`) }
export async function dashboard(params?: { date_from?: string; date_to?: string }) { const { data } = await api.get<DashboardData>('/finance/dashboard/', { params }); return data }
export function logout() { tokenStore.set(null); sessionStorage.removeItem('mymoney_refresh_token') }


export type NotificationItem = {
  id: string
  notification_type: string
  severity: 'INFO' | 'WARNING' | 'CRITICAL'
  title: string
  message: string
  is_read: boolean
  created_at: string
  metadata: Record<string, unknown>
}
export type NotificationResponse = { unread_count: number; results: NotificationItem[] }
export type FinancialInsights = {
  month: string
  summary: {
    income: string; expenses: string; net: string
    previous_income: string; previous_expenses: string
    income_change_percent: number | null; expense_change_percent: number | null
  }
  top_expense_categories: { category_id: string | null; category: string; amount: string }[]
  budgets: { id: string; category: string; amount: string; spent: string; remaining: string; percentage: number }[]
  goals: { id: string; name: string; target_amount: string; current_amount: string; percentage: number; target_date: string | null }[]
  upcoming_recurring: { id: string; description: string; amount: string; next_run: string; account: string }[]
}
export async function listNotifications(unread = false) {
  const { data } = await api.get<NotificationResponse>('/finance/notifications/', { params: unread ? { unread: 'true' } : undefined })
  return data
}
export async function markNotificationRead(id: string, is_read = true) {
  const { data } = await api.patch<{ id: string; is_read: boolean }>(`/finance/notifications/${id}/read/`, { is_read })
  return data
}
export async function generateNotifications() {
  const { data } = await api.post<{ created: number; unread_count: number }>('/finance/notifications/generate/')
  return data
}
export async function getFinancialInsights(month?: string) {
  const { data } = await api.get<FinancialInsights>('/finance/insights/', { params: month ? { month } : undefined })
  return data
}


// Sprint 10 — budgets, goals and recurring transactions
export type Budget = { id: string; category: string; category_name: string; month: string; amount: string; spent: string; remaining: string; percentage: number; notes: string }
export type FinancialGoal = { id: string; name: string; target_amount: string; current_amount: string; percentage: number; remaining: string; target_date: string | null; notes: string; is_active: boolean }
export type RecurringTransaction = { id: string; account: string; account_name: string; category: string | null; category_name: string | null; transaction_type: 'INCOME' | 'EXPENSE'; description: string; amount: string; frequency: 'WEEKLY' | 'MONTHLY' | 'YEARLY'; next_run: string; end_date: string | null; is_active: boolean; notes: string }
export async function listBudgets(month?: string) { const { data } = await api.get<Budget[]>('/finance/budgets/', { params: month ? { month } : undefined }); return data }
export async function createBudget(payload: Partial<Budget>) { const { data } = await api.post<Budget>('/finance/budgets/', payload); return data }
export async function updateBudget(id: string, payload: Partial<Budget>) { const { data } = await api.patch<Budget>(`/finance/budgets/${id}/`, payload); return data }
export async function deleteBudget(id: string) { await api.delete(`/finance/budgets/${id}/`) }
export async function listGoals() { const { data } = await api.get<FinancialGoal[]>('/finance/goals/'); return data }
export async function createGoal(payload: Partial<FinancialGoal>) { const { data } = await api.post<FinancialGoal>('/finance/goals/', payload); return data }
export async function updateGoal(id: string, payload: Partial<FinancialGoal>) { const { data } = await api.patch<FinancialGoal>(`/finance/goals/${id}/`, payload); return data }
export async function deleteGoal(id: string) { await api.delete(`/finance/goals/${id}/`) }
export async function listRecurring() { const { data } = await api.get<RecurringTransaction[]>('/finance/recurring/'); return data }
export async function createRecurring(payload: Partial<RecurringTransaction>) { const { data } = await api.post<RecurringTransaction>('/finance/recurring/', payload); return data }
export async function updateRecurring(id: string, payload: Partial<RecurringTransaction>) { const { data } = await api.patch<RecurringTransaction>(`/finance/recurring/${id}/`, payload); return data }
export async function deleteRecurring(id: string) { await api.delete(`/finance/recurring/${id}/`) }
export async function generateRecurring() { const { data } = await api.post<{ created: number; transactions: string[] }>('/finance/recurring/generate/'); return data }
