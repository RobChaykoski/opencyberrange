# Anti-scraping and crawler controls

Status: **Active**
Applies to: Community / Academic profile, Professional 2.2.0, Enterprise preview

OpenCyberRange is a private training platform. Its public surface is the login,
registration, certificate-verification, and setup pages. Those pages must not be
indexed by search engines, archived, or used as model-training input.

Authentication remains the primary control. The controls on this page are
defence in depth: they stop compliant crawlers, make the platform's intent
explicit, and raise the cost of bulk collection.

## Controls

| Layer | Control | Where |
|---|---|---|
| Discovery | `robots.txt` disallows every path, with explicit groups for search and AI crawlers | `platform/frontend/public/robots.txt` |
| Page metadata | `noindex, nofollow, noarchive, nosnippet, noimageindex` plus Google/Bing variants | `platform/frontend/index.html` |
| Response headers | `X-Robots-Tag` on HTML, assets, images, wiki pages, downloads, and API responses | `platform/frontend/nginx.conf` and `nginx-ssl.conf` |
| Request filtering | Known crawler and AI-scraper user agents receive `403` before content is served | `nginx.conf` / `nginx-ssl.conf` `$ocr_blocked_crawler` map |
| Edge filtering | Optional early block at Nginx Proxy Manager | See [Reverse proxy](REVERSE-PROXY.md) |
| Authentication | Every learning, profile, admin, and wiki route requires a valid session | Backend routers |

## Blocked user agents

The nginx map blocks these families:

- **Search:** Googlebot, Bingbot, Slurp, DuckDuckBot, Baiduspider, YandexBot,
  Sogou, Exabot, Qwantify, SeznamBot, NaverBot, Yeti, ia_archiver.
- **AI and model training:** GPTBot, OAI-SearchBot, ChatGPT-User,
  Google-Extended, ClaudeBot, Claude-Web, anthropic-ai, PerplexityBot, CCBot,
  Bytespider, Amazonbot, Applebot-Extended, Meta-ExternalAgent,
  Meta-ExternalFetcher, cohere-ai, YouBot, Diffbot.
- **SEO and bulk scrapers:** AhrefsBot, SemrushBot, MJ12bot, DotBot, PetalBot,
  Barkrowler, DataForSeoBot, Scrapy, omgili, omgilibot.

Social link-preview bots are deliberately not blocked. If a preview bot is
abused, add it to the same map.

## Keeping the lists in step

The same families appear in three places:

1. `platform/frontend/public/robots.txt`
2. the `$ocr_blocked_crawler` map in `nginx.conf` and `nginx-ssl.conf`
3. the optional Nginx Proxy Manager advanced configuration in
   [Reverse proxy](REVERSE-PROXY.md)

When adding a crawler, update all three and rebuild the frontend image so the
new nginx configuration is baked in.

## Verification

Run these against a deployed host:

```bash
# robots.txt is served and disallows everything
curl -fsS https://labs.example.com/robots.txt

# HTML carries X-Robots-Tag and the noindex meta tag
curl -fsSI https://labs.example.com/login | grep -i 'x-robots-tag'
curl -fsS https://labs.example.com/login | grep -i 'name="robots"'

# Known crawlers are refused
curl -fsS -A 'GPTBot' https://labs.example.com/ -o /dev/null -w '%{http_code}\n'
curl -fsS -A 'Googlebot' https://labs.example.com/ -o /dev/null -w '%{http_code}\n'

# Normal clients still work
curl -fsS -A 'Mozilla/5.0' https://labs.example.com/ -o /dev/null -w '%{http_code}\n'
```

Expected: `robots.txt` returns `Disallow: /`, the headers are present, the
crawler requests return `403`, and the normal request returns `200`.

## Limitations

- User-agent strings are self-declared. A determined scraper can spoof a
  browser. Authentication, rate limiting, and audit logging remain the controls
  that matter for protected content.
- `robots.txt` is advisory. The `403` map and the authentication boundary are
  what enforce the policy.
- Do not block a crawler that the institution relies on for accessibility,
  monitoring, or link previews without checking the impact first.

## Evidence

Record header output and crawler `403` results in
[`V2-SECURITY-EVIDENCE.md`](V2-SECURITY-EVIDENCE.md) when a release changes the
nginx configuration.
