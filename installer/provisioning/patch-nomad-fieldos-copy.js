#!/usr/bin/env node
'use strict'

// Keep FieldOS descriptions truthful for the archives actually installed.
// This intentionally targets the pinned N.O.M.A.D. frontend bundle and fails
// closed if upstream changes the expected copy or bundles it more than once.
const fs = require('node:fs')
const path = require('node:path')

const assetsRoot = process.argv[2] || '/app/public/assets'
const replacements = [
  [
    'const ge={label:"Maps",to:"/maps",target:"",description:"View offline maps"',
    'const ge={label:"Maps",to:"/maps?lat=35.86&lng=-86.35&zoom=7",target:"",description:"View offline maps"',
  ],
  [
    'Offline access to Wikipedia, medical references, how-to guides, and encyclopedias',
    'Search installed offline archives. Coverage depends on the content packs installed on this system.',
  ],
  ['Complete Wikipedia offline', 'Search the offline archives installed on this system'],
  [
    'Medical references and first aid guides',
    'Medical and first-aid coverage depends on installed archives; check sources',
  ],
  ['DIY repair guides and how-to content', 'Repair and how-to coverage depends on installed archives'],
  ['Project Gutenberg books and literature', 'Literature coverage depends on installed archives'],
]

function jsFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const filename = path.join(directory, entry.name)
    return entry.isDirectory() ? jsFiles(filename) : entry.isFile() && entry.name.endsWith('.js') ? [filename] : []
  })
}

let patched = 0
let alreadyPatched = 0
for (const filename of jsFiles(assetsRoot)) {
  let source = fs.readFileSync(filename, 'utf8')
  let changed = false
  for (const [before, after] of replacements) {
    const occurrences = source.split(before).length - 1
    if (occurrences === 0) {
      if (source.includes(after)) {
        alreadyPatched += 1
        continue
      }
      continue
    }
    if (occurrences !== 1) {
      throw new Error(`${path.basename(filename)} contains ${occurrences} instances of expected N.O.M.A.D. copy`)
    }
    source = source.replace(before, after)
    changed = true
    patched += 1
  }
  if (changed) {
    const mode = fs.statSync(filename).mode & 0o777
    const temporary = `${filename}.fieldos-tmp`
    fs.writeFileSync(temporary, source, { mode })
    fs.renameSync(temporary, filename)
  }
}

if (patched + alreadyPatched !== replacements.length) {
  throw new Error(
    `Expected ${replacements.length} pinned UI strings; patched=${patched}, already=${alreadyPatched}. ` +
      'The N.O.M.A.D. bundle may have changed; review before updating this patch.',
  )
}
console.log(`FieldOS N.O.M.A.D. content copy: ${patched ? `patched ${patched}` : 'already patched'} strings.`)
