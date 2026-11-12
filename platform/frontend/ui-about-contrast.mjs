import { chromium } from 'playwright'

const BASE = (process.env.UI_BASE_URL || 'http://localhost:4173').replace(/\/$/, '')
const PATH = process.env.UI_ABOUT_PATH || '/about'

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({
  ignoreHTTPSErrors: true,
  viewport: { width: 1280, height: 900 },
})
await context.addInitScript(() => {
  localStorage.setItem('theme', 'dark')
})
const page = await context.newPage()
await page.goto(`${BASE}${PATH}`, { waitUntil: 'networkidle', timeout: 60000 })
const button = page.locator('.public-about__actions .btn--primary').first()
await button.waitFor({ state: 'visible', timeout: 15000 })
const styles = await button.evaluate((node) => {
  const computed = getComputedStyle(node)
  return { color: computed.color, background: computed.backgroundColor, text: node.textContent.trim() }
})
console.log(styles)
const rgb = (value) => value.match(/\d+/g).slice(0, 3).map(Number)
const luminance = ([r, g, b]) => {
  const channels = [r, g, b].map((v) => {
    const s = v / 255
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4)
  })
  return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
}
const fg = luminance(rgb(styles.color))
const bg = luminance(rgb(styles.background))
const contrast = (Math.max(fg, bg) + 0.05) / (Math.min(fg, bg) + 0.05)
console.log('contrast', contrast.toFixed(2))
if (contrast < 4.5) throw new Error(`Button contrast too low: ${contrast.toFixed(2)}`)
await browser.close()
