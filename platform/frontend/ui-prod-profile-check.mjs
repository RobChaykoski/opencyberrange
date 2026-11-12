import { chromium, request } from 'playwright'

const BASE = (process.env.UI_BASE_URL || 'https://172.16.16.41').replace(/\/$/, '')
const TOKEN = process.env.UI_TOKEN || ''

if (!TOKEN) {
  console.error('UI_TOKEN is required')
  process.exit(1)
}

const api = await request.newContext({
  baseURL: BASE,
  ignoreHTTPSErrors: true,
  extraHTTPHeaders: { Authorization: `Bearer ${TOKEN}` },
})
const me = await api.get('/api/auth/me')
if (!me.ok()) {
  console.error('token rejected', me.status())
  process.exit(1)
}
const user = await me.json()
await api.dispose()

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1440, height: 1000 } })
await context.addInitScript(({ token, user }) => {
  localStorage.setItem('token', token)
  localStorage.setItem('user', JSON.stringify(user))
  localStorage.setItem('theme', 'dark')
  localStorage.setItem('ocr_orientation_seen_v1_' + user.username, '1')
}, { token: TOKEN, user })

const page = await context.newPage()
await page.goto(`${BASE}/profile?tab=careers`, { waitUntil: 'networkidle', timeout: 60000 })
await page.locator('.gps').first().waitFor({ state: 'visible', timeout: 30000 })
await page.locator('.atlas').first().waitFor({ state: 'visible', timeout: 30000 })
console.log('careers: gps and atlas visible')

await page.goto(`${BASE}/profile?tab=skill-tree`, { waitUntil: 'networkidle', timeout: 60000 })
await page.locator('.dna-section').first().waitFor({ state: 'visible', timeout: 30000 })
await page.locator('.dna-ce').first().waitFor({ state: 'visible', timeout: 30000 })
const trends = await page.locator('.dna-tree__trend').count()
console.log('skill-tree: cyber dna and continuing education visible; trend lines', trends)
if (trends < 1) throw new Error('No Cyber DNA trend lines rendered')
console.log('profile check OK')
await context.close()
await browser.close()
