# Chapter Review

## What You Practised

- Mapping a public web surface before touching its links
- Using `robots.txt` as a discovery hint
- Reading HTML and JavaScript source instead of only rendered pages
- Inspecting image metadata and extracting an LSB payload
- Searching public code for leaked staging material
- Reading a live public homepage's metadata and head section

## The OSINT Loop

1. **Scope** — what are you allowed to look at?
2. **Collect** — save the page, file, or response exactly as served.
3. **Verify** — corroborate the finding with a second source.
4. **Record** — note the URL, timestamp, command, and result.
5. **Report** — explain impact without publishing real secrets.

## Capstone Questions

1. Correlate the badge ID `KR-0421` across the profile, the badge image, the
   SWOCTS homepage, and the public repository. What does the combination
   reveal that no single source does?
2. Which finding would be most useful to an attacker, and why?
3. Which finding is the easiest for the defender to fix?
4. What would you remove from Kestrel Connect before making it public?
5. How would you prove the public-repository flag is real without copying
   the secret into your report?

## Responsible Disclosure

If this were a real assessment:

- stop collecting once you have enough to prove the issue
- do not download unrelated personal data
- report privately to the owner
- give them a reasonable window to fix it
- never publish a live token, credential, or personal record

## Further Practice

- Search a public repository for `TODO` comments near authentication code.
- Compare a PNG before and after a metadata strip with `exiftool -all=`.
- Use `zsteg` on a harmless test image that you created yourself.
- Read the source of a small open-source web app and list every asset it
  loads. Ask which of those assets could leak information.
