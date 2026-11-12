import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium, request } from 'playwright'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..')
const BASE = (process.env.UI_BASE_URL || '').replace(/\/$/, '')
const USERNAME = process.env.UI_SMOKE_USERNAME || ''
const PASSWORD = process.env.UI_SMOKE_PASSWORD || ''

const api = await request.newContext({ baseURL: BASE, ignoreHTTPSErrors: true })
const response = await api.post('/api/auth/login', { form: { username: USERNAME, password: PASSWORD } })
console.log('login', response.status())
const body = await response.json()
const token = body.access_token || body.token || ''
const me = await api.get('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } })
const user = me.ok() ? await me.json() : {}
console.log('me', me.status(), user.username, user.role)
await api.dispose()

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1440, height: 1200 } })
await context.addInitScript(({ token, user }) => {
  localStorage.setItem('token', token)
  localStorage.setItem('user', JSON.stringify(user))
  localStorage.setItem('theme', 'dark')
  localStorage.setItem('ocr_orientation_seen_v1_' + user.username, '1')
}, { token, user })
const page = await context.newPage()
page.on('console', (msg) => console.log('console:', msg.type(), msg.text().slice(0, 200)))
page.on('pageerror', (error) => console.log('pageerror:', String(error).slice(0, 300)))
await page.goto(`${BASE}/profile?tab=skill-tree`, { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(4000)
console.log('url', page.url())
console.log('dna', await page.locator('.dna-section').count())
console.log('text', (await page.locator('body').innerText()).slice(0, 1200))
await page.screenshot({ path: path.join(ROOT, 'debug-profile.png'), fullPage: true })
await context.close()
await browser.close()
