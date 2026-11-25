/**
 * Capture and refresh the SWOCTS Cyber Range user-manual screenshots.
 *
 * Usage:
 *   UI_BASE_URL=https://172.16.16.44 \
 *   UI_STUDENT_USERNAME=... UI_STUDENT_PASSWORD=... \
 *   UI_INSTRUCTOR_USERNAME=... UI_INSTRUCTOR_PASSWORD=... \
 *   UI_ADMIN_USERNAME=... UI_ADMIN_PASSWORD=... \
 *   node scripts/ui-manual-screenshots.mjs
 *
 * Optional:
 *   UI_MANUAL_ACTIVE_LAB=1     spawn linux-1-1 and capture the active-lab
 *                              shots, then stop the session
 *   UI_MANUAL_STUDENT_IMAGE=... override the student/desktop screenshot to use
 *   UI_MANUAL_SKIP_ADMIN=1      skip admin captures (no admin credentials)
 *
 * Prerequisites for the admin screenshots:
 *   - at least one pending account (Users > Pending)
 *   - at least one locked account
 * The script does not create accounts. If a capture target is missing it logs
 * SKIP and leaves the existing image in place.
 *
 * The script signs in through the API, sets the browser token in
 * localStorage, sets Privacy Mode (off by default; keep it on with
 * UI_MANUAL_PRIVACY=1 when the host mirrors production users), and writes PNGs
 * under Manual-Lite/**. It performs GETs plus, when UI_MANUAL_ACTIVE_LAB=1, one
 * lab spawn and stop.
 *
 * Requires Playwright: npx playwright install chromium
 */
import fs from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'

// The repository root has no node_modules; Playwright is installed with the
// frontend. Resolve it from that package so the documented root-level command
// works without NODE_PATH or a second install.
const require = createRequire(
  new URL('../platform/frontend/package.json', import.meta.url),
)
const { chromium, request } = require('playwright')

const BASE = (process.env.UI_BASE_URL || '').replace(/\/$/, '')
const ROOT = process.cwd()
const ACTIVE_LAB = process.env.UI_MANUAL_ACTIVE_LAB === '1'
const SKIP_ADMIN = process.env.UI_MANUAL_SKIP_ADMIN === '1'
// Keep Privacy Mode on when the target database may contain real users. Use
// this for any shared development host that mirrors production accounts.
const KEEP_PRIVACY = process.env.UI_MANUAL_PRIVACY === '1'

const IMG = {
  start: path.join(ROOT, 'Manual-Lite', '01_Getting_Started', 'img'),
  student: path.join(ROOT, 'Manual-Lite', '02_Student_Guide', 'img'),
  instructor: path.join(ROOT, 'Manual-Lite', '03_Instructor_Guide', 'img'),
  admin: path.join(ROOT, 'Manual-Lite', '04_Admin_Guide', 'img'),
  vpn: path.join(ROOT, 'Manual-Lite', '05_VPN_Setup_Guide', 'img'),
  workflow: path.join(ROOT, 'Manual-Lite', '06_Lab_Workflow_Reference', 'img'),
  trouble: path.join(ROOT, 'Manual-Lite', '07_Troubleshooting', 'img'),
  deploy: path.join(ROOT, 'Manual-Lite', '00_Server_Deployment', 'img'),
}

const CREDS = {
  student: {
    username: process.env.UI_STUDENT_USERNAME || process.env.UI_SMOKE_USERNAME || '',
    password: process.env.UI_STUDENT_PASSWORD || process.env.UI_SMOKE_PASSWORD || '',
  },
  instructor: {
    username: process.env.UI_INSTRUCTOR_USERNAME || '',
    password: process.env.UI_INSTRUCTOR_PASSWORD || '',
  },
  admin: {
    username: process.env.UI_ADMIN_USERNAME || '',
    password: process.env.UI_ADMIN_PASSWORD || '',
  },
}

if (!BASE) {
  console.log('Manual screenshots skipped: UI_BASE_URL is required.')
  process.exit(0)
}

const report = []
const browser = await chromium.launch({ headless: true })

async function login(role) {
  const { username, password } = CREDS[role]
  if (!username || !password) return null
  const api = await request.newContext({ baseURL: BASE, ignoreHTTPSErrors: true })
  try {
    const response = await api.post('/api/auth/login', { form: { username, password } })
    if (!response.ok()) {
      console.error(`login failed for ${role} (${response.status()})`)
      return null
    }
    const body = await response.json()
    const me = await api.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${body.access_token}` },
    })
    return { token: body.access_token, user: me.ok() ? await me.json() : {} }
  } finally {
    await api.dispose()
  }
}

async function contextFor(session, viewport = { width: 1440, height: 1100 }) {
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport,
    deviceScaleFactor: 2,
  })
  if (session) {
    await context.addInitScript(
      ({ token, user, keepPrivacy }) => {
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))
        localStorage.setItem('theme', 'dark')
        localStorage.setItem('privacy-mode', keepPrivacy ? 'on' : 'off')
        // Mark the choice explicit so the role default does not override it for
        // instructor captures.
        localStorage.setItem('privacy-mode-explicit', '1')
        localStorage.setItem('ocr_orientation_seen_v1_' + user.username, '1')
      },
      { ...session, keepPrivacy: KEEP_PRIVACY },
    )
  }
  const page = await context.newPage()
  page.setDefaultTimeout(15000)
  page.on('pageerror', (err) => console.error('pageerror:', String(err).split('\n')[0]))
  return { context, page }
}

async function go(page, route, wait = 1300) {
  await page.goto(`${BASE}${route}`, { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(wait)
}

async function shot(page, selector, target, label) {
  try {
    const locator = page.locator(selector).first()
    await locator.waitFor({ state: 'visible', timeout: 12000 })
    await locator.scrollIntoViewIfNeeded()
    await page.waitForTimeout(300)
    await locator.screenshot({ path: target, animations: 'disabled' })
    report.push(`OK ${label}`)
  } catch (err) {
    report.push(`SKIP ${label}: ${String(err).split('\n')[0]}`)
  }
}

async function viewportShot(page, target, label) {
  await page.screenshot({ path: target, animations: 'disabled' })
  report.push(`OK ${label}`)
}

async function closeOverlay(page) {
  const overlay = page.locator('.modal-overlay').first()
  if (await overlay.count()) {
    await overlay.click({ position: { x: 4, y: 4 } }).catch(() => {})
    await page.waitForTimeout(400)
  }
}

for (const dir of Object.values(IMG)) fs.mkdirSync(dir, { recursive: true })

// ---------- Guest pages ----------
{
  const { context, page } = await contextFor(null)
  await go(page, '/login')
  await viewportShot(page, path.join(IMG.start, 'login.png'), 'login')
  await viewportShot(page, path.join(IMG.trouble, 'login-screen.png'), 'login-screen')
  await go(page, '/register')
  await viewportShot(page, path.join(IMG.start, 'register.png'), 'register')
  await context.close()
}

// ---------- Student ----------
const student = await login('student')
if (student) {
  const { context, page } = await contextFor(student)
  await go(page, '/dashboard')
  await viewportShot(page, path.join(IMG.student, 'student-dashboard.png'), 'student dashboard')
  await viewportShot(page, path.join(IMG.start, 'navigation-sidebar.png'), 'navigation sidebar')

  await go(page, '/exercises')
  await viewportShot(page, path.join(IMG.student, 'browsing-exercises.png'), 'browsing exercises')

  await go(page, '/exercises/linux')
  await viewportShot(page, path.join(IMG.student, 'track-detail.png'), 'track detail')
  await viewportShot(page, path.join(IMG.workflow, 'lab-statuses.png'), 'lab statuses')

  await go(page, '/courses')
  await viewportShot(page, path.join(IMG.student, 'course-list.png'), 'course list')
  const courseLink = page.locator('.course-card__action, a[href^="/courses/"]').first()
  if (await courseLink.count()) {
    await courseLink.click()
    await page.waitForTimeout(1400)
    await viewportShot(page, path.join(IMG.student, 'course-labs.png'), 'course overview')
  }

  await go(page, '/vpn-setup')
  await viewportShot(page, path.join(IMG.student, 'vpn-setup.png'), 'vpn setup page')
  await viewportShot(page, path.join(IMG.vpn, 'vpn-overview.png'), 'vpn overview')
  await shot(page, '.vpn-card', path.join(IMG.vpn, 'vpn-download.png'), 'vpn download')
  await shot(page, '.instructions-card', path.join(IMG.vpn, 'vpn-linux.png'), 'vpn instructions')

  await go(page, '/profile')
  await viewportShot(page, path.join(IMG.student, 'profile.png'), 'profile overview')
  const tab = (name) => page.locator('.profile-tab', { hasText: name }).first()
  if (await tab('Cyber DNA').count()) {
    await tab('Cyber DNA').click()
    await page.waitForTimeout(1200)
    await shot(page, '.dna-layout', path.join(IMG.student, 'profile-cyber-dna.png'), 'dna layout')
    await shot(page, '.dna-class-card', path.join(IMG.student, 'profile-dna-class.png'), 'dna class')
    await shot(page, '.dna-tree', path.join(IMG.student, 'profile-dna-tree.png'), 'dna tree')
    await shot(page, '.dna-ce', path.join(IMG.student, 'profile-dna-continuing-education.png'), 'dna continuing education')
    await shot(page, '.momentum', path.join(IMG.student, 'profile-momentum.png'), 'momentum')
  }
  if (await tab('Career GPS').count()) {
    await tab('Career GPS').click()
    await page.waitForTimeout(1200)
    await shot(page, '.gps-panel', path.join(IMG.student, 'profile-cyber-gps.png'), 'career gps')
    await shot(page, '.gps-revisit', path.join(IMG.student, 'profile-cyber-gps-signal.png'), 'fading signal')
    await shot(page, '.atlas', path.join(IMG.student, 'profile-careers.png'), 'career atlas')
  }
  if (await tab('Security & privacy').count()) {
    await tab('Security & privacy').click()
    await page.waitForTimeout(900)
    await shot(page, '.consent-panel', path.join(IMG.student, 'profile-consent.png'), 'consent panel')
  }

  await go(page, '/events')
  await shot(page, '.community-events', path.join(IMG.student, 'community-events-calendar.png'), 'community events')

  await go(page, '/threat-awareness')
  await shot(page, '.threat-map', path.join(IMG.student, 'threat-map.png'), 'threat map')
  await viewportShot(page, path.join(IMG.student, 'threat-map-page.png'), 'threat map page')

  await go(page, '/tools')
  await viewportShot(page, path.join(IMG.student, 'tools-catalogue.png'), 'tools catalogue')

  await go(page, '/change-password')
  await viewportShot(page, path.join(IMG.student, 'change-password.png'), 'change password')

  const mobile = await contextFor(student, { width: 390, height: 844 })
  await go(mobile.page, '/dashboard', 1600)
  await viewportShot(mobile.page, path.join(IMG.student, 'mobile-navigation.png'), 'mobile navigation')
  await mobile.context.close()

  await go(page, '/workbooks')
  const open = page.locator('.wb-card__open').first()
  if (await open.count()) {
    const [reader] = await Promise.all([context.waitForEvent('page'), open.click()])
    await reader.waitForLoadState('networkidle').catch(() => {})
    await reader.waitForTimeout(2000)
    await reader.screenshot({
      path: path.join(IMG.student, 'workbook-reading.png'),
      animations: 'disabled',
    })
    report.push('OK workbook reading')
    await reader.close()
  }

  if (ACTIVE_LAB) {
    const api = await request.newContext({ baseURL: BASE, ignoreHTTPSErrors: true })
    const headers = { Authorization: `Bearer ${student.token}` }
    const spawn = await api.post('/api/labs/spawn/linux-1-1-ssh-service-detection', {
      headers,
      data: { rangebox: false },
    })
    if (spawn.ok()) {
      const { session_id: sessionId } = await spawn.json()
      for (let i = 0; i < 60; i++) {
        const status = await api.get(`/api/labs/spawn-status/${sessionId}`, { headers })
        const data = status.ok() ? await status.json() : {}
        if (['running', 'error', 'failed'].includes(data.status)) break
        await new Promise((resolve) => setTimeout(resolve, 3000))
      }
      await go(page, '/exercises/linux', 1800)
      await shot(page, '.active-lab-panel', path.join(IMG.student, 'working-in-a-lab.png'), 'working in a lab')
      await shot(page, '.active-lab-panel__header', path.join(IMG.student, 'active-lab-extend.png'), 'active lab extend')
      await shot(page, '.active-lab-panel__header', path.join(IMG.student, 'active-lab-stop.png'), 'active lab stop')
      await shot(page, '.flag-panel', path.join(IMG.student, 'submit-flag.png'), 'submit flag')
      const hint = page.getByRole('button', { name: /Need a hint/i }).first()
      if (await hint.count()) {
        await hint.click()
        await page.waitForTimeout(700)
        const requestHint = page.getByRole('button', { name: /Request Hint/i }).first()
        if (await requestHint.count()) {
          await requestHint.click()
          await page.waitForTimeout(1200)
        }
        await shot(
          page,
          '.active-lab-grid .panel-section:has(.section-title:has-text("Hints"))',
          path.join(IMG.student, 'hints.png'),
          'hints'
        )
      }
      await api.post('/api/labs/stop', { headers, data: { session_id: sessionId } })
    } else {
      report.push(`SKIP active lab: spawn returned ${spawn.status()}`)
    }
    await api.dispose()
  }
  await context.close()
} else {
  report.push('SKIP student captures: no student credentials')
}

// ---------- Instructor ----------
const instructor = await login('instructor')
if (instructor) {
  const { context, page } = await contextFor(instructor)
  await go(page, '/instructor', 1700)
  await viewportShot(page, path.join(IMG.instructor, 'instructor-dashboard.png'), 'instructor dashboard')

  await go(page, '/instructor?tab=courses', 1500)
  await viewportShot(page, path.join(IMG.instructor, 'course-card-actions.png'), 'course cards')
  const manage = page.getByRole('button', { name: /Manage/i }).first()
  if (await manage.count()) {
    await manage.click()
    await page.waitForTimeout(1400)
    const files = {
      Students: 'course-students.png',
      'Exercises (': 'course-exercises.png',
      'Exercise plan': 'course-reorder-labs.png',
      Assignments: 'course-assignments.png',
      Reports: 'course-reports.png',
      Settings: 'course-settings.png',
    }
    for (const [name, file] of Object.entries(files)) {
      const btn = page.locator('.sub-tab', { hasText: name }).first()
      if (await btn.count()) {
        await btn.click()
        await page.waitForTimeout(1200)
        await viewportShot(page, path.join(IMG.instructor, file), `course ${name}`)
      } else {
        report.push(`SKIP course tab ${name}`)
      }
    }
  }

  await go(page, '/contract-review', 1800)
  await viewportShot(page, path.join(IMG.instructor, 'contract-review.png'), 'contract review queue')
  const contractItem = page.locator('.contract-review__item').first()
  if (await contractItem.count()) {
    await contractItem.click()
    await page.waitForTimeout(1400)
    await viewportShot(page, path.join(IMG.instructor, 'contract-review-form.png'), 'contract review form')
  } else {
    report.push('SKIP contract review form: no contracts in the queue')
  }

  // Student Preview banner
  await go(page, '/instructor?tab=courses', 1300)
  const preview = page.locator('.action-btn--impersonate').first()
  if (await preview.count()) {
    await preview.click()
    await page.waitForTimeout(2200)
    await shot(page, '.imp-banner', path.join(IMG.admin, 'admin-impersonation.png'), 'student preview banner')
    const exit = page.getByRole('button', { name: /Exit Preview/i }).first()
    if (await exit.count()) {
      await exit.click()
      await page.waitForTimeout(700)
    }
  }
  await context.close()
} else {
  report.push('SKIP instructor captures: no instructor credentials')
}

// ---------- Admin ----------
const admin = SKIP_ADMIN ? null : await login('admin')
if (admin) {
  const { context, page } = await contextFor(admin)
  await go(page, '/admin', 1500)
  await viewportShot(page, path.join(IMG.admin, 'admin-panel-overview.png'), 'admin overview')

  const createUser = page.getByRole('button', { name: /Create New User/i }).first()
  if (await createUser.count()) {
    await createUser.click()
    await page.waitForTimeout(800)
    await shot(page, '.create-form', path.join(IMG.admin, 'admin-create-user.png'), 'create user form')
  }

  await go(page, '/admin?tab=users')
  const pending = page.getByRole('button', { name: /^Pending/ }).first()
  if (await pending.count()) {
    await pending.click()
    await page.waitForTimeout(1100)
    await viewportShot(page, path.join(IMG.admin, 'admin-pending.png'), 'pending approvals')
  }
  // The pending tab replaces the user table, so return to Users before using
  // the status filter for the locked-account capture.
  await go(page, '/admin?tab=users')
  const filter = page.locator('select').filter({ has: page.locator('option[value="locked"]') }).first()
  if (await filter.count()) {
    await filter.selectOption('locked')
    await page.waitForTimeout(1100)
    await viewportShot(page, path.join(IMG.admin, 'admin-locked-users.png'), 'locked users')
  } else {
    report.push('SKIP locked users: status filter not found')
  }

  await go(page, '/admin?tab=labs', 1500)
  await viewportShot(page, path.join(IMG.admin, 'admin-exercises.png'), 'admin exercises')
  const importExercise = page.getByRole('button', { name: /Import Exercise/i }).first()
  if (await importExercise.count()) {
    await importExercise.click()
    await page.waitForTimeout(900)
    await shot(page, '.modal', path.join(IMG.admin, 'admin-import-exercise.png'), 'import exercise')
    await closeOverlay(page)
  }
  const tracks = page.getByRole('button', { name: /Tracks & Levels/i }).first()
  if (await tracks.count()) {
    await tracks.click()
    await page.waitForTimeout(1100)
    await viewportShot(page, path.join(IMG.admin, 'admin-tracks.png'), 'admin tracks')
  }
  await go(page, '/admin?tab=labs', 1300)
  const edit = page.locator('.action-btn--view').first()
  if (await edit.count()) {
    await edit.click()
    await page.waitForTimeout(1200)
    await shot(page, '.modal', path.join(IMG.admin, 'admin-edit-lab.png'), 'edit lab')
    const composeTab = page.locator('.modal button').filter({ hasText: /Compose/i }).first()
    if (await composeTab.count()) {
      await composeTab.click()
      await page.waitForTimeout(800)
      await shot(page, '.modal', path.join(IMG.admin, 'admin-edit-compose.png'), 'edit compose')
    }
    await closeOverlay(page)
  }
  const createLab = page.getByRole('button', { name: /\+ Create Exercise/i }).first()
  if (await createLab.count()) {
    await createLab.click()
    await page.waitForTimeout(1000)
    await shot(page, '.modal', path.join(IMG.admin, 'admin-create-lab.png'), 'create lab')
    await closeOverlay(page)
  }
  const disk = page.getByRole('button', { name: /Disk Management/i }).first()
  if (await disk.count()) {
    await disk.click()
    await page.waitForTimeout(1100)
    await shot(page, '.modal', path.join(IMG.admin, 'admin-disk.png'), 'disk management')
    await closeOverlay(page)
  }

  await go(page, '/admin?tab=monitoring', 1500)
  await viewportShot(page, path.join(IMG.admin, 'admin-monitoring-sessions.png'), 'sessions')
  const vpn = page.getByRole('button', { name: /VPN Peers/ }).first()
  if (await vpn.count()) {
    await vpn.click()
    await page.waitForTimeout(1200)
    await viewportShot(page, path.join(IMG.admin, 'admin-vpn-peers.png'), 'vpn peers')
  }
  const audit = page.getByRole('button', { name: /Activity Log/ }).first()
  if (await audit.count()) {
    await audit.click()
    await page.waitForTimeout(1200)
    const eventSelect = page.locator('select').first()
    const options = await eventSelect.locator('option').allTextContents()
    const loginOption = options.find((value) => /login/i.test(value))
    if (loginOption) {
      await eventSelect.selectOption({ label: loginOption })
      await page.waitForTimeout(1200)
    }
    await viewportShot(page, path.join(IMG.admin, 'admin-activity-log.png'), 'activity log')
  }

  await go(page, '/admin?tab=settings', 1500)
  await viewportShot(page, path.join(IMG.admin, 'admin-settings.png'), 'settings')
  const features = page.getByRole('tab', { name: /^Features/ }).first()
  if (await features.count()) {
    await features.click()
    await page.waitForTimeout(900)
    // Crop to the category tabs and the feature rows so the development-only
    // cutover block above does not dominate a settings figure.
    const categories = page.locator('.settings-categories').first()
    const panel = page.locator('.settings-panel').first()
    await categories.scrollIntoViewIfNeeded()
    await page.waitForTimeout(300)
    const top = await categories.boundingBox()
    const bottom = await panel.boundingBox()
    if (top && bottom) {
      await page.screenshot({
        path: path.join(IMG.admin, 'admin-settings-features.png'),
        animations: 'disabled',
        clip: {
          x: Math.max(0, Math.min(top.x, bottom.x) - 8),
          y: Math.max(0, top.y - 8),
          width: Math.max(top.width, bottom.width) + 16,
          height: bottom.y + bottom.height - top.y + 16,
        },
      })
      report.push('OK features')
    } else {
      report.push('SKIP features: settings regions not visible')
    }
  } else {
    report.push('SKIP features tab: not found')
  }

  await go(page, '/admin?tab=system', 1500)
  await viewportShot(page, path.join(IMG.admin, 'admin-diagnostics.png'), 'system')
  await viewportShot(page, path.join(IMG.deploy, 'post-install-admin.png'), 'post-install admin')
  await context.close()
} else {
  report.push('SKIP admin captures: no admin credentials')
}

await browser.close()
console.log(report.join('\n'))
console.log(`Manual screenshots complete: ${report.filter((line) => line.startsWith('OK')).length} image(s).`)
