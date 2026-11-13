import { chromium, request } from 'playwright'

const BASE = (process.env.UI_BASE_URL || 'https://172.16.16.41').replace(/\/$/, '')
const TOKEN = process.env.UI_TOKEN || ''
if (!TOKEN) throw new Error('UI_TOKEN is required')

const api = await request.newContext({
  baseURL: BASE,
  ignoreHTTPSErrors: true,
  extraHTTPHeaders: { Authorization: `Bearer ${TOKEN}` },
})
const me = await api.get('/api/auth/me')
if (!me.ok()) throw new Error(`token rejected: ${me.status()}`)
const user = await me.json()
await api.dispose()

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1440, height: 1100 } })
await context.addInitScript(({ token, user }) => {
  localStorage.setItem('token', token)
  localStorage.setItem('user', JSON.stringify(user))
  localStorage.setItem('theme', 'dark')
  localStorage.setItem('ocr_orientation_seen_v1_' + user.username, '1')
}, { token: TOKEN, user })

const page = await context.newPage()
await page.goto(`${BASE}/events`, { waitUntil: 'networkidle', timeout: 60000 })
await page.locator('.community-events').first().waitFor({ state: 'visible', timeout: 30000 })
const title = await page.locator('#community-events-title').innerText()
const calendar = await page.locator('.calendar').count()
const events = await page.locator('.community-event').count()
const sources = await page.locator('.community-source').count()
const dots = await page.locator('.calendar-day__dot--community').count()
const links = await page.locator('.community-source a').evaluateAll((nodes) => nodes.map((node) => node.href))
console.log({ title, calendar, events, sources, dots })
console.log(links)
if (!calendar || !events || sources < 2) throw new Error('community calendar did not render')
if (!links.some((href) => href.includes('swocts.com/events'))) throw new Error('SWOCTS source missing')
if (!links.some((href) => href.includes('eventbrite.ca/o/cyber-hive-yxu'))) throw new Error('Cyber Hive source missing')
const screenshot = process.env.UI_EVENTS_SCREENSHOT
if (screenshot) {
  await page.locator('.community-events').first().screenshot({ path: screenshot, animations: 'disabled' })
  console.log('screenshot', screenshot)
}
console.log('events calendar OK')
await context.close()
await browser.close()
