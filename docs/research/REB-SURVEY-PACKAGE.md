# REB-ready survey package

**Status:** template for Research Ethics Board review. Do not recruit
participants until the REB has approved the protocol and the approved consent
form is in use.

**Document version:** 2026-11-04  
**Platform privacy contact:** privacy@swocts.com  
**Principal investigator:** _to be completed_  
**Institution / REB protocol number:** _to be completed_

This package supports a low-risk, optional survey about the OpenCyberRange
platform and how it is used. It is written for a Canadian REB context and aligns
with TCPS 2 and PIPEDA. It is not legal advice; the REB and the institution's
privacy office make the final determination.

## Package contents

1. Study summary
2. Background and rationale
3. Research questions
4. Participants and eligibility
5. Consent process
6. Recruitment and opt-in flow
7. Survey instrument
8. Data collection and management
9. Privacy and PIPEDA alignment
10. Risks and benefits
11. Withdrawal and incident handling
12. Dissemination and reporting
13. REB submission checklist
14. Appendix A — Consent form template
15. Appendix B — Survey instrument (standalone copy)
16. Appendix C — Data dictionary
17. Appendix D — Platform privacy statement reference

## 1. Study summary

| Item | Detail |
|---|---|
| Title | Learner and instructor experience with the OpenCyberRange platform |
| Design | Optional, cross-sectional, self-administered online survey with Likert and open-ended questions |
| Purpose | Understand usability, reliability, accessibility, and platform usage to improve the learning environment |
| Population | Adult learners and instructors who use the platform; minors only with REB-approved guardian consent and assent |
| Recruitment | In-platform opt-in from Profile → Surveys, plus a plain-language invitation |
| Consent | Explicit opt-in after the versioned survey privacy statement; separate REB consent form where required |
| Data | Survey responses, role, track context, device class, and timestamps; no passwords, grades, lab flags, or sensitive personal data |
| Retention | Responses up to 24 months; consent records up to 24 months after withdrawal |
| Risks | Minimal: possible inconvenience, mild discomfort answering open-ended questions, and privacy risk mitigated by data minimisation |
| Benefits | No direct benefit; indirect benefit is improved platform usability and learning experience |
| Compensation | None |
| Dissemination | Aggregate findings to the operator and, where appropriate, a report or conference presentation |

## 2. Background and rationale

OpenCyberRange is a self-hosted cybersecurity training platform. Learners work
through tracks, levels, and labs; instructors assign labs to courses and review
completion data; administrators operate the platform. The platform already
records completion, attempts, hints, time, and certificates for learning and
administration.

The survey addresses a gap: the platform records **what** learners did, but not
**how the experience felt** or **where the interface created friction**. The
study asks about the platform and its usage only. It does not ask about
participants' personal lives, beliefs, health, finances, or other sensitive
topics.

## 3. Research questions

1. Which platform features do learners and instructors find most and least
   usable?
2. Where do learners experience friction in the path from sign-in to launching
   a lab, following the workbook, submitting a flag, and earning a certificate?
3. How reliable and accessible is the platform across devices and connection
   types?
4. Which improvements would have the greatest positive impact on the learning
   experience?
5. How do instructors use completion, attempt, hint, and time data in courses?

## 4. Participants and eligibility

### Inclusion

- Adults (18+) who are registered learners, instructors, or administrators on an
  OpenCyberRange deployment and who have used the platform at least once.
- Minors may participate **only** if the REB approves a guardian consent and
  youth assent process and the deployment has implemented it. The platform's
  opt-in switch alone is not sufficient for minors.

### Exclusion

- People who have not used the platform.
- Anyone who cannot provide informed consent (or guardian consent and assent
  where applicable).
- Anyone outside the approved deployment(s).

### Vulnerable participants

Students are in a relationship of dependency with instructors and the
institution. Participation must be voluntary, must not affect grades,
assessment, enrolment, or support, and must not be solicited by an instructor
who has direct academic authority over the participant. The survey invitation
should come from the platform or research team, not from the course instructor.

## 5. Consent process

The platform has a two-step consent flow:

1. The learner opens **Profile → Surveys**.
2. Clicking **Opt in to surveys** opens the full, versioned privacy statement.
3. Consent is recorded only after the learner presses **I agree — opt me in**.

The platform records the opt-in flag, timestamp, and statement version, and
appends every opt-in and withdrawal to the consent history. Withdrawal is
available from the same panel.

For the research study, the REB may require a separate consent form in addition
to the platform opt-in. If so, the survey must not open until the participant
has read the REB-approved consent form and indicated agreement. The platform
opt-in and the REB consent are separate records; neither substitutes for the
other.

Consent must state:

- the purpose of the study;
- what data will be collected and what will not;
- that participation is voluntary;
- that declining or withdrawing has no effect on grades, access, or support;
- the retention period and who can access the data;
- how to withdraw and how to request deletion;
- the privacy contact and the REB contact.

## 6. Recruitment and opt-in flow

1. The platform operator enables the survey feature and publishes the current
   privacy statement version.
2. An invitation is posted in the platform or sent through the platform's
   normal communication channel. The invitation must not be sent by an
   instructor with direct academic authority over the recipient.
3. The invitation links to **Profile → Surveys** and the REB-approved consent
   form.
4. Only accounts with `survey_opt_in = true` and, where required, a recorded REB
   consent are eligible to see the survey.
5. The survey can be completed once per consented participant per round. The
   platform may record a pseudonymous response ID to prevent duplicates.

Recruitment text must not promise benefits, imply that participation is
required, or suggest that declining will affect grades or access.

## 7. Survey instrument

The full instrument is in Appendix B. It has five sections and takes about
8–12 minutes:

- **A. About your use** — role, track context, experience level.
- **B. Usability** — navigation, finding exercises, launching labs, workbook
  clarity, feedback, reliability, performance, accessibility.
- **C. Learning experience** — confidence, difficulty, hints, progression,
  certificates.
- **D. Features** — VPN setup, RangeBox, competitions, profile, transcript,
  survey flow.
- **E. Open-ended** — what worked, what to improve, one change.

The instrument uses 5-point Likert items, optional single-choice items, and
optional open-ended text. No question requires a name, email, student ID, or
other direct identifier. Open-ended answers should be reviewed before release to
remove accidental identifiers.

## 8. Data collection and management

### What is collected

- Survey answers (Likert, single-choice, open text).
- Role (student, instructor, administrator) and, optionally, track context.
- Device class (desktop, tablet, mobile) and browser family, if the survey
  records it.
- Response timestamp and survey round.
- A pseudonymous response ID, and optionally a keyed hash of the account ID to
  link a response to platform usage data without storing the account ID in the
  survey dataset.

### What is not collected

- Passwords or password hashes.
- Grades, quiz answers, lab flags, or flag attempts.
- Government identifiers, financial information, health information, or other
  sensitive personal data.
- IP addresses in the research dataset.
- Names, emails, or student IDs in open text (participants are asked not to
  include them).

### Storage and access

- Responses are stored on the platform server in the operator's controlled
  environment.
- Access is limited to the named research team and authorised platform
  administrators who need it for the study.
- The research dataset is exported to an encrypted, access-controlled location
  for analysis.
- Aggregate tables are separated from free-text responses.

### Retention

- Survey responses: up to 24 months from the survey date, unless the approved
  protocol states a shorter period.
- Consent records: while the account is active and up to 24 months after
  withdrawal, to demonstrate that consent was handled correctly.
- After retention, responses are deleted or reduced to aggregate statistics that
  cannot identify a participant.

### De-identification

- Direct identifiers are not collected in the survey.
- If a keyed account hash is used, the key is held separately from the
  dataset.
- Free-text answers are reviewed for accidental identifiers before analysis and
  before any quotation is used.
- Small cells (for example, a single instructor in a category) are suppressed in
  reports.

## 9. Privacy and PIPEDA alignment

| PIPEDA principle | How the study applies it |
|---|---|
| Accountability | A named PI and privacy contact are responsible; the REB protocol records the team and roles |
| Identifying purposes | The consent form and privacy statement state the purpose before collection |
| Consent | Explicit opt-in after the statement; withdrawal is available and recorded |
| Limiting collection | Only platform/usage data; no passwords, grades, flags, or sensitive data |
| Limiting use, disclosure, retention | Used for platform improvement and aggregate reporting; retained for a fixed period |
| Accuracy | Participants can review and correct their responses on request |
| Safeguards | Access control, encryption in transit, encrypted analysis storage, small-cell suppression |
| Openness | The privacy statement and this package are available to participants and the REB |
| Individual access | Participants can request their responses through the privacy contact |
| Challenging compliance | Participants can contact the privacy contact and the REB |

## 10. Risks and benefits

### Risks

- **Minimal psychological or emotional risk.** Some open-ended questions may
  prompt reflection on a frustrating experience. Participants can skip any
  question.
- **Privacy risk.** Mitigated by not collecting direct identifiers, minimising
  device data, suppressing small cells, and limiting access.
- **Power imbalance.** Mitigated by voluntary participation, no grade impact,
  and recruitment that does not come from a course instructor with direct
  authority.

### Benefits

There is no direct benefit or compensation. The indirect benefit is improved
platform usability and a better learning experience for future learners.

### Risk/benefit conclusion

The study is minimal risk. The potential benefit to the platform and future
learners is proportionate to the minimal burden on participants.

## 11. Withdrawal and incident handling

- Participants can withdraw from future surveys at any time from **Profile →
  Surveys** or by contacting privacy@swocts.com.
- Withdrawal stops future invitations immediately.
- Participants can ask for their prior responses to be deleted. The research
  team will delete them unless the approved protocol requires retention for
  audit or aggregate reporting; in that case the participant will be told why.
- If a privacy incident occurs, the operator follows its incident-response and
  breach-notification process, notifies the REB as required, and records the
  incident in the platform audit trail.

## 12. Dissemination and reporting

- Findings are reported in aggregate. No individual learner, instructor, or
  institution is identified.
- Quotations from open text are used only with permission and after
  de-identification; small cells are suppressed.
- Reports distinguish platform activity signals from learning outcomes and do
  not rank individual learners.
- Results may be shared with the platform operator, the institution, and the
  REB. External publication requires the approved protocol and REB guidance.

## 13. REB submission checklist

- [ ] Protocol synopsis and full protocol
- [ ] Research questions and design
- [ ] Participant population, inclusion/exclusion, and vulnerability analysis
- [ ] Recruitment materials and invitation text
- [ ] Consent form (and guardian consent/assent if minors are included)
- [ ] Survey instrument
- [ ] Data management plan and data dictionary
- [ ] Privacy impact assessment / PIPEDA alignment
- [ ] Risk/benefit assessment
- [ ] Withdrawal and incident procedures
- [ ] Dissemination plan
- [ ] Conflict-of-interest declarations
- [ ] TCPS 2 CORE tutorial certificates for the research team
- [ ] Platform privacy statement version and consent flow screenshots
- [ ] REB protocol number and approval date recorded before recruitment
- [ ] Data-sharing or transfer agreements, if any
- [ ] Retention and destruction schedule

## Appendix A — Consent form template

> **Study title:** Learner and instructor experience with the OpenCyberRange
> platform
>
> **Principal investigator:** _name, department, institution, email_
>
> **REB protocol:** _number_
>
> **What is this study about?** We want to understand how learners and
> instructors use OpenCyberRange and where the platform can be improved. The
> survey asks about the platform and its usage, not about your personal life.
>
> **What will I be asked to do?** Complete an optional online survey of about
> 8–12 minutes. You can skip any question and stop at any time.
>
> **What data will be collected?** Your survey answers, your role, optional
> track context, device class, and a timestamp. We will not collect your
> password, grades, lab flags, or sensitive personal information.
>
> **Do I have to participate?** No. Participation is voluntary. Declining or
> withdrawing will not affect your grades, access, enrolment, or support.
>
> **Can I withdraw?** Yes. You can withdraw from future surveys in Profile →
> Surveys or by contacting privacy@swocts.com. You can ask for your prior
> responses to be deleted.
>
> **How long will data be kept?** Responses are kept for up to 24 months and
> then deleted or aggregated. Consent records are kept while your account is
> active and up to 24 months after withdrawal.
>
> **Who will see the data?** The named research team and authorised platform
> administrators. Reports use aggregate data and suppress small cells.
>
> **What are the risks and benefits?** The study is minimal risk. There is no
> direct benefit or compensation; the indirect benefit is a better platform.
>
> **Who can I contact?** Privacy: privacy@swocts.com. REB: _office, email,
> phone._
>
> **Consent.** By clicking **I agree** below, I confirm that I have read this
> form, I understand the study, and I agree to participate. I understand that I
> can withdraw at any time.

## Appendix B — Survey instrument

### Section A — About your use

A1. Which role best describes you?
- Student
- Instructor
- Administrator
- Other / prefer not to say

A2. Which track or course were you working in most recently? (optional free text
or track list)

A3. How would you describe your experience with the platform?
- First few sessions
- A few weeks
- A few months
- More than six months

### Section B — Usability

Please rate each statement from 1 (strongly disagree) to 5 (strongly agree), or
select "not applicable".

B1. I could find the exercise I wanted without help.
B2. Starting a lab was straightforward.
B3. The workbook instructions were clear and easy to follow.
B4. The feedback after submitting a flag helped me understand what to do next.
B5. The platform was reliable during my session.
B6. The platform performed well on my device and connection.
B7. The interface was readable and usable on my screen size.
B8. The VPN setup instructions were clear. (If you did not use the VPN, choose
"not applicable".)
B9. The RangeBox desktop was responsive enough for the exercise. (If you did not
use RangeBox, choose "not applicable".)
B10. I could recover from an error without losing my work.

### Section C — Learning experience

C1. The difficulty of the exercises matched my current level.
C2. The hints were useful without giving away the answer.
C3. The progression from one level to the next felt coherent.
C4. The workbook analysis questions helped me consolidate what I learned.
C5. I understood why I earned a certificate.
C6. I felt confident applying the skills outside the platform.

### Section D — Features

D1. Which features did you use? (select all that apply)
- Tracks and levels
- Workbook
- VPN
- RangeBox / browser desktop
- Courses
- Competitions
- Profile and certificates
- Transcript PDF
- Celebration Wall
- Surveys

D2. Which feature was most valuable to you? (single choice or short text)

D3. Which feature needs the most improvement? (single choice or short text)

D4. Did you use the platform on a shared or low-spec device?
- Yes
- No
- Prefer not to say

### Section E — Open-ended

E1. What worked well for you on the platform?
E2. What got in the way of your learning?
E3. If you could change one thing about the platform, what would it be?
E4. Is there anything else you want the team to know?

Please do not include names, email addresses, student IDs, passwords, flags, or
other personal information in your answers.

## Appendix C — Data dictionary

| Field | Type | Description | Identifiable? |
|---|---|---|---|
| `response_id` | string | Random pseudonymous response identifier | No |
| `account_hash` | string (optional) | Keyed hash of the account ID, used to link usage data | Pseudonymous |
| `role` | enum | student / instructor / administrator / other | No |
| `track_context` | string | Track or course the participant was using | No |
| `experience_level` | enum | first sessions / weeks / months / 6+ months | No |
| `device_class` | enum | desktop / tablet / mobile / unknown | No |
| `likert_B1..B10` | integer 1–5 | Usability ratings | No |
| `likert_C1..C6` | integer 1–5 | Learning-experience ratings | No |
| `features_used` | string list | Selected features | No |
| `open_E1..E4` | text | Open-ended answers, reviewed for identifiers | Potentially |
| `submitted_at` | timestamp | Response time | No |
| `survey_round` | string | Survey wave identifier | No |

## Appendix D — Platform privacy statement reference

The platform's current survey privacy statement is versioned in
`platform/backend/app/services/survey_consent.py`. The statement covers purpose,
scope, data minimisation, consent, use and disclosure, retention, safeguards,
access and correction, withdrawal, accountability, and contact. The version
recorded with each consent must match the statement the participant saw.

The platform privacy contact is **privacy@swocts.com**. Update this package if
the contact or the statement version changes.

## Related documents

- [Survey privacy and consent](../SURVEY-PRIVACY.md)
- [Privacy, erasure, and backups](../PRIVACY-AND-DATA-DELETION.md)
- [System architecture](../ARCHITECTURE.md)
- [Learning framework](../LEARNING-FRAMEWORK.md)
- [NICE mapping matrix](../NICE-MAPPING.md)
