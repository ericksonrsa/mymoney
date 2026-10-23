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
