import { wikiUrl } from './wikiUrl'

// Resolve a lab's workbook field to the wiki URL the learner can open.
//
// A namespaced value (wiki/range/... or wiki/course/...) resolves on its own.
// A bare path belongs to the active course workbook, so it only resolves when
// the caller has the course wiki slug. In that case returning an empty string
// is deliberate: the UI says the workbook is only available from the course
// instead of rendering a button that silently does nothing.
export function resolveWorkbookUrl(workbook, wikiSlug) {
  if (!workbook || typeof workbook !== 'string') return ''
  if (workbook.startsWith('wiki/range/') || workbook.startsWith('wiki/course/')) {
    return wikiUrl('/' + workbook)
  }
  if (wikiSlug) {
    return wikiUrl('/wiki/course/' + wikiSlug + '/' + workbook)
  }
  return ''
}
