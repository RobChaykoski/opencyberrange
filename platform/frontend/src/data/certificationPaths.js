// Vendor certification guidance for OpenCyberRange tracks.
//
// This is a curated summary, not an official mapping. Certifications and their
// requirements change; verify them with the vendor. The full roadmap is Paul
// Jerimy's Security Certification Roadmap, linked below with attribution.
export const CERTIFICATION_ROADMAP_URL =
  'https://pauljerimy.com/security-certification-roadmap/'
export const CISO_MINDMAP_URL =
  'https://rafeeqrehman.com/wp-content/uploads/2026/04/CISO-MindMap-2026.pdf'
export const SWOCTS_RESOURCES_URL = 'https://swocts.com/resources'

const GENERAL_ENTRY = {
  entry: ['CompTIA Security+', 'ISC2 Certified in Cybersecurity (CC)'],
  core: ['CompTIA CySA+', 'Microsoft SC-200', 'Cisco CyberOps Associate'],
  advanced: ['ISC2 CISSP', 'CompTIA SecurityX (CASP+)'],
}

export const CERTIFICATION_PATHS = {
  network: {
    summary: 'Network defence, traffic analysis, and security operations.',
    entry: ['CompTIA Network+', 'Cisco CCNA'],
    core: ['CompTIA Security+', 'Cisco CyberOps Associate', 'GIAC GCIA'],
    advanced: ['Cisco CCNP Security', 'GIAC GCED', 'ISC2 CISSP'],
    roles: ['SOC analyst', 'Network security analyst', 'Security operations engineer'],
  },
  web: {
    summary: 'Web application testing, secure development, and AppSec.',
    entry: ['eJPT', 'CompTIA Security+'],
    core: ['CompTIA PenTest+', 'PortSwigger BSCP', 'OSWA'],
    advanced: ['OSWE', 'GIAC GWAPT', 'ISC2 CSSLP'],
    roles: ['Application security analyst', 'Penetration tester', 'Secure code reviewer'],
  },
  windows: {
    summary: 'Windows administration, Active Directory, and enterprise defence.',
    entry: ['CompTIA Security+', 'Microsoft SC-900'],
    core: ['Microsoft SC-200', 'CompTIA CySA+', 'GIAC GCIH'],
    advanced: ['OSCP', 'GIAC GCWN', 'Microsoft SC-100'],
    roles: ['SOC analyst', 'Windows security administrator', 'Red team operator'],
  },
  linux: {
    summary: 'Linux administration, hardening, and offensive tradecraft.',
    entry: ['CompTIA Linux+', 'Linux Foundation LFCS'],
    core: ['CompTIA Security+', 'OSCP'],
    advanced: ['Linux Foundation LFCE', 'GIAC GPEN', 'Red Hat RHCE'],
    roles: ['Linux administrator', 'Penetration tester', 'Platform security engineer'],
  },
  osint: {
    summary: 'Open-source research, threat intelligence, and investigations.',
    entry: ['CompTIA Security+', 'OSINT fundamentals training'],
    core: ['GIAC GOSI', 'GIAC GCTI', 'Intel Techniques OSINT'],
    advanced: ['GIAC GASF', 'CREST threat intelligence certifications'],
    roles: ['OSINT analyst', 'Threat intelligence analyst', 'Investigator'],
  },
  forensics: {
    summary: 'Digital forensics, incident response, and evidence handling.',
    entry: ['CompTIA Security+', 'CompTIA CySA+'],
    core: ['GIAC GCFE', 'GIAC GCFA', 'IACIS CFCE'],
    advanced: ['GIAC GNFA', 'GIAC GIME', 'IACIS CAWFE'],
    roles: ['DFIR analyst', 'Forensic examiner', 'Incident responder'],
  },
  malware: {
    summary: 'Malware analysis, reverse engineering, and threat research.',
    entry: ['CompTIA Security+', 'CompTIA CySA+'],
    core: ['GIAC GREM', 'GIAC GCIH'],
    advanced: ['GIAC GXPN', 'OSED', 'GIAC GIME'],
    roles: ['Malware analyst', 'Reverse engineer', 'Threat researcher'],
  },
  ot: {
    summary: 'Industrial control systems, OT security, and critical infrastructure.',
    entry: ['CompTIA Security+', 'Cisco CyberOps Associate'],
    core: ['GIAC GICSP', 'ISA/IEC 62443 certificate program'],
    advanced: ['GIAC GRID', 'GIAC GCIP'],
    roles: ['OT security analyst', 'ICS security engineer', 'Critical infrastructure defender'],
  },
  ai: {
    summary: 'AI security, governance, and secure use of machine learning.',
    entry: ['CompTIA Security+', 'ISO/IEC 42001 foundation training'],
    core: ['IAPP AIGP', 'GIAC GMLE', 'Cloud AI security specialty'],
    advanced: ['Vendor AI security architect certifications', 'GIAC GSE'],
    roles: ['AI security analyst', 'ML security engineer', 'AI governance lead'],
  },
  'software-security': {
    summary: 'Secure software design, review, and supply-chain assurance.',
    entry: ['CompTIA Security+', 'CertNexus Cyber Secure Coder'],
    core: ['ISC2 CSSLP', 'PortSwigger BSCP'],
    advanced: ['OSWE', 'GIAC GWEB', 'ISACA CISA'],
    roles: ['AppSec engineer', 'Secure SDLC lead', 'Software assurance auditor'],
  },
  'high-school': {
    summary: 'Entry-level cybersecurity foundations and career exploration.',
    entry: ['CompTIA ITF+', 'CompTIA Security+'],
    core: ['ISC2 CC', 'Cisco CyberOps Associate'],
    advanced: ['CompTIA CySA+', 'CompTIA PenTest+'],
    roles: ['IT support', 'SOC analyst (entry)', 'Cybersecurity apprentice'],
  },
}

export const DEFAULT_CERTIFICATION_PATH = {
  summary: 'General cybersecurity foundations with a route into defence or offensive security.',
  ...GENERAL_ENTRY,
  roles: ['SOC analyst', 'Security administrator', 'Security engineer'],
}

export function getCertificationPath(track) {
  const slug = String(track?.slug || '').toLowerCase()
  const name = String(track?.name || '').toLowerCase()
  const direct = CERTIFICATION_PATHS[slug]
  if (direct) return direct

  const aliases = [
    ['software-security', ['software', 'appsec', 'application security']],
    ['network', ['network', 'networking']],
    ['windows', ['windows', 'active directory']],
    ['linux', ['linux', 'unix']],
    ['osint', ['osint', 'open source', 'intelligence']],
    ['forensics', ['forensic', 'dfir']],
    ['malware', ['malware', 'reverse']],
    ['ot', ['ot ', 'ics', 'industrial']],
    ['ai', [' ai', 'artificial intelligence', 'machine learning']],
    ['web', ['web']],
    ['high-school', ['high school', 'foundation']],
  ]

  for (const [key, needles] of aliases) {
    if (needles.some((needle) => name.includes(needle))) {
      return CERTIFICATION_PATHS[key]
    }
  }

  return DEFAULT_CERTIFICATION_PATH
}
