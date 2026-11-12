/**
 * Capture the workbook reading view from a dev deployment.
 *
 *   UI_BASE_URL=https://172.16.16.44 \
 *   UI_SMOKE_USERNAME=... UI_SMOKE_PASSWORD=... \
 *   node platform/frontend/ui-workbook-screenshot.mjs
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium, request } from 'playwright'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..')
const BASE = (process.env.UI_BASE_URL || '').replace(/\/$/, '')
const USERNAME = process.env.UI_SMOKE_USERNAME || ''
const PASSWORD = process.env.UI_SMOKE_PASSWORD || ''
const WORKBOOK_PATH =
  process.env.UI_WORKBOOK_PATH ||
  '/wiki/range/malware/CH_MAL01_Malware_Fundamentals/01_EICAR_Triage/'

if (!BASE || !USERNAME || !PASSWORD) {
  console.log('Workbook screenshot skipped: UI_BASE_URL and credentials are required.')
  process.exit(0)
}

const api = await request.newContext({ baseURL: BASE, ignoreHTTPSErrors: true })
const login = await api.post('/api/auth/login', {
  form: { username: USERNAME, password: PASSWORD },
})
if (!login.ok()) {
  console.error(`Login failed: ${login.status()} ${await login.text()}`)
  process.exit(1)
}
const body = await login.json()
const token = body.access_token || body.token || ''
const me = await api.get('/api/auth/me', {
  headers: { Authorization: `Bearer ${token}` },
})
const user = me.ok() ? await me.json() : {}
await api.dispose()

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({
  ignoreHTTPSErrors: true,
  viewport: { width: 1440, height: 1200 },
  deviceScaleFactor: 2,
})
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
await page.goto(`${BASE}${WORKBOOK_PATH}`, {
  waitUntil: 'networkidle',
  timeout: 60000,
})
const article = page.locator('.md-content').first()
await article.waitFor({ state: 'visible', timeout: 45000 })
await page.waitForTimeout(400)

const studentImg = path.join(ROOT, 'Manual-Lite', '02_Student_Guide', 'img')
const workbookAssets = path.join(ROOT, 'Workbook', 'assets')
fs.mkdirSync(studentImg, { recursive: true })
fs.mkdirSync(workbookAssets, { recursive: true })
const targets = [
  path.join(studentImg, 'workbook-reading.png'),
  path.join(workbookAssets, 'workbook-reading.png'),
]
for (const target of targets) {
  await article.screenshot({ path: target, animations: 'disabled' })
  console.log(`WROTE: workbook reading view -> ${path.relative(ROOT, target)}`)
}

await context.close()
await browser.close()
