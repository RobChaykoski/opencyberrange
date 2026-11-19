# User-manual JavaScript assets

| File | Version | Licence | Source |
|---|---|---|---|
| `html2pdf.bundle.min.js` | 0.10.2 | MIT (Erik Koopmans) | https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.2/html2pdf.bundle.min.js |
| `pdf-export.js` | first-party | PolyForm Noncommercial 1.0.0 | This repository |

`html2pdf` is loaded lazily by `pdf-export.js` only when the reader chooses
**Save as PDF**. Do not add it to `extra_javascript`; that would download the
bundle on every page.

The licence text is `html2pdf.LICENSE.txt`.
