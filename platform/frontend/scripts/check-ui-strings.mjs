#!/usr/bin/env node
/**
 * Baseline gate for untranslated UI strings.
 *
 * The codebase predates i18n, so the first run records the existing bare
 * strings in Vue templates. CI fails when a file grows beyond its baseline or
 * the total grows. Touching a file is the moment to move its strings into the
 * locale catalogue and lower its baseline.
 *
 * Usage:
 *   node scripts/check-ui-strings.mjs
 *   node scripts/check-ui-strings.mjs --update
 */
import { execFileSync } from 'node:child_process'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const ROOT = dirname(HERE)
const BASELINE = join(HERE, 'ui-string-baseline.json')
const RULE = 'vue/no-bare-strings-in-template'

const raw = execFileSync(
  process.execPath,
  [join(ROOT, 'node_modules', 'eslint', 'bin', 'eslint.js'), 'src', '--format', 'json'],
  { cwd: ROOT, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }
)

const results = JSON.parse(raw)
const files = {}
let total = 0
for (const result of results) {
  const count = (result.messages || []).filter((message) => message.ruleId === RULE).length
  if (!count) continue
  const name = relative(ROOT, result.filePath).split('\\').join('/')
  files[name] = count
  total += count
}

const current = { total, files }

if (process.argv.includes('--update')) {
  writeFileSync(BASELINE, `${JSON.stringify(current, null, 2)}\n`, 'utf8')
  console.log(`Wrote ${BASELINE}: ${total} bare string(s) across ${Object.keys(files).length} file(s).`)
  process.exit(0)
}

if (!existsSync(BASELINE)) {
  console.error(`Missing ${BASELINE}. Run: node scripts/check-ui-strings.mjs --update`)
  process.exit(1)
}

const baseline = JSON.parse(readFileSync(BASELINE, 'utf8'))
const growth = []
for (const [file, count] of Object.entries(files)) {
  const allowed = baseline.files?.[file] || 0
  if (count > allowed) growth.push(`${file}: ${count} > ${allowed}`)
}
for (const [file, allowed] of Object.entries(baseline.files || {})) {
  const count = files[file] || 0
  if (count < allowed) {
    console.log(`  decreased: ${file}: ${count} (baseline ${allowed}) - lower it with --update`)
  }
}

if (total > (baseline.total || 0) || growth.length) {
  console.error('Untranslated UI string budget failed:')
  console.error(`  total: ${total} (baseline ${baseline.total || 0})`)
  for (const line of growth) console.error(`  - ${line}`)
  console.error('Move new text into the locale catalogue or record an explicit baseline update in review.')
  process.exit(1)
}

console.log(
  `Untranslated UI string budget passed: ${total} bare string(s) across ${Object.keys(files).length} file(s).`
)
