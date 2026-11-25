# ZAP Baseline Triage: Shared Files Exposure

**Track:** Web · **Level:** 11 · **Time:** 60 minutes · **Difficulty:** intermediate

## Scenario

Northshore Community Arts is preparing a small public site for its 2026 season.
The director asked for a quick scanner pass and a human read of the results
before launch. The site is a synthetic practice target with no real member,
donor, or event data.

You have written authorisation to test this lab target only. Run a ZAP baseline
scan, triage the report by risk and evidence, and confirm at least one finding
by hand. A shared export directory is part of the site. Find out whether it is
exposed, what it contains, and what the organisation should do before launch.

## What you will practise

- Run a passive baseline scan against an authorised practice target.
- Read scanner evidence instead of relying on alert names.
- Separate a confirmed finding from a false positive or a low-value alert.
- Recover an exposed assessment token and explain the impact.
- Write a remediation and retest note.

## Before You Begin

- Start the exercise from the Web track, level 11. The target is a local Flask
  practice app; use the hostname or IP shown in the exercise details.
- Open **Tools → ZAP scan**. The planner writes the command and a triage
  checklist. It does not run the scan.
- If ZAP is not installed, the planner links to the official download page. In
  a restricted workspace, use the preinstalled ZAP or the Docker image shown in
  the command.
- Use the lab target only. Do not point a scan at a public service, another
  learner's host, or a production deployment.

## Work through the exercise

1. **Open the site.** Browse the landing page and note the links and the search
   form. Keep the browser open for manual confirmation later.

2. **Build the baseline command.** In the planner, choose **Baseline**, enter
   the lab target URL, choose the HTML report, and tick all three authorisation
   boxes. Copy the command.

   The shape is:

   ```bash
   docker run --rm -t -v "$PWD:/zap/wrk/:rw" zaproxy/zap-stable \
     zap-baseline.py -t 'http://<target>/' \
     -r zap-report.html -J zap-report.json -m 5 -l WARN
   ```

   A local ZAP install uses `zap-baseline.py` with the same flags.

3. **Run the scan.** Run the command in the RangeBox terminal. Open
   `zap-report.html` in the browser. The baseline scan is passive; it does not
   change the site.

4. **Triage by risk and evidence.** Sort the report by risk. For each alert,
   open the request and response evidence. Focus on:
   - directory browsing or a public export directory;
   - missing security headers;
   - a cookie without `HttpOnly` or `Secure`;
   - server or framework version disclosure.

5. **Confirm the directory finding by hand.** Use the URL from the report, or
   the **Shared files** link on the landing page. A confirmed finding has
   evidence you can reproduce, not just an alert name. Open the exposed export
   and recover the assessment token.

6. **Record the finding.** Write a short note with:
   - **Finding:** what is exposed and where.
   - **Evidence:** the URL, the response, and the file name.
   - **Impact:** who could read it and what it reveals.
   - **Fix:** remove the directory from the public root, require
     authentication, or serve it from a separate controlled host.
   - **Retest:** rerun the baseline scan and confirm the listing no longer
     appears.

7. **Optional full scan.** Run `zap-full-scan.py` against the same disposable
   target. Compare the report with the baseline. The full scan sends active
   attacks; keep it on this lab target. What did it add, and which new alert
   would you confirm by hand before reporting it?

## Evidence

- The assessment flag from the exposed file.
- A short triage note with the finding, evidence, impact, fix, and retest.
- The ZAP command and the report file name you used.

## Analysis Questions

**1. Why is a scanner alert a candidate rather than a confirmed finding?**

**2. What makes a public directory listing a security issue even when the files
look boring?**

**3. What did the baseline report not prove about the site?**

**4. Which finding would you fix first, and why?**

**5. How would you retest the fix without relying only on the scanner?**

## Defensive takeaway

Remove export and backup directories from the public document root, require
authentication for shared files, set explicit security headers, and do not
expose framework versions. Treat scanner output as a candidate list: confirm
each finding, fix the ones that matter, and retest.

## If You Get Stuck

- Confirm the target URL includes the trailing slash and the lab app is
  running.
- If the report is empty, check that the scan points at the lab target and not
  at a public site.
- If the directory listing is not in the report, open the **Shared files** link
  from the landing page and confirm it by hand. The report is a guide, not the
  only evidence.
- If ZAP is unavailable, use the planner's download link or the Docker command.
  Do not replace the scan with a blind guess; the lab is about reading
  evidence.

> The target is a local, intentionally imperfect practice app. Do not test a
> real host or another learner's session.
