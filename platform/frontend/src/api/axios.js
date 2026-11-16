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

let refreshInFlight = null

async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) throw new Error('no refresh token')
  if (!refreshInFlight) {
    refreshInFlight = axios
      .post('/api/auth/refresh', { refresh_token: refreshToken })
      .then(({ data }) => {
        localStorage.setItem('token', data.access_token)
        if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
        return data.access_token
      })
      .finally(() => {
        refreshInFlight = null
      })
  }
  return refreshInFlight
}

function clearSession() {
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
}

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const url = String(error.config?.url || '')
    const onLogin = window.location.pathname === '/login'
    const status = error.response?.status
    if (status === 403 && error.response?.headers?.['x-reauth-required']) {
      window.dispatchEvent(
        new CustomEvent('ocr:reauth-required', {
          detail: { purpose: error.response.headers['x-reauth-purpose'] || '' },
        })
      )
      return Promise.reject(error)
    }
    // A wiki-cookie probe is best-effort and must never trigger a redirect.
    // Nor should a 401 on the login page reload it (bad password, expired
    // stale token, or the wiki probe): both would cause a reload loop.
    if (status === 401 && !url.includes('/auth/wiki-cookie') && !onLogin) {
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
          if (saved.refresh_token) localStorage.setItem('refresh_token', saved.refresh_token)
          if (saved.user) localStorage.setItem('user', saved.user)
        }
        sessionStorage.removeItem('ocr_impersonating')
        sessionStorage.removeItem('ocr_original_session')
        sessionStorage.removeItem('ocr_imp_meta')
        window.location.href = '/dashboard'
        return Promise.reject(error)
      }

      // One refresh attempt per request. The refresh endpoint itself is
      // excluded so a rejected refresh cannot recurse.
      if (
        !error.config?._retry &&
        !url.includes('/auth/refresh') &&
        !url.includes('/auth/login') &&
        localStorage.getItem('refresh_token')
      ) {
        error.config._retry = true
        try {
          const accessToken = await refreshAccessToken()
          error.config.headers = error.config.headers || {}
          error.config.headers.Authorization = `Bearer ${accessToken}`
          return api(error.config)
        } catch {
          clearSession()
        }
      } else {
        clearSession()
      }
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
