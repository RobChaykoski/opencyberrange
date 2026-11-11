/**
 * Exercise-workspace regression walkthrough.
 *
 * Verifies the combined desktop workspace (RangeBox + details/flag + framed
 * workbook) as a student and, optionally, as an instructor. It also checks the
 * main workspace controls: Expand/Restore, Open RangeBox in a new tab, Open
 * workbook in a new tab, Request Hint, flag error handling, and Stop.
 *
 * Required environment:
 *   UI_BASE_URL                 e.g. https://ctfd.swocts.com
 *   UI_STUDENT_USERNAME         dedicated test student account
 *   UI_STUDENT_PASSWORD
 *
 * Optional:
 *   UI_INSTRUCTOR_USERNAME      dedicated test instructor account
 *   UI_INSTRUCTOR_PASSWORD
 *   UI_TRACK_SLUG               default: high-school
 *   UI_LAB_NAME                 default: RangeBox First Steps
 *   UI_ARTIFACT_DIR             default: ui-workspace-artifacts
 *   UI_BROWSER_EXECUTABLE       system Chromium/Edge path
 *   UI_PLAYWRIGHT_PATH          module path or file URL for playwright/playwright-core
 *   UI_SKIP_INSTRUCTOR=1        run the student checks only
 *   UI_KEEP_SESSION=1           leave the lab running for manual inspection
 *
 * The script only launches an isolated lab for the dedicated test accounts. It
 * accepts the Stop confirmation dialog, never submits a correct flag, and never
 * changes another learner's record.
 */
import fs from 'node:fs'
import path from 'node:path'

const BASE = (process.env.UI_BASE_URL || '').replace(/\/$/, '')
const STUDENT_USER = process.env.UI_STUDENT_USERNAME || ''
const STUDENT_PASS = process.env.UI_STUDENT_PASSWORD || ''
const INSTRUCTOR_USER = process.env.UI_INSTRUCTOR_USERNAME || ''
const INSTRUCTOR_PASS = process.env.UI_INSTRUCTOR_PASSWORD || ''
const TRACK = process.env.UI_TRACK_SLUG || 'high-school'
const LAB_NAME = process.env.UI_LAB_NAME || 'RangeBox First Steps'
const OUT = process.env.UI_ARTIFACT_DIR || 'ui-workspace-artifacts'
const ARTIFACTS = []
const CHECKS = []

if (!BASE) {
  console.log('Workspace regression skipped: UI_BASE_URL is required.')
  process.exit(0)
}
if (!STUDENT_USER || !STUDENT_PASS) {
  console.log('Workspace regression skipped: UI_STUDENT_USERNAME and UI_STUDENT_PASSWORD are required.')
  process.exit(0)
}

const PLAYWRIGHT = process.env.UI_PLAYWRIGHT_PATH || 'playwright'
let chromium
let request
try {
  ;({ chromium, request } = await import(PLAYWRIGHT))
} catch (error) {
  console.error(`Cannot load Playwright from ${PLAYWRIGHT}.`)
  console.error('Install it with: npm install --no-save playwright')
  console.error(error.message)
  process.exit(2)
}

fs.mkdirSync(OUT, { recursive: true })

function check(name, ok, detail = '') {
  CHECKS.push({ name, ok, detail })
  console.log(`${ok ? 'PASS' : 'FAIL'}: ${name}${detail ? ' - ' + detail : ''}`)
}

async function loginAs(username, password) {
  const api = await request.newContext({ baseURL: BASE, ignoreHTTPSErrors: true })
  try {
    const response = await api.post('/api/auth/login', {
      form: { username, password },
    })
    if (!response.ok()) {
      console.error(`Login failed for ${username}: HTTP ${response.status()}`)
      return null
    }
    const body = await response.json()
    const token = body.access_token || body.token || ''
    if (!token) return null
    const meResponse = await api.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const user = meResponse.ok() ? await meResponse.json() : (body.user || {})
    return { token, user }
  } finally {
    await api.dispose()
  }
}

const browser = await chromium.launch({
  headless: true,
  ...(process.env.UI_BROWSER_EXECUTABLE ? { executablePath: process.env.UI_BROWSER_EXECUTABLE } : {}),
})
const pageErrors = []
const consoleErrors = []

async function contextFor(viewport, session) {
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport,
    deviceScaleFactor: 1,
    isMobile: viewport.width <= 768,
    hasTouch: viewport.width <= 768,
  })
  await context.addInitScript(({ token, user }) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    localStorage.setItem('ocr_orientation_seen_v1_' + user.username, '1')
  }, session)
  const page = await context.newPage()
  page.on('pageerror', (error) => pageErrors.push(String(error)))
  page.on('console', (message) => {
    if (message.type() === 'error' && isRelevantConsoleError(message.text())) {
      consoleErrors.push(message.text())
    }
  })
  page.on('dialog', (dialog) => dialog.accept())
  return { context, page }
}

async function screenshot(page, name) {
  const file = path.join(OUT, name)
  await page.screenshot({ path: file, fullPage: false })
  ARTIFACTS.push(name)
  return file
}

// noVNC can log one transient close while the desktop container finishes
// starting; the component reconnects and the connected-state check below is the
// authoritative signal.
const IGNORED_CONSOLE = [
  /Failed when connecting: Connection closed.*RangeBox not ready/i,
]
function isRelevantConsoleError(text) {
  return !IGNORED_CONSOLE.some((pattern) => pattern.test(text))
}

function hasOverflow(page) {
  return page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth > 1)
}

async function openTrack(page) {
  await page.goto(`${BASE}/exercises/${TRACK}`, { waitUntil: 'networkidle', timeout: 60000 })
  await page.locator('.lab-row').first().waitFor({ state: 'visible', timeout: 30000 })
  await page.waitForTimeout(600)
}

async function labRow(page) {
  const row = page.locator('.lab-row', { hasText: LAB_NAME }).first()
  if ((await row.count()) === 0) throw new Error(`Lab row not found: ${LAB_NAME}`)
  return row
}

async function launchLab(page) {
  // A previous run may have left the test account's lab running. Reuse an
  // already-rendered workspace instead of clicking through the lab list.
  if (await page.locator('.active-lab-panel--workspace').count()) {
    await page.locator('.panel-section--rangebox').waitFor({ state: 'visible', timeout: 30000 })
    await page.waitForTimeout(1000)
    return
  }
  // A VPN-only or stale session still blocks the row; close it first and wait
  // for the background cleanup before starting a new environment.
  if (await page.locator('.active-lab-panel').count()) {
    await stopLab(page, 'pre-cleanup')
    await page.waitForTimeout(3000)
    await page.reload({ waitUntil: 'networkidle', timeout: 60000 })
    await page.locator('.lab-row').first().waitFor({ state: 'visible', timeout: 30000 })
  }
  const row = await labRow(page)
  const continueButton = row.getByRole('button', { name: 'Continue' })
  if (await continueButton.count()) {
    await continueButton.click()
  } else {
    const launchButton = row.getByRole('button', { name: 'Launch' })
    if ((await launchButton.count()) === 0) {
      throw new Error('The lab is locked or unavailable for this account.')
    }
    await launchButton.click()
  }
  await page.locator('.active-lab-panel').waitFor({ state: 'visible', timeout: 60000 })
  await page.locator('.active-lab-panel--workspace').waitFor({ state: 'visible', timeout: 600000 })
  await page.locator('.panel-section--rangebox').waitFor({ state: 'visible', timeout: 30000 })
  await page.waitForTimeout(1500)
}

async function assertWorkspace(page, role) {
  const workspace = page.locator('.active-lab-panel--workspace')
  check(`${role}: combined workspace visible`, await workspace.isVisible())
  check(`${role}: RangeBox pane visible`, await page.locator('.panel-section--rangebox').isVisible())
  check(`${role}: workbook frame present`, await page.locator('.workspace-workbook iframe').count() === 1)
  check(`${role}: flag input visible`, await page.locator('#lab-flag-input').isVisible())
  check(`${role}: timer visible`, await page.locator('.active-lab-panel__timer').isVisible())

  const iframeSrc = await page.locator('.workspace-workbook iframe').getAttribute('src')
  check(`${role}: workbook URL resolved`, Boolean(iframeSrc && iframeSrc.includes('/wiki/')), iframeSrc || 'missing')

  check(`${role}: Expand control present`, await page.getByRole('button', { name: 'Expand', exact: true }).count() === 1)
  check(`${role}: Open RangeBox in new tab present`, await page.getByRole('button', { name: 'Open in new tab' }).count() >= 1)
  check(`${role}: Stop Exercise present`, await page.getByRole('button', { name: 'Stop Exercise' }).count() === 1)
  check(`${role}: no horizontal overflow at desktop width`, !(await hasOverflow(page)))

  // The VNC connection should reach the connected state, not stay on Connecting.
  const connected = page.locator('.rangebox__status--connected')
  if ((await connected.count()) === 0) {
    await connected.waitFor({ state: 'visible', timeout: 45000 }).catch(() => {})
  }
  check(`${role}: RangeBox VNC connected`, await connected.count() > 0)

  await screenshot(page, `workspace-${role}-dark.png`)
}

async function exerciseControls(page, role) {
  // Expand and restore the workbook pane.
  await page.getByRole('button', { name: 'Expand', exact: true }).click()
  await page.locator('.active-lab-grid--workbook-expanded').waitFor({ state: 'visible', timeout: 5000 })
  check(`${role}: workbook Expand works`, await page.locator('.active-lab-grid--workbook-expanded').isVisible())
  await page.getByRole('button', { name: 'Restore', exact: true }).click()
  check(`${role}: workbook Restore works`, (await page.locator('.active-lab-grid--workbook-expanded').count()) === 0)

  // Open the RangeBox in a new tab and confirm the session query is present.
  const [rangeboxTab] = await Promise.all([
    page.context().waitForEvent('page'),
    page.locator('.panel-section--rangebox').getByRole('button', { name: 'Open in new tab' }).click(),
  ])
  await rangeboxTab.waitForLoadState('domcontentloaded').catch(() => {})
  check(`${role}: Open RangeBox new tab`, /\/rangebox\?.*session=/.test(rangeboxTab.url()), rangeboxTab.url())
  await rangeboxTab.close()

  // Open the workbook in a new tab.
  const [workbookTab] = await Promise.all([
    page.context().waitForEvent('page'),
    page.locator('.panel-section--workbook').getByRole('button', { name: 'Open in new tab' }).click(),
  ])
  await workbookTab.waitForLoadState('domcontentloaded').catch(() => {})
  check(`${role}: Open workbook new tab`, workbookTab.url().includes('/wiki/'), workbookTab.url())
  await workbookTab.close()

  // A wrong flag must produce an error, not a completion.
  await page.locator('#lab-flag-input').fill('OCR{workspace_regression_invalid}')
  await page.getByRole('button', { name: 'Submit', exact: true }).click()
  await page.locator('.flag-message--error').waitFor({ state: 'visible', timeout: 20000 }).catch(() => {})
  check(`${role}: invalid flag shows an error`, await page.locator('.flag-message--error').count() > 0)
}

async function requestHint(page, role) {
  const button = page.getByRole('button', { name: /Request Hint/i })
  if ((await button.count()) === 0) {
    check(`${role}: hint control present`, false, 'No Request Hint button')
    return
  }
  await button.first().click()
  const hint = page.locator('.hint-box').first()
  await hint.waitFor({ state: 'visible', timeout: 20000 }).catch(() => {})
  check(`${role}: Request Hint returns a hint`, await hint.count() > 0)
}

async function stopLab(page, role) {
  if (process.env.UI_KEEP_SESSION === '1') return
  const stop = page.getByRole('button', { name: 'Stop Exercise' })
  if ((await stop.count()) === 0) return
  await stop.click()
  await page.locator('.active-lab-panel').waitFor({ state: 'detached', timeout: 30000 }).catch(() => {})
  check(`${role}: Stop Exercise closes the panel`, (await page.locator('.active-lab-panel').count()) === 0)
}

async function studentWalkthrough() {
  const session = await loginAs(STUDENT_USER, STUDENT_PASS)
  if (!session) {
    check('student login', false, 'Dedicated test student account was rejected')
    return
  }
  check('student login', true, session.user.role)

  const { context, page } = await contextFor({ width: 1440, height: 1000 }, session)
  try {
    await openTrack(page)
    await launchLab(page)
    await assertWorkspace(page, 'student')

    // Light theme screenshot and contrast check.
    const beforeTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'))
    await page.locator('.theme-toggle:visible').first().click()
    await page.waitForTimeout(400)
    const afterTheme = await page.evaluate(() => document.documentElement.getAttribute('data-theme'))
    await screenshot(page, 'workspace-student-light.png')
    check('student: theme toggle changes theme', Boolean(afterTheme) && afterTheme !== beforeTheme, `${beforeTheme} -> ${afterTheme}`)

    await exerciseControls(page, 'student')
    await requestHint(page, 'student')

    // Mobile fallback: the workspace must not appear below 768 px.
    const mobile = await contextFor({ width: 390, height: 844 }, session)
    await openTrack(mobile.page)
    const row = await labRow(mobile.page)
    const continueButton = row.getByRole('button', { name: 'Continue' })
    if (await continueButton.count()) await continueButton.click()
    await mobile.page.locator('.active-lab-panel').waitFor({ state: 'visible', timeout: 60000 })
    check('student mobile: workspace disabled', (await mobile.page.locator('.active-lab-panel--workspace').count()) === 0)
    check('student mobile: section jump bar visible', await mobile.page.locator('.active-lab-jump').isVisible())
    check('student mobile: no horizontal overflow', !(await hasOverflow(mobile.page)))
    await screenshot(mobile.page, 'workspace-student-mobile.png')
    await mobile.context.close()
  } finally {
    await stopLab(page, 'student').catch(() => {})
    await context.close()
  }
}

async function instructorWalkthrough() {
  if (process.env.UI_SKIP_INSTRUCTOR === '1') return
  if (!INSTRUCTOR_USER || !INSTRUCTOR_PASS) {
    console.log('Instructor walkthrough skipped: credentials not provided.')
    return
  }
  const session = await loginAs(INSTRUCTOR_USER, INSTRUCTOR_PASS)
  if (!session) {
    check('instructor login', false, 'Dedicated test instructor account was rejected')
    return
  }
  check('instructor login', true, session.user.role)

  const { context, page } = await contextFor({ width: 1440, height: 1000 }, session)
  try {
    await openTrack(page)
    check('instructor: Instructor navigation visible', await page.locator('.nav-section', { hasText: 'Instructor' }).count() > 0)
    await launchLab(page)
    await assertWorkspace(page, 'instructor')
    await exerciseControls(page, 'instructor')
  } finally {
    await stopLab(page, 'instructor').catch(() => {})
    await context.close()
  }
}

try {
  await studentWalkthrough()
  await instructorWalkthrough()
} catch (error) {
  check('walkthrough completed without an uncaught error', false, error.message)
  console.error(error)
} finally {
  check('no page errors', pageErrors.length === 0, pageErrors.slice(0, 3).join(' | '))
  check('no console errors', consoleErrors.length === 0, consoleErrors.slice(0, 3).join(' | '))
  await browser.close()
  const failed = CHECKS.filter((item) => !item.ok)
  const evidence = {
    base: BASE,
    track: TRACK,
    lab: LAB_NAME,
    runAt: new Date().toISOString(),
    checks: CHECKS,
    failed: failed.length,
    artifacts: ARTIFACTS,
    pageErrors,
    consoleErrors,
  }
  fs.writeFileSync(path.join(OUT, 'workspace-regression.json'), JSON.stringify(evidence, null, 2))
  console.log(`\n${CHECKS.length - failed.length} passed, ${failed.length} failed.`)
  console.log(`Evidence: ${path.join(OUT, 'workspace-regression.json')}`)
  process.exit(failed.length ? 1 : 0)
}
