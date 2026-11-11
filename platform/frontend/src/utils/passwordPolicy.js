// Client-side mirror of the backend password policy.
//
// The backend remains authoritative. This copy exists so the registration and
// change-password fields can reject the obvious shortcuts before a submit:
// a dictionary word with a digit or symbol appended, an account name, a
// repeated pattern, or a simple sequence.

const COMMON_PASSWORD_BASES = new Set([
  'password', 'passw0rd', 'passwd', 'pass', 'qwerty', 'qwertyuiop',
  'azerty', 'abc123', '123456', '1234567', '12345678', '123456789',
  '1234567890', '111111', '000000', 'letmein', 'welcome', 'admin',
  'administrator', 'root', 'toor', 'login', 'iloveyou', 'monkey',
  'dragon', 'master', 'sunshine', 'princess', 'football', 'baseball',
  'shadow', 'superman', 'batman', 'trustno1', 'starwars', 'whatever',
  'freedom', 'hello', 'secret', 'changeme', 'changeit', 'default',
  'guest', 'user', 'test', 'testing', 'student', 'teacher', 'instructor',
  'school', 'college', 'university', 'cyber', 'security', 'range',
  'rangebox', 'opencyberrange', 'ocr', 'kali', 'ubuntu', 'remnux',
  'linux', 'windows', 'summer', 'winter', 'spring', 'autumn', 'fall',
  'january', 'february', 'march', 'april', 'may', 'june', 'july',
  'august', 'september', 'october', 'november', 'december', 'monday',
  'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
  'northwind', 'swocts', 'academy', 'course', 'lab', 'flag',
])

const SYMBOL_TRANSLATION = { '@': 'a', $: 's', '+': 't' }
const DIGIT_TRANSLATION = {
  0: 'o', 1: 'l', 3: 'e', 4: 'a', 5: 's', 7: 't', 8: 'b',
}
const SEQUENCES = ['0123456789', 'abcdefghijklmnopqrstuvwxyz', 'qwertyuiop', 'asdfghjkl', 'zxcvbnm']

const isAlnum = (ch) => /[\p{L}\p{N}]/u.test(ch)

function translate(value, map) {
  return [...value].map((ch) => map[ch] ?? ch).join('')
}

function normalise(value) {
  return [...value.normalize('NFKC').toLowerCase()].filter(isAlnum).join('')
}

function passwordBase(value) {
  const folded = translate(value.normalize('NFKC').toLowerCase(), SYMBOL_TRANSLATION)
  const alnum = normalise(folded)
  const withoutCounter = alnum.replace(/[0-9]+$/, '')
  return translate(withoutCounter || alnum, DIGIT_TRANSLATION)
}

function hasSequentialRun(value, runLength = 4) {
  if (value.length < runLength) return false
  for (let start = 0; start <= value.length - runLength; start += 1) {
    const chunk = value.slice(start, start + runLength)
    if (![...chunk].every(isAlnum)) continue
    const deltas = []
    for (let i = 0; i < chunk.length - 1; i += 1) {
      deltas.push(chunk.charCodeAt(i + 1) - chunk.charCodeAt(i))
    }
    if (deltas.every((delta) => delta === 1) || deltas.every((delta) => delta === -1)) {
      return true
    }
  }
  for (const sequence of SEQUENCES) {
    for (let start = 0; start <= sequence.length - runLength; start += 1) {
      if (value.includes(sequence.slice(start, start + runLength))) return true
    }
  }
  return false
}

function isRepeatedPattern(value) {
  if (value.length >= 4 && new Set(value).size === 1) return true
  return /^(.+?)\1+$/.test(value)
}

function contextTokens({ username, email, firstName, lastName } = {}) {
  const tokens = new Set()
  for (const value of [username, firstName, lastName]) {
    if (value) tokens.add(String(value).normalize('NFKC').toLowerCase())
  }
  if (email) {
    const local = String(email).split('@')[0].toLowerCase()
    tokens.add(local)
    for (const part of local.split(/[^a-z0-9]+/)) {
      if (part) tokens.add(part)
    }
  }
  return [...tokens].filter((token) => token.length >= 3)
}

function containsContextToken(value, token) {
  const escaped = token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return (
    new RegExp(`^${escaped}[0-9\\W_]*$`).test(value)
    || new RegExp(`^[0-9\\W_]*${escaped}$`).test(value)
    || new RegExp(`(?<![a-z0-9])${escaped}(?![a-z0-9])`).test(value)
  )
}

export function passwordPolicyError(value, context = {}) {
  if (!value) return ''
  const normalised = normalise(value)
  if (COMMON_PASSWORD_BASES.has(passwordBase(value))) {
    return 'Password is too common. Choose a longer phrase that is not a common word, name, or simple pattern.'
  }
  const lowerValue = value.normalize('NFKC').toLowerCase()
  for (const token of contextTokens(context)) {
    if (containsContextToken(lowerValue, token)) {
      return 'Password must not contain your username, email, or name.'
    }
  }
  if (isRepeatedPattern(normalised.replace(/[0-9]+$/, ''))) {
    return 'Password must not repeat the same character or pattern.'
  }
  if (hasSequentialRun(normalised)) {
    return 'Password must not contain a simple sequence such as 1234, abcd, or qwerty.'
  }
  return ''
}
