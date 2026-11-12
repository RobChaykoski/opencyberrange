import { chromium, request } from 'playwright'

const BASE = (process.env.UI_BASE_URL || '').replace(/\/$/, '')
const USERNAME = process.env.UI_SMOKE_USERNAME || ''
const PASSWORD = process.env.UI_SMOKE_PASSWORD || ''
const PAGE_PATH = process.env.UI_WIKI_PATH || '/wiki/reference/manual/'
const EXPECT = (process.env.UI_WIKI_EXPECT || '').toLowerCase()

const api = await request.newContext({ baseURL: BASE, ignoreHTTPSErrors: true })
const login = await api.post('/api/auth/login', {
  form: { username: USERNAME, password: PASSWORD },
})
const body = await login.json()
const token = body.access_token || body.token || ''
await api.dispose()

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1280, height: 900 } })
await context.addCookies([
  {
    name: 'wiki_auth',
    value: token,
    url: BASE,
    httpOnly: false,
    secure: BASE.startsWith('https:'),
    sameSite: 'Lax',
  },
])
const page = await context.newPage()
await page.goto(`${BASE}${PAGE_PATH}`, { waitUntil: 'networkidle', timeout: 60000 })
const title = await page.locator('h1').first().innerText()
const images = await page.locator('.md-content img').count()
const loaded = await page.locator('.md-content img').evaluateAll((nodes) =>
  nodes.filter((node) => node.complete && node.naturalWidth > 0).length,
)
console.log('path:', PAGE_PATH)
console.log('title:', title)
console.log('images:', images, 'loaded:', loaded)
if (EXPECT && !title.toLowerCase().includes(EXPECT)) {
  throw new Error(`Unexpected page title: ${title}`)
}
if (images > 0 && loaded < images) {
  throw new Error(`Images did not load (${loaded}/${images})`)
}
console.log('wiki page OK')
await context.close()
await browser.close()
