import api from '../api/axios'

// Keep the wiki session cookie in sync with the current login.
//
// The SPA token stays in localStorage, but the framed wiki must not be able to
// read it. The backend copies the JWT into an HttpOnly `wiki_session` cookie
// scoped by WIKI_COOKIE_DOMAIN. Nginx validates that cookie for wiki
// subrequests. Nothing here writes the JWT from JavaScript.
//
// IMPORTANT: every place that refreshes wiki auth must use THIS helper so the
// cookie scope and refresh timing stay consistent.
export async function setWikiAuthCookie() {
  // Do not probe an authenticated endpoint from the login page or any other
  // unauthenticated view. A 401 here used to trigger the axios redirect
  // interceptor, which reloaded /login and started the probe again.
  if (!localStorage.getItem('token')) return
  try {
    await api.post('/auth/wiki-cookie')
  } catch {
    // The wiki is optional on pages that never open one. A missing cookie
    // surfaces as a normal wiki login redirect rather than breaking the page.
  }
}

// Remove the HttpOnly cookie on logout or account deletion. Also clear the
// legacy JS-readable cookie from pre-origin-split builds so it cannot shadow
// the scoped cookie.
export async function clearWikiAuthCookie() {
  try {
    await api.delete('/auth/wiki-cookie')
  } catch {
    // Best effort: the server-side logout path also expires the cookie.
  }
  const host = window.location.hostname
  const isIp = /^\d{1,3}(\.\d{1,3}){3}$/.test(host)
  const domainAttr = (!isIp && host !== 'localhost' && host.includes('.'))
    ? `; Domain=${host}` : ''
  document.cookie = `wiki_auth=; path=/; max-age=0${domainAttr}`
  document.cookie = 'wiki_auth=; path=/; max-age=0'
}
