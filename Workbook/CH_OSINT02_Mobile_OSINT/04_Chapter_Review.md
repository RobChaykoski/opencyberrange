# Chapter Review -- Mobile OSINT

## Self-assessment

1. Can you explain the difference between hiding a field in a template and
   authorising a request?
2. Can you reproduce the mobile response with a `curl` user agent?
3. Can you name two other client signals a server might use to change a
   response?
4. Can you describe a safe way to serve different fields to different clients?

## Answer key

1. Hiding a field in a template changes what one client displays. Authorising a
   request decides whether the user may receive the field at all. Only the
   second is a security control.
2. Use `curl -A "Mozilla/5.0 (iPhone; ...)"` against the same URL and compare
   the response with the desktop request.
3. Examples include the `User-Agent`, cookies, query parameters, the `Accept`
   header, and the viewport. None of them is a substitute for authorisation.
4. Authenticate the user, check the user's permission for each field, and return
   only the permitted fields. Use the same authorisation decision for every
   client.

## Command cheat sheet

```bash
# Desktop response
curl -s http://<target>:8080/

# Mobile response
curl -s -A "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)" \
  http://<target>:8080/

# Mobile JSON
curl -s -A "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)" \
  http://<target>:8080/api/profile
```

## Next step

The public-profile exercise uses an instructor-owned profile as an authorised
OSINT source. The banner exercise uses a synthetic Shodan-style mirror with
fictional hosts. All three keep the same rule: only the authorised target in the
brief, and no collection of real personal data.
