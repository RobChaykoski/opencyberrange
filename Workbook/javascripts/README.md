# Workbook JavaScript vendor assets

| File | Version | Licence | Source | SHA256 |
|---|---|---|---|---|
| `html2pdf.bundle.min.js` | 0.10.2 | MIT (Erik Koopmans) | https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.2/html2pdf.bundle.min.js | `73b512869d64d0f2828e436b24b23b7d84f24b7028bba6c49cb4d1c988103da4` |
| `mermaid.min.js` | 11.17.2 | MIT (Knut Sveidqvist) | https://registry.npmjs.org/mermaid/-/mermaid-11.17.2.tgz (`dist/mermaid.min.js`) | `581ed7d74bd9048d0e3a91363927d72ef22942d7722546b27f7cc29e35390eb8` |

The licence texts are `html2pdf.LICENSE.txt` and `mermaid.LICENSE.txt`.
`embed-mode.js` is first-party code.

Mermaid is loaded as a local classic script before Material's bundle runs, so
the wiki never needs `unpkg.com` in its CSP.
