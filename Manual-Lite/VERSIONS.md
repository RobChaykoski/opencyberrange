# Manual editions

The core manual in this folder describes the workflows shared by the
**Community / Academic**, **Professional**, and **Enterprise** edition profiles
on platform **Release 5.38.0**, plus the **Advanced DNA Insights** feature
(enabled under Admin settings). Professional and Enterprise are cumulative:
every page here still applies, and each edition adds the pages in its own
supplement.

!!! note "Development preview"
    Momentum, the Career Atlas, and the extended career dossier are gated by
    **Admin -> Settings -> Features -> Advanced DNA Insights**. They are off by
    default in production. See
    [Career Atlas and Momentum](02_Student_Guide/21_Career_Atlas_And_Momentum.md).

| Edition profile | Platform release | Manual | What it adds |
|---|---|---|---|
| Community / Academic | Release 5.38.0 | This manual | Single-host teaching platform, labs, workbooks, evidence review, courses, certificates, privacy, and administration |
| Professional | Release 5.38.0 | [Professional supplement](09_Professional/index.md) | Analytics and reporting, competency evidence, feedback, exercise health, and intervention signals |
| Enterprise | Release 5.38.0 (SSO; HA preview) | [Enterprise supplement](10_Enterprise/index.md) | Multi-host HA lab pool, OIDC/SAML/LDAP SSO, LTI 1.3, enterprise reporting, and compliance reporting |

Release 5 remains a single-tenant appliance: one deployment serves one
institution. LTI 1.3 is implemented; full multi-tenancy is deferred. SFIA 9
crosswalks are planned under the licensing gate in
[SFIA 9 ingestion](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/SFIA-9-INGESTION.md).
Confirm the edition-specific limits in
[Admin Panel Overview](04_Admin_Guide/01_Admin_Panel_Overview.md).

## How to use the manuals

- Start with this manual for anything a learner, instructor, or administrator
  does on a single host.
- Open the Professional supplement when you need the analytics, reporting, or
  competency pages. Those pages assume the core manual.
- Open the Enterprise supplement for the HA topology, identity federation, and
  compliance material. HA is a separate deployment, not a setting in the
  single-host Compose stack.

!!! note "Keep the editions cumulative"
    A fix or explanation that belongs to all editions belongs in this core
    manual first. The supplements should describe only the delta for their
    edition so the three manuals cannot drift apart.
