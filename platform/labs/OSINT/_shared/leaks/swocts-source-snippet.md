# SWOCTS source-code flag

The OSINT exercise **The Public Homepage** expects this marker in the source
of `https://www.swocts.com`:

```text
OCR{swocts_v13w_s0urc3}
```

## Next.js (app router)

Add a custom metadata field in the root layout, for example `app/layout.tsx`:

```tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  // ...existing metadata
  other: {
    "x-swocts-osint": "OCR{swocts_v13w_s0urc3}",
  },
};
```

Next.js renders this as:

```html
<meta name="x-swocts-osint" content="OCR{swocts_v13w_s0urc3}"/>
```

## Static HTML

If the site is not using the Next.js metadata API, place this in the document
head:

```html
<meta name="x-swocts-osint" content="OCR{swocts_v13w_s0urc3}" />
```

Keep the value identical to the lab flag. The lab checks the submitted value
case-sensitively.
