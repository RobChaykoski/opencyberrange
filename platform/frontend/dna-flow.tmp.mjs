import { chromium } from 'playwright'

const BASE = 'https://172.16.16.44'
const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1440, height: 1000 } })
const page = await ctx.newPage()

await page.goto(`${BASE}/login`, { waitUntil: 'networkidle' })
await page.getByPlaceholder('Enter your username').fill('qa_dna')
await page.getByPlaceholder('Enter your password').fill('QaCohortProd#2026')
await page.getByRole('button', { name: 'Sign In', exact: true }).last().click()
await page.waitForTimeout(4000)
console.log('after login url', page.url())
await page.screenshot({ path: 'C:/Users/rob/AppData/Local/Temp/opencode/dna-discover.png' })

const investigating = page.getByRole('button', { name: /I like investigating/i }).first()
console.log('interest button', await investigating.count())
if (await investigating.count()) {
  await investigating.click()
  await page.waitForTimeout(1800)
  console.log('after choose url', page.url())
  await page.screenshot({ path: 'C:/Users/rob/AppData/Local/Temp/opencode/dna-path.png' })
}

await page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle' })
await page.waitForTimeout(2000)
console.log('dashboard url', page.url())
const band = await page.locator('.dna-band').count()
console.log('dna band', band)
if (band) {
  console.log((await page.locator('.dna-band').innerText()).slice(0, 500))
  await page.locator('.dna-band').screenshot({ path: 'C:/Users/rob/AppData/Local/Temp/opencode/dna-band.png' })
}
await browser.close()
