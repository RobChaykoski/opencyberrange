#!/usr/bin/env node
/**
 * Guard the frontend chunks against monolith creep.
 *
 * The admin, instructor, and lab routes are the expensive ones. A route chunk
 * above the threshold is a signal to split a tab or move a heavy dependency
 * behind defineAsyncComponent; it is not a reason to raise the limit silently.
 */
import { readdirSync, statSync } from 'node:fs'
import { join } from 'node:path'

const DIST = 'dist/assets'
const MAX_CHUNK_KB = 600
const MAX_ENTRY_KB = 200

const files = readdirSync(DIST)
  .filter((name) => name.endsWith('.js'))
  .map((name) => ({
    name,
    kb: Math.round(statSync(join(DIST, name)).size / 1024),
  }))
  .sort((a, b) => b.kb - a.kb)

if (!files.length) {
  console.error(`No built JavaScript found in ${DIST}. Run npm run build first.`)
  process.exit(1)
}

console.log('Largest JavaScript chunks:')
for (const file of files.slice(0, 8)) {
  console.log(`  ${String(file.kb).padStart(5)} KB  ${file.name}`)
}

const failures = []
for (const file of files) {
  if (file.kb > MAX_CHUNK_KB) {
    failures.push(`${file.name} is ${file.kb} KB (limit ${MAX_CHUNK_KB} KB)`)
  }
}
const entry = files.find((file) => /^index-.*\.js$/.test(file.name))
if (entry && entry.kb > MAX_ENTRY_KB) {
  failures.push(`${entry.name} is ${entry.kb} KB (entry limit ${MAX_ENTRY_KB} KB)`)
}

if (failures.length) {
  console.error('\nBundle budget failed:')
  for (const failure of failures) console.error(`  - ${failure}`)
  console.error(
    '\nSplit the route with defineAsyncComponent or move the dependency behind a dynamic import.'
  )
  process.exit(1)
}

console.log(
  `\nBundle budget passed: max ${MAX_CHUNK_KB} KB per chunk, ${MAX_ENTRY_KB} KB entry.`
)
