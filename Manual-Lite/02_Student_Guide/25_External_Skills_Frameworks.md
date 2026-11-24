# External Skills Frameworks

The platform uses a single competency vocabulary and maps it to external
frameworks where a credible, reviewed mapping exists. The mapping is evidence
for curriculum design and accreditation. It is not a certification, a grade, or
a job guarantee.

## Frameworks in use or planned

| Framework | What it adds | Current state |
|---|---|---|
| **NICE / NIST Workforce Framework** | Work roles, tasks, and knowledge/skill statements for the cyber workforce | Referenced in the competency crosswalks and role profiles |
| **ACM/IEEE CS2023** | Computing knowledge areas for curriculum alignment | Referenced where the competency is a computing knowledge area |
| **CAE-CD outcomes** | Institutional cyber-defence programme outcomes | Referenced in programme and accreditation evidence |
| **SFIA 9** | Seven levels of responsibility plus a professional-skills catalogue for the digital world | **Blocked pending a product licence.** The personal licence does not permit product use or published mappings. See the [SFIA 9 ingestion plan](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/SFIA-9-INGESTION.md) |

## How the platform uses a mapping

- A lab has a reviewed competency contract.
- The contract names the competency ids and the evidence types that support
  them.
- Accepted evidence contributes to competency coverage and Cyber DNA.
- A crosswalk links the competency to an external framework code or role.
- The crosswalk is versioned and reviewed; an old report keeps the version it
  used.

A mapping describes the **curriculum**, not the learner. A learner who completes
a mapped lab has practised the competency; that does not make them certified,
job-ready, or authorised to test a real system.

## SFIA 9

SFIA 9 was published in October 2024 and is the current standard. It defines
seven levels of responsibility, a professional-skills catalogue, and generic
attributes. The official framework is at
[sfia-online.org/en/sfia-9](https://sfia-online.org/en/sfia-9).

SFIA levels are **responsibility levels**, not scores. A level describes the
scope, autonomy, influence, and accountability expected at that level. It is not
a percentage, a badge, or a pass mark.

The platform has not imported SFIA skill definitions or published a lab-to-SFIA
mapping. The SFIA Foundation's content is subject to its licence and attribution
terms. The personal licence permits personal information and development use
only; it does not permit product use, redistribution, or published mappings.

The platform is a product with a public manual, so it needs a commercial or
academic licence (or written permission) that covers embedding SFIA content and
publishing mappings. Until that licence is recorded, no SFIA definitions,
RDF output, PDFs, or mappings will be added to the repository, the platform, or
this manual.

When a suitable licence is available, the platform will show the mapping as a
read-only crosswalk beside competency coverage. It will not change a learner's
score, grade, or readiness label.

## Why the licensing gate matters

- The SFIA name, skill definitions, level descriptors, and spreadsheet are
  controlled by the SFIA Foundation.
- A public web page is not a redistribution licence.
- A mapping can reference an official code and link to the source without
  copying the full definition, if the licence allows it.
- The ingestion plan records the licence reference, snapshot date, and content
  hash before any content is committed.

## Related pages

- [Navigating your Cyber DNA](22_Navigating_Your_Cyber_DNA.md)
- [Career Atlas and Momentum](21_Career_Atlas_And_Momentum.md)
- [Workbook answers](24_Workbook_Answers.md)
- [SFIA 9 ingestion plan](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/SFIA-9-INGESTION.md)
- [Competency Framework](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/COMPETENCY-FRAMEWORK.md)
