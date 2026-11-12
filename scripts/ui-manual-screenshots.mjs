/**
 * Capture manual screenshots for the advanced DNA insights preview.
 *
 * Run this on a development deployment after the feature is enabled:
 *
 *   UI_BASE_URL=https://172.16.16.44 \
 *   UI_SMOKE_USERNAME=... UI_SMOKE_PASSWORD=... \
 *   node scripts/ui-manual-screenshots.mjs
 *
 * Or pass a short-lived token with UI_SMOKE_TOKEN.
 *
 * The script only performs GETs and UI navigation. It writes:
 *   Manual-Lite/02_Student_Guide/img/profile-momentum.png
 *   Manual-Lite/02_Student_Guide/img/profile-careers.png
 *   Manual-Lite/04_Admin_Guide/img/admin-settings-features.png
 *
 * It requires Playwright, as the other UI scripts do:
 *   npm install --no-save playwright
 *   npx playwright install --with-deps chromium
 */
import fs from 'node:fs'
import path from 'node:path'
import { chromium, request } from 'playwright'

const BASE = (process.env.UI_BASE_URL || '').replace(/\/$/, '')
let TOKEN = process.env.UI_SMOKE_TOKEN || ''
const USERNAME = process.env.UI_SMOKE_USERNAME || ''
const PASSWORD = process.env.UI_SMOKE_PASSWORD || ''
const ROOT = process.cwd()
const STUDENT_IMG = path.join(ROOT, 'Manual-Lite', '02_Student_Guide', 'img')
const ADMIN_IMG = path.join(ROOT, 'Manual-Lite', '04_Admin_Guide', 'img')

if (!BASE) {
  console.log('Manual screenshots skipped: UI_BASE_URL is required.')
  process.exit(0)
}

async function login() {
  if (TOKEN) {
    const api = await request.newContext({
      baseURL: BASE,
      ignoreHTTPSErrors: true,
      extraHTTPHeaders: { Authorization: `Bearer ${TOKEN}` },
    })
    try {
      const me = await api.get('/api/auth/me')
      if (!me.ok()) return null
      return { token: TOKEN, user: await me.json() }
    } finally {
      await api.dispose()
    }
  }
  if (!USERNAME || !PASSWORD) return null
  const api = await request.newContext({ baseURL: BASE, ignoreHTTPSErrors: true })
  try {
    const response = await api.post('/api/auth/login', {
      form: { username: USERNAME, password: PASSWORD },
    })
    if (!response.ok()) return null
    const body = await response.json()
    const token = body.access_token || body.token || ''
    if (!token) return null
    const me = await api.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
    return { token, user: me.ok() ? await me.json() : {} }
  } finally {
    await api.dispose()
  }
}

const session = await login()
if (!session?.token) {
  console.error('Manual screenshots failed: provide UI_SMOKE_TOKEN or UI_SMOKE_USERNAME / UI_SMOKE_PASSWORD.')
  process.exit(1)
}

fs.mkdirSync(STUDENT_IMG, { recursive: true })
fs.mkdirSync(ADMIN_IMG, { recursive: true })

const browser = await chromium.launch({ headless: true })
const written = []
const errors = []

async function contextFor(theme, viewport = { width: 1440, height: 1100 }) {
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport,
    deviceScaleFactor: 2,
  })
  await context.addInitScript(({ token, user, theme }) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    localStorage.setItem('theme', theme)
    localStorage.setItem('ocr_orientation_seen_v1_' + user.username, '1')
  }, { token: session.token, user: session.user, theme })
  const page = await context.newPage()
  page.on('pageerror', (error) => errors.push(String(error)))
  return { context, page }
}

async function shot(page, selector, target, label) {
  const locator = page.locator(selector).first()
  await locator.waitFor({ state: 'visible', timeout: 45000 })
  await locator.scrollIntoViewIfNeeded()
  await page.waitForTimeout(350)
  await locator.screenshot({ path: target, animations: 'disabled' })
  written.push(path.relative(ROOT, target))
  console.log(`WROTE: ${label} -> ${path.relative(ROOT, target)}`)
}

const dark = await contextFor('dark')
try {
  await dark.page.goto(`${BASE}/profile?tab=skill-tree`, { waitUntil: 'networkidle', timeout: 45000 })
  if (!(await dark.page.locator('.momentum').count())) {
    console.error(
      'Momentum is not visible. Enable Admin -> Settings -> Features -> Advanced DNA Insights on this deployment.'
    )
    process.exitCode = 1
  } else {
    await shot(
      dark.page,
      '.dna-section',
      path.join(STUDENT_IMG, 'profile-dna.png'),
      'Cyber DNA section'
    )
    await shot(
      dark.page,
      '.momentum',
      path.join(STUDENT_IMG, 'profile-momentum.png'),
      'Momentum panel'
    )
  }

  await dark.page.goto(`${BASE}/profile?tab=careers`, { waitUntil: 'networkidle', timeout: 45000 })
  if (!(await dark.page.locator('.atlas').count())) {
    console.error(
      'Career Atlas is not visible. Enable Admin -> Settings -> Features -> Advanced DNA Insights on this deployment.'
    )
    process.exitCode = 1
  } else {
    await shot(
      dark.page,
      '.atlas',
      path.join(STUDENT_IMG, 'profile-careers.png'),
      'Career Atlas'
    )
  }
} finally {
  await dark.context.close()
}

if (session.user?.role === 'admin') {
  const admin = await contextFor('dark', { width: 1440, height: 1000 })
  try {
    await admin.page.goto(`${BASE}/admin?tab=settings`, { waitUntil: 'networkidle', timeout: 45000 })
    const features = admin.page.locator('button.lab-tab', { hasText: 'Features' }).first()
    if (await features.count()) {
      await features.click()
      await admin.page.waitForTimeout(500)
      await admin.page.screenshot({
        path: path.join(ADMIN_IMG, 'admin-settings-features.png'),
        fullPage: false,
        animations: 'disabled',
      })
      written.push(path.relative(ROOT, path.join(ADMIN_IMG, 'admin-settings-features.png')))
      console.log('WROTE: Admin Features settings -> Manual-Lite/04_Admin_Guide/img/admin-settings-features.png')
    } else {
      console.error('Features settings tab not found. Is this build current?')
      process.exitCode = 1
    }
  } finally {
    await admin.context.close()
  }
} else {
  console.log('Skipped admin screenshot: the signed-in account is not an administrator.')
}

await browser.close()

if (errors.length) {
  console.error('Page errors observed during capture:')
  for (const error of errors) console.error(`  - ${error}`)
  process.exitCode = 1
}

console.log(`Manual screenshots complete: ${written.length} file(s).`)
