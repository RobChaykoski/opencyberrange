/**
 * Ask for the compliance reason before a report or data export.
 *
 * The backend records the reason in the audit log. Callers should stop when
 * this returns null so an export cannot be produced without a purpose.
 */
export function requireExportReason(
  promptText = 'Why is this report being exported?',
  minimumLength = 5
) {
  const entered = window.prompt(
    `${promptText}\n\n` +
    `A reason of at least ${minimumLength} characters is required and is ` +
    'recorded in the audit log.'
  )
  const reason = (entered || '').trim()
  return reason.length >= minimumLength ? reason : null
}
