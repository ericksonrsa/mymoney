import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

export const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

let accessToken: string | null = null

export const tokenStore = {
  get: () => accessToken,
  set: (token: string | null) => {
    accessToken = token,
  },
}

api.interceptors.request.use((config) => {
  const token = tokenStore.get()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export type AuthTokens = { access: string; refresh: string }
export type User = { id: number; username: string; email: string; first_name: string; last_name: string }

let refreshPromise: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      const refresh = sessionStorage.getItem('mymoney_refresh_token')
      if (!refresh) return null
      try {
        const { data } = await axios.post<AuthTokens>(`${API_URL}/auth/token/refresh/`, { refresh })
        tokenStore.set(data.access)
        return data.access
      } catch {
        tokenStore.set(null)
        sessionStorage.removeItem('mymoney_refresh_token')
        return null
      } finally {
        refreshPromise = null
      }
    })()
  }
  return refreshPromise
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status !== 401 || original?._retry) return Promise.reject(error)
    original._retry = true
    const token = await refreshAccessToken()
    if (!token) return Promise.reject(error)
    original.headers.Authorization = `Bearer ${token}`
    return api(original)
  },
)

export async function login(username: string, password: string) {
  const { data } = await api.post<AuthTokens>('/auth/login/', { username, password })
  tokenStore.set(data.access)
  sessionStorage.setItem('mymoney_refresh_token', data.refresh)
  return data
}

export async function register(payload: { username: string; email: string; password: string; password_confirm: string }) {
  const { data } = await api.post<User>('/auth/register/', payload)
  return data
}

export async function me() {
  const { data } = await api.get<User>('/auth/me/')
  return data
}

export function logout() {
  tokenStore.set(null)
  sessionStorage.removeItem('mymoney_refresh_token')
}
