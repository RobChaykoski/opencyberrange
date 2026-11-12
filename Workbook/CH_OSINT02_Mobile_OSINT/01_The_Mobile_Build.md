# Exercise 1.1 -- The Mobile Build

**Track:** OSINT · **Difficulty:** Beginner · **Estimated time:** 25 minutes

**Framework alignment:** [MITRE ATT&CK](https://attack.mitre.org/) Reconnaissance
T1593 Search Open Websites/Domains and T1592.004 Gather Victim Host Information:
Client Configurations.

## Before You Begin

- Launch the **The Mobile Build** exercise and open the **Active Lab View**.
- Note the target address shown for the portal, for example
  `http://10.100.13.84:8080/`. Your session uses a different `/24`; substitute
  your own address.
- You need a browser. A phone is strongly recommended, because the mobile
  renderer is the intended path. A terminal with `curl` is the fallback.

## Scenario

Kestrel Ridge has a staff portal with a public profile page. The desktop build
and the mobile build are rendered from different templates. The mobile template
includes a **mobile contact card** that the desktop template does not render.

You have been asked to review the portal the way a researcher with a phone
would. Open the profile on your phone, compare what the two clients receive, and
recover the access marker from the mobile-only card.

This is a safe, simulated portal. It has no connection to the real internet and
no real employee data.

## Objectives

1. Open the same profile from a desktop browser and from a phone.
2. Identify what the mobile response contains that the desktop response does not.
3. Explain why the difference is a rendering choice, not an access control.
4. Submit the access marker as the flag.

## Background: one URL, two renderers

A server can decide what to send based on the `User-Agent` header, a cookie, a
query parameter, or the viewport. That decision is not automatically a security
boundary. If the mobile response contains a field that the desktop response
omits, the field is still being sent to a client that may not be authorised to
see it.

The safer pattern is to authorise the request first, then return only the fields
that the authenticated user may see. Hiding a field in one template is not the
same as protecting it.

## Walkthrough

### 1. Open the desktop build

On your laptop, open the portal address from the Active Lab View. You should see
a **Desktop build** label and a **Renderer note** that says the mobile build
differs. The desktop page does not contain the access marker.

### 2. Open the mobile build on your phone

Connect your phone to the same lab network. If your course uses the platform
VPN, install the WireGuard profile on the phone and connect before opening the
address. Open the same portal address in the phone browser.

The mobile build shows a **Mobile contact card** with an **Access marker**
field. That value is the flag.

!!! tip "No phone?"
    Use a mobile user agent from a terminal:

    ```bash
    curl -s -A "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)" \
      http://10.100.13.84:8080/
    ```

    Replace the address with your own target. Compare the response with the
    desktop request.

### 3. Compare the responses

From the terminal, compare the desktop and mobile responses:

```bash
curl -s http://10.100.13.84:8080/ | grep -o 'OCR{[^}]*}'
curl -s -A "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)" \
  http://10.100.13.84:8080/ | grep -o 'OCR{[^}]*}'
```

The first command should return nothing. The second should return the flag. The
JSON endpoint makes the same decision:

```bash
curl -s -A "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)" \
  http://10.100.13.84:8080/api/profile
```

### 4. Submit the flag

Copy the access marker exactly as it appears and submit it on the exercise page.

## Analysis Questions

1. Which client received the extra field? What decided that?
2. Was the field hidden by CSS, by the template, or by an authorisation check?
3. If the desktop user can send the mobile `User-Agent`, what does that tell you
   about the protection?
4. What would you change in the server code to make the field safe?
5. Where else have you seen a mobile-only or desktop-only view that exposed more
   than the other view?

## Defensive Takeaways

- Authorise every request before choosing a template.
- Do not rely on a client-specific view to protect data.
- Return the minimum field set for the authenticated user, not the maximum field
  set for the client class.
- Test the same endpoint with different clients and compare the responses.
- Treat a renderer difference as a potential information leak until you can
  explain why it is safe.

## If You Get Stuck

- Confirm you are using the address from **your** Active Lab View, not the
  example address in this page.
- If the phone cannot reach the target, check the VPN connection and the target
  address.
- If the mobile card does not appear, check the `User-Agent` your client sends.
- If the flag is rejected, copy the value exactly; do not add spaces or change
  the case.
