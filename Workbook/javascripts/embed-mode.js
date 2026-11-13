/* Mark the page as embedded without touching the parent document. */
(function () {
  function mark() {
    document.documentElement.classList.add('ocr-embed');
  }
  try {
    if (window.self !== window.top) {
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', mark, { once: true });
      } else {
        mark();
      }
    }
  } catch (error) {
    // A cross-origin parent still means this page is framed.
    mark();
  }
})();
