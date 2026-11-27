# Environment setup

Run on staging or development, never production.

## Platform

- [ ] Release under test is deployed and `/api/version` matches the intended tag.
- [ ] Admin can sign in.
- [ ] A test course named `First-Time User Test` exists and is active.
- [ ] The selected lab is assigned and visible.
- [ ] The invite code is fresh and recorded on the course card.
- [ ] The approval gate is on, so approval wait is measured.
- [ ] The test course has no real learner data.

## VPN

- [ ] WireGuard server is reachable from the test network.
- [ ] Peer Manager is healthy.
- [ ] A test peer can connect and reach only its assigned lab `/24`.
- [ ] The client install package is available for the test device.
- [ ] A second peer is available for the separation check.

## Devices

- [ ] Fresh browser profile per participant; no saved session.
- [ ] No pre-installed VPN profile.
- [ ] Screen resolution and browser zoom recorded.
- [ ] For a minor: minor-safe lab, guardian consent, facilitator present.
- [ ] A backup device is available if the participant's device fails.

## Reset between sessions

- [ ] Delete the participant account and its sessions.
- [ ] Revoke the VPN peer and remove the firewall rule.
- [ ] Remove the browser profile and downloaded VPN config.
- [ ] Clear the course invite code if it is single-use.
- [ ] Confirm the next participant starts signed out.

## Evidence

- [ ] Timing sheet row created before the session.
- [ ] Observation log opened.
- [ ] Timer tested.
- [ ] Course card and lab card printed or visible.
- [ ] Consent forms ready, including guardian form.
