import axios from 'axios'

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const url = String(error.config?.url || '')
    const onLogin = window.location.pathname === '/login'
    // A wiki-cookie probe is best-effort and must never trigger a redirect.
    // Nor should a 401 on the login page reload it (bad password, expired
    // stale token, or the wiki probe): both would cause a reload loop.
    if (error.response?.status === 401 && !url.includes('/auth/wiki-cookie') && !onLogin) {
      // If impersonating and token expired, restore original session
      const imp = sessionStorage.getItem('ocr_impersonating') === 'true'
      if (imp) {
        let saved = {}
        try {
          saved = JSON.parse(sessionStorage.getItem('ocr_original_session') || '{}')
        } catch {
          // Malformed impersonation state must not block the redirect; the
          // empty object above is the safe fallback.
        }
        if (saved.token) {
          localStorage.setItem('token', saved.token)
          if (saved.user) localStorage.setItem('user', saved.user)
        }
        sessionStorage.removeItem('ocr_impersonating')
        sessionStorage.removeItem('ocr_original_session')
        sessionStorage.removeItem('ocr_imp_meta')
        window.location.href = '/dashboard'
      } else {
        // Token expired or invalid - redirect to login
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
