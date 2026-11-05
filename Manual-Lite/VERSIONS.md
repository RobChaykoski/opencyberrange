# Manual editions

The core manual in this folder describes the **Community / Academic 1.1**
platform. Professional and Enterprise are cumulative: every page here still
applies, and each edition adds the pages in its own supplement.

| Edition | Version | Manual | What it adds |
|---|---|---|---|
| Community / Academic | 1.1.x | This manual | Single-host teaching platform, labs, workbooks, courses, certificates, privacy, and administration |
| Professional | 2.1.x | [Professional supplement](09_Professional/index.md) | Learning analytics, cross-course reports, competency evidence, feedback, radar reporting, exercise health, and intervention signals |
| Enterprise | 3.0.x | [Enterprise supplement](10_Enterprise/index.md) | Multi-host HA lab pool, SSO, enterprise reporting, multi-tenancy, LMS/SIS integration, and compliance reporting |

## How to use the manuals

- Start with this manual for anything a learner, instructor, or administrator
  does on a single host.
- Open the Professional supplement when you need the analytics, reporting, or
  competency pages. Those pages assume the core manual.
- Open the Enterprise supplement for the HA topology, identity federation,
  tenancy, and compliance material. HA is a separate deployment, not a setting
  in the single-host Compose stack.

!!! note "Keep the editions cumulative"
    A fix or explanation that belongs to all editions belongs in this core
    manual first. The supplements should describe only the delta for their
    edition so the three manuals cannot drift apart.
