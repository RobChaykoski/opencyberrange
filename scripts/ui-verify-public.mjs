#!/usr/bin/env node
/**
 * Public certificate verification smoke test.
 *
 * Checks the public /verify page without signing in:
 *   - the page loads and is not redirected to the login screen;
 *   - Verify stays disabled until the ID has a valid shape;
 *   - a malformed ID shows the format error;
 *   - a well-formed unknown ID returns the generic invalid result;
 *   - the desktop and 390 px mobile layouts have no horizontal overflow;
 *   - no page or console errors are raised.
 *
 * The result is written to UI_ARTIFACT_DIR (default ui-verify-artifacts/) with
 * screenshots. No account, token, learner record, or secret is used.
 *
 * Usage:
 *   UI_VERIFY_URLS=https://ctfd.swocts.com,https://172.16.16.44 \
 *   node scripts/ui-verify-public.mjs
 *
 * Environment:
 *   UI_VERIFY_URLS        comma-separated base URLs (default production URL)
 *   UI_ARTIFACT_DIR       evidence directory (default ui-verify-artifacts)
 *   UI_PLAYWRIGHT_PATH    module path or file URL for playwright/playwright-core
 *   UI_BROWSER_CHANNEL    Playwright browser channel (default msedge)
 *   UI_BROWSER_EXECUTABLE system browser executable; wins over the channel
 */
import fs from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'

const require = createRequire(import.meta.url)
const PLAYWRIGHT = process.env.UI_PLAYWRIGHT_PATH || 'playwright'
let chromium
try {
  ;({ chromium } = require(PLAYWRIGHT))
} catch (err) {
  console.error(`Cannot load Playwright from ${PLAYWRIGHT}.`)
  console.error('Set UI_PLAYWRIGHT_PATH or install Playwright where Node can resolve it.')
  console.error(String(err.message || err))
  process.exit(2)
}

const BASES = (process.env.UI_VERIFY_URLS || 'https://ctfd.swocts.com')
  .split(',')
  .map((value) => value.trim().replace(/\/+$/, ''))
  .filter(Boolean)
const ARTIFACT_DIR = process.env.UI_ARTIFACT_DIR || 'ui-verify-artifacts'
const VIEWPORTS = [
  { name: 'desktop', width: 1280, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
]
const MALFORMED_ID = 'OCR-BAD'
const WELL_FORMED_UNKNOWN_ID = 'OCR-WEB-L01-0123456789'
const BANNED_IN_RESULT = /email|username|student_id|user_id|score|solved_count|token/i

fs.mkdirSync(ARTIFACT_DIR, { recursive: true })

const checks = []
const failures = []
let current = { base: '', viewport: '' }

function check(name, ok, detail = '') {
  const row = { ...current, name, ok: Boolean(ok), detail: String(detail).slice(0, 300) }
  checks.push(row)
  if (!ok) failures.push(row)
  const marker = row.ok ? 'PASS' : 'FAIL'
  console.log(`${marker} ${row.base}/${row.viewport} ${name}${detail ? ` :: ${row.detail}` : ''}`)
}

const launchOptions = { headless: true }
if (process.env.UI_BROWSER_EXECUTABLE) {
  launchOptions.executablePath = process.env.UI_BROWSER_EXECUTABLE
} else {
  launchOptions.channel = process.env.UI_BROWSER_CHANNEL || 'msedge'
}

const browser = await chromium.launch(launchOptions)
try {
  for (const base of BASES) {
    for (const viewport of VIEWPORTS) {
      current = { base, viewport: viewport.name }
      const context = await browser.newContext({
        ignoreHTTPSErrors: true,
        viewport: { width: viewport.width, height: viewport.height },
        isMobile: viewport.name === 'mobile',
        hasTouch: viewport.name === 'mobile',
      })
      const page = await context.newPage()
      const pageErrors = []
      const consoleErrors = []
      page.on('pageerror', (err) => pageErrors.push(String(err)))
      page.on('console', (message) => {
        if (message.type() === 'error') consoleErrors.push(message.text())
      })

      try {
        const response = await page.goto(`${base}/verify`, {
          waitUntil: 'networkidle',
          timeout: 45000,
        })
        check('verify page loaded', response && response.status() < 400, `HTTP ${response?.status()}`)
        check('not redirected to login', !page.url().includes('/login'), page.url())

        const heading = page.locator('h1', { hasText: 'Verify a certificate' })
        check('verification heading', (await heading.count()) === 1)

        const input = page.locator('#certificate-id')
        const button = page.locator('button[type="submit"]', { hasText: 'Verify' })
        check('ID input present', (await input.count()) === 1)
        check('Verify disabled when empty', await button.isDisabled())

        await input.fill(MALFORMED_ID)
        await input.blur()
        const alert = page.locator('#certificate-id-error')
        check(
          'malformed ID shows format error',
          await alert.isVisible(),
          ((await alert.textContent()) || '').trim().slice(0, 80),
        )
        check('Verify remains disabled for malformed ID', await button.isDisabled())

        await input.fill(WELL_FORMED_UNKNOWN_ID)
        check('well-formed track ID enables Verify', await button.isEnabled())
        await button.click()
        await page.waitForURL(/\/verify\/certificate\//, { timeout: 15000 }).catch(() => {})
        check('submission routes to result URL', /\/verify\/certificate\//.test(page.url()), page.url())

        const invalid = page.locator('.verify-result--invalid')
        await invalid.waitFor({ state: 'visible', timeout: 20000 }).catch(() => {})
        check('unknown ID returns generic invalid result', await invalid.isVisible())
        const resultText = ((await invalid.textContent()) || '').replace(/\s+/g, ' ').trim()
        check('invalid result hides account details', !BANNED_IN_RESULT.test(resultText), resultText.slice(0, 100))

        const overflow = await page.evaluate(() => ({
          scrollWidth: document.documentElement.scrollWidth,
          innerWidth: window.innerWidth,
        }))
        check(
          'no horizontal overflow',
          overflow.scrollWidth <= overflow.innerWidth + 1,
          JSON.stringify(overflow),
        )

        const screenshot = `${viewport.name}-verify-invalid.png`
        await page.screenshot({ path: path.join(ARTIFACT_DIR, screenshot), fullPage: true })
        check('screenshot written', fs.existsSync(path.join(ARTIFACT_DIR, screenshot)), screenshot)
        check('no page errors', pageErrors.length === 0, pageErrors.join(' | '))
        check('no console errors', consoleErrors.length === 0, consoleErrors.join(' | '))
      } catch (err) {
        check('exception', false, String(err))
      } finally {
        await context.close()
      }
    }
  }
} finally {
  await browser.close()
}

const evidence = {
  schema: 1,
  runAt: new Date().toISOString(),
  script: path.basename(fileURLToPath(import.meta.url)),
  bases: BASES,
  checks,
  failed: failures.length,
  artifacts: fs
    .readdirSync(ARTIFACT_DIR)
    .filter((name) => name.endsWith('.png'))
    .sort(),
}
fs.writeFileSync(
  path.join(ARTIFACT_DIR, 'verify-public.json'),
  JSON.stringify(evidence, null, 2) + '\n',
  'utf8',
)

console.log(`\n${checks.length - failures.length}/${checks.length} checks passed, ${failures.length} failed`)
process.exit(failures.length ? 1 : 0)
