/*
 * Page export menu for the workbook and user-manual MkDocs sites.
 *
 * The old control was a single "Save as PDF" button. It is now an accessible
 * export menu with PDF, print, Word, HTML, and copy-link actions. The menu is
 * inserted after the page title, follows Material's instant navigation, and
 * keeps every action client-side: no page content leaves the browser.
 */
(function () {
  'use strict';

  var EXPORT_CONTAINER = 'ocr-export';

  var ICONS = {
    download:
      '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></svg>',
    pdf:
      '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8"/><path d="M8 17h5"/></svg>',
    print:
      '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9V2h12v7"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 14h12v8H6z"/></svg>',
    word:
      '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="m8 12 2 7 2-5 2 5 2-7"/></svg>',
    html:
      '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m8 8-4 4 4 4"/><path d="m16 8 4 4-4 4"/><path d="m13 5-2 14"/></svg>',
    link:
      '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
    chevron:
      '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
    spinner:
      '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" class="ocr-export__spin" aria-hidden="true"><path d="M21 12a9 9 0 1 1-9-9"/></svg>',
    check:
      '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m20 6-11 11-5-5"/></svg>',
  };

  function pageContent() {
    return document.querySelector('.md-content__inner');
  }

  var PDF_SCRIPT = 'javascripts/html2pdf.bundle.min.js';
  var pdfLibraryPromise = null;

  function pdfScriptUrl() {
    var script = document.querySelector('script[src*="pdf-export.js"]');
    if (!script) return PDF_SCRIPT;
    try {
      var url = new URL(script.getAttribute('src'), window.location.href);
      return url.pathname.replace(/pdf-export\.js$/, 'html2pdf.bundle.min.js') + '?v=1';
    } catch (error) {
      return PDF_SCRIPT;
    }
  }

  /* html2pdf is ~900 KB. Load it only when the reader asks for a PDF, not on
     every page of the manual. */
  function ensurePdfLibrary() {
    if (typeof html2pdf !== 'undefined') return Promise.resolve();
    if (pdfLibraryPromise) return pdfLibraryPromise;

    pdfLibraryPromise = new Promise(function (resolve, reject) {
      var script = document.createElement('script');
      script.src = pdfScriptUrl();
      script.async = true;
      script.onload = function () {
        if (typeof html2pdf !== 'undefined') {
          resolve();
        } else {
          pdfLibraryPromise = null;
          reject(new Error('PDF library did not initialise.'));
        }
      };
      script.onerror = function () {
        pdfLibraryPromise = null;
        reject(new Error('PDF library could not be loaded.'));
      };
      document.head.appendChild(script);
    });
    return pdfLibraryPromise;
  }

  function pageTitle() {
    var heading = document.querySelector('.md-content h1');
    var text = (heading && heading.textContent ? heading.textContent : document.title || 'document')
      .replace(/\s+/g, ' ')
      .trim();
    return text || 'document';
  }

  function safeFilename(value) {
    return String(value || 'document')
      .replace(/[^\w\s.-]/g, '')
      .replace(/\s+/g, '_')
      .replace(/_+/g, '_')
      .slice(0, 120) || 'document';
  }

  function currentUrl() {
    return window.location.href.split('#')[0];
  }

  function absolutize(root) {
    var url;
    root.querySelectorAll('img[src], video[poster], source[src]').forEach(function (node) {
      var attr = node.hasAttribute('poster') ? 'poster' : 'src';
      try {
        url = new URL(node.getAttribute(attr), window.location.href);
        node.setAttribute(attr, url.href);
      } catch (error) {
        /* Leave malformed or data URLs untouched. */
      }
    });
    root.querySelectorAll('a[href]').forEach(function (node) {
      var href = node.getAttribute('href') || '';
      if (!href || href.charAt(0) === '#' || /^(mailto:|tel:|data:|javascript:)/i.test(href)) return;
      try {
        url = new URL(href, window.location.href);
        node.setAttribute('href', url.href);
      } catch (error) {
        /* Leave malformed URLs untouched. */
      }
    });
  }

  function buildClone() {
    var content = pageContent();
    if (!content) return null;

    var clone = content.cloneNode(true);
    clone.querySelectorAll('.' + EXPORT_CONTAINER + ', .md-source, script').forEach(function (node) {
      node.remove();
    });
    clone.querySelectorAll('[hidden]').forEach(function (node) {
      node.removeAttribute('hidden');
    });
    absolutize(clone);

    clone.style.color = '#1a1a1a';
    clone.style.background = '#fff';
    clone.querySelectorAll('pre, code').forEach(function (node) {
      node.style.color = '#1a1a1a';
      node.style.background = '#f5f5f5';
      node.style.whiteSpace = 'pre-wrap';
      node.style.wordBreak = 'break-word';
    });

    var footer = document.createElement('div');
    footer.className = 'ocr-export-footer';
    footer.style.cssText =
      'margin-top:2.5em;padding-top:0.8em;border-top:1px solid #d7dde8;' +
      'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;' +
      'font-size:9pt;line-height:1.5;color:#64748b;';
    // security-delta: allow innerHTML - every dynamic value is escaped above
    footer.innerHTML =
      '<strong style="display:block;color:#0f172a;">' + escapeHtml(pageTitle()) + '</strong>' +
      '<span>SWOCTS Cyber Range · exported ' + escapeHtml(new Date().toLocaleDateString()) + '</span><br>' +
      '<span style="word-break:break-all;">' + escapeHtml(currentUrl()) + '</span>';
    clone.appendChild(footer);
    return clone;
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function standaloneStyles() {
    return [
      ':root{color-scheme:light;}',
      'body{margin:0;background:#eef2f7;color:#1a1a1a;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.65;}',
      'article{max-width:52rem;margin:2rem auto;padding:2.5rem 3rem;background:#fff;border-radius:10px;box-shadow:0 18px 50px rgba(15,23,42,.12);}',
      'h1,h2,h3,h4{color:#0f172a;line-height:1.25;}',
      'h1{font-size:1.9rem;margin:0 0 1rem;}',
      'h2{margin-top:2rem;padding-bottom:.35rem;border-bottom:1px solid #e2e8f0;}',
      'a{color:#0369a1;}',
      'img,video,svg{max-width:100%;height:auto;}',
      'pre{overflow-x:auto;padding:.9rem 1rem;border:1px solid #dbe3ee;border-radius:6px;background:#f8fafc;}',
      'code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.88em;}',
      'table{width:100%;border-collapse:collapse;margin:1rem 0;}',
      'th,td{border:1px solid #dbe3ee;padding:.45rem .6rem;text-align:left;}',
      'th{background:#f1f5f9;}',
      'blockquote{border-left:3px solid #38bdf8;margin-left:0;padding-left:1rem;color:#475569;}',
      '.admonition{border:1px solid #dbe3ee;border-left:4px solid #38bdf8;border-radius:6px;padding:.75rem 1rem;margin:1rem 0;background:#f8fafc;}',
      '@media print{body{background:#fff;}article{max-width:none;margin:0;padding:0;box-shadow:none;}}',
      '@media (max-width:640px){article{margin:0;padding:1.25rem;border-radius:0;}}',
    ].join('\n');
  }

  function downloadBlob(blob, filename) {
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function showToast(message, tone) {
    var previous = document.querySelector('.ocr-export-toast');
    if (previous) previous.remove();

    var toast = document.createElement('div');
    toast.className = 'ocr-export-toast' + (tone ? ' ocr-export-toast--' + tone : '');
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');
    // security-delta: allow innerHTML - static icon plus escaped message
    toast.innerHTML = (tone === 'success' ? ICONS.check : '') + '<span>' + escapeHtml(message) + '</span>';
    document.body.appendChild(toast);
    window.requestAnimationFrame(function () { toast.classList.add('is-visible'); });
    window.setTimeout(function () {
      toast.classList.remove('is-visible');
      window.setTimeout(function () { toast.remove(); }, 220);
    }, 2600);
  }

  function setBusy(trigger, busy) {
    if (!trigger) return;
    trigger.disabled = busy;
    trigger.setAttribute('aria-busy', busy ? 'true' : 'false');
    var label = trigger.querySelector('.ocr-export__label');
    if (label) label.textContent = busy ? 'Preparing…' : 'Export';
    var icon = trigger.querySelector('.ocr-export__icon');
    // security-delta: allow innerHTML - one of two static SVG icons
    if (icon) icon.innerHTML = busy ? ICONS.spinner : ICONS.download;
  }

  function closeMenu(container, restoreFocus) {
    if (!container) return;
    var menu = container.querySelector('.ocr-export__menu');
    var trigger = container.querySelector('.ocr-export__trigger');
    if (!menu || !trigger) return;
    menu.hidden = true;
    trigger.setAttribute('aria-expanded', 'false');
    container.classList.remove('is-open');
    if (restoreFocus) trigger.focus();
  }

  function openMenu(container) {
    var menu = container.querySelector('.ocr-export__menu');
    var trigger = container.querySelector('.ocr-export__trigger');
    if (!menu || !trigger) return;
    menu.hidden = false;
    trigger.setAttribute('aria-expanded', 'true');
    container.classList.add('is-open');
    var first = menu.querySelector('[role="menuitem"]');
    if (first) first.focus();
  }

  function actionButton(iconName, title, description, handler) {
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'ocr-export__item';
    button.setAttribute('role', 'menuitem');
    // security-delta: allow innerHTML - static icon names and escaped labels
    button.innerHTML =
      '<span class="ocr-export__item-icon ocr-export__item-icon--' + iconName + '">' + ICONS[iconName] + '</span>' +
      '<span class="ocr-export__item-copy"><strong>' + escapeHtml(title) + '</strong>' +
      '<span>' + escapeHtml(description) + '</span></span>';
    button.addEventListener('click', handler);
    return button;
  }

  function buildControl(heading, trigger) {
    var container = document.createElement('div');
    container.className = EXPORT_CONTAINER;

    // security-delta: allow innerHTML - static SVG icons only
    trigger.innerHTML =
      '<span class="ocr-export__icon">' + ICONS.download + '</span>' +
      '<span class="ocr-export__label">Export</span>' +
      '<span class="ocr-export__chevron">' + ICONS.chevron + '</span>';

    var menu = document.createElement('div');
    menu.className = 'ocr-export__menu';
    menu.setAttribute('role', 'menu');
    menu.setAttribute('aria-label', 'Export this page');
    menu.hidden = true;

    var eyebrow = document.createElement('div');
    eyebrow.className = 'ocr-export__eyebrow';
    eyebrow.textContent = 'Download or share';
    menu.appendChild(eyebrow);

    menu.appendChild(actionButton('pdf', 'Save as PDF', 'Full page, paginated for A4', function () {
      closeMenu(container);
      savePdf(trigger);
    }));
    menu.appendChild(actionButton('print', 'Print / save as PDF', 'Open the browser print dialog', function () {
      closeMenu(container);
      window.print();
    }));
    menu.appendChild(actionButton('word', 'Word document', 'Editable .doc copy of this page', function () {
      closeMenu(container);
      downloadWord(trigger);
    }));
    menu.appendChild(actionButton('html', 'Web page', 'Standalone HTML file', function () {
      closeMenu(container);
      downloadHtml(trigger);
    }));
    menu.appendChild(actionButton('link', 'Copy page link', 'Share this section with your class', function () {
      closeMenu(container);
      copyLink();
    }));

    trigger.addEventListener('click', function (event) {
      event.stopPropagation();
      if (container.classList.contains('is-open')) {
        closeMenu(container);
      } else {
        openMenu(container);
      }
    });

    trigger.addEventListener('keydown', function (event) {
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        openMenu(container);
      }
    });

    menu.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeMenu(container, true);
        return;
      }
      if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
      event.preventDefault();
      var items = Array.prototype.slice.call(menu.querySelectorAll('[role="menuitem"]'));
      var index = items.indexOf(document.activeElement);
      if (event.key === 'ArrowDown') index = (index + 1) % items.length;
      if (event.key === 'ArrowUp') index = (index - 1 + items.length) % items.length;
      items[index].focus();
    });

    container.appendChild(trigger);
    container.appendChild(menu);
    heading.insertAdjacentElement('afterend', container);

    return container;
  }

  function savePdf(trigger) {
    var clone = buildClone();
    if (!clone) {
      showToast('Could not find page content.', 'error');
      return;
    }

    setBusy(trigger, true);
    var options = {
      margin: [10, 10, 15, 10],
      filename: safeFilename(pageTitle()) + '.pdf',
      image: { type: 'jpeg', quality: 0.95 },
      html2canvas: { scale: 2, useCORS: true, logging: false, scrollY: 0 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak: { mode: ['avoid-all', 'css', 'legacy'] },
    };

    ensurePdfLibrary().then(function () {
      return html2pdf().set(options).from(clone).save();
    }).then(function () {
      setBusy(trigger, false);
      showToast('PDF saved.', 'success');
    }).catch(function () {
      setBusy(trigger, false);
      showToast('PDF generation failed. Try Print / save as PDF instead.', 'error');
    });
  }

  function downloadHtml(trigger) {
    var clone = buildClone();
    if (!clone) {
      showToast('Could not find page content.', 'error');
      return;
    }
    var html = '<!doctype html><html lang="en"><head><meta charset="utf-8">' +
      '<meta name="viewport" content="width=device-width, initial-scale=1">' +
      '<title>' + escapeHtml(pageTitle()) + '</title><style>' + standaloneStyles() + '</style>' +
      '</head><body><article>' + clone.innerHTML + '</article></body></html>';
    setBusy(trigger, true);
    downloadBlob(new Blob([html], { type: 'text/html;charset=utf-8' }), safeFilename(pageTitle()) + '.html');
    setBusy(trigger, false);
    showToast('Web page downloaded.', 'success');
  }

  function downloadWord(trigger) {
    var clone = buildClone();
    if (!clone) {
      showToast('Could not find page content.', 'error');
      return;
    }
    var header = '<html xmlns:o="urn:schemas-microsoft-com:office:office" ' +
      'xmlns:w="urn:schemas-microsoft-com:office:word" ' +
      'xmlns="http://www.w3.org/TR/REC-html40"><head><meta charset="utf-8">' +
      '<title>' + escapeHtml(pageTitle()) + '</title>' +
      '<style>@page WordSection1{size:612pt 792pt;margin:72pt 64pt;} ' +
      'div.WordSection1{page:WordSection1;} body{font-family:Calibri,Arial,sans-serif;font-size:11pt;line-height:1.5;color:#1a1a1a;} ' +
      'h1{font-size:20pt;} h2{font-size:15pt;border-bottom:1px solid #dbe3ee;padding-bottom:3pt;} ' +
      'pre{font-family:Consolas,monospace;font-size:9pt;background:#f5f5f5;padding:6pt;} ' +
      'table{border-collapse:collapse;} th,td{border:1px solid #dbe3ee;padding:4pt;}</style>' +
      '</head><body><div class="WordSection1">' + clone.innerHTML + '</div></body></html>';
    setBusy(trigger, true);
    downloadBlob(new Blob([header], { type: 'application/msword' }), safeFilename(pageTitle()) + '.doc');
    setBusy(trigger, false);
    showToast('Word document downloaded.', 'success');
  }

  function copyLink() {
    var url = window.location.href;
    var done = function () { showToast('Link copied.', 'success'); };
    var fallback = function () {
      var field = document.createElement('textarea');
      field.value = url;
      field.setAttribute('readonly', 'readonly');
      field.style.cssText = 'position:fixed;left:-9999px;top:0;';
      document.body.appendChild(field);
      field.select();
      try {
        document.execCommand('copy') ? done() : showToast('Could not copy the link.', 'error');
      } catch (error) {
        showToast('Could not copy the link.', 'error');
      }
      field.remove();
    };

    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(url).then(done).catch(fallback);
    } else {
      fallback();
    }
  }

  function insertButton() {
    var heading = document.querySelector('.md-content h1');
    if (!heading) return;
    if (heading.parentNode.querySelector('.' + EXPORT_CONTAINER)) return;

    var trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'ocr-export__trigger';
    trigger.title = 'Export this page';
    trigger.setAttribute('aria-haspopup', 'menu');
    trigger.setAttribute('aria-expanded', 'false');
    buildControl(heading, trigger);
  }

  /* Close any open menu when the reader clicks elsewhere or presses Escape. */
  document.addEventListener('click', function (event) {
    document.querySelectorAll('.' + EXPORT_CONTAINER + '.is-open').forEach(function (container) {
      if (!container.contains(event.target)) closeMenu(container);
    });
  });

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;
    document.querySelectorAll('.' + EXPORT_CONTAINER + '.is-open').forEach(function (container) {
      closeMenu(container, true);
    });
  });

  /* Run on the initial load. */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', insertButton);
  } else {
    insertButton();
  }

  /* Re-run after MkDocs Material instant navigation. */
  if (typeof document$ !== 'undefined') {
    document$.subscribe(function () { insertButton(); });
  } else {
    document.addEventListener('DOMContentSwitch', insertButton);
    var bodyObs = new MutationObserver(function () { insertButton(); });
    if (document.body) {
      bodyObs.observe(document.body, { childList: true, subtree: false });
    } else {
      document.addEventListener('DOMContentLoaded', function () {
        bodyObs.observe(document.body, { childList: true, subtree: false });
      });
    }
  }
})();
