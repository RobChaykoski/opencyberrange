# SWSEC02: API Testing with Karate

<!-- BEGIN GENERATED CHAPTER POSITION -->
!!! note "Curriculum position"
    **Chapter:** `SWSEC02` — API Testing with Karate
    **Prerequisites:** `SWSEC01` — Software Security Foundations
    **Recommended next:** `MAL01` — Malware Fundamentals
<!-- END GENERATED CHAPTER POSITION -->

## Why this chapter exists

Most software security work starts with a request and a response. You need to
know what the service promised, what it actually returned, and whether the
difference is a bug. Karate is a small, readable test framework for exactly
that job: it turns an HTTP request and its assertions into a feature file that
another person can review.

This chapter is a CTF-style sequence. Each lab gives you a flag, but the flag is
not the whole assessment. You also submit the feature file, the run report, and
a short explanation. That is how the platform checks that you learned the
technique rather than copied a string.

## What you will be able to do

- read and write a Karate feature file;
- assert a status code, a JSON field, an array shape, and a data type;
- drive the same scenario with an Examples table;
- log in once, extract a token, and reuse it;
- write a negative test and explain a failing security assertion;
- produce a run report that an instructor or reviewer can audit.

## Before you start

You need a terminal and Java 17 or newer. Check Java first:

```bash
java -version
```

Download the standalone Karate jar once:

```bash
curl -L -o karate.jar \
  https://github.com/karatelabs/karate/releases/download/v1.5.1/karate-1.5.1.jar
```

Run a feature:

```bash
java -jar karate.jar features/
```

The HTML report is written to `target/karate-reports/karate-summary.html`.
Relative paths inside a feature resolve from the feature file, so keep the
`features/` folder and `karate.jar` next to each other unless you pass an
absolute path.

Karate's official documentation is at <https://docs.karatelabs.io>. The
standalone jar is published on the
[Karate releases page](https://github.com/karatelabs/karate/releases).

## The lab sequence

| Lab | Technique | Flag source |
|---|---|---|
| [Your First API Test](01_First_Karate_Feature.md) | Feature, Scenario, url, path, method, status, match | `flag` field in `/api/v1/jobs` |
| [Assertions and Data Tables](02_Assertions_And_Data_Tables.md) | `match`, `Scenario Outline`, `Examples`, fuzzy types | `flag` field in `/api/v1/echo?value=karate` |
| [Authenticate Once, Reuse Everywhere](03_Authentication_And_Reuse.md) | JSON login, token extraction, header reuse, `callSingle` | `flag` field in `/api/v1/me` |
| [Negative Tests and Evidence Reports](04_Negative_Tests_And_Evidence.md) | `status 403`, tags, a failing security assertion, a finding | `flag` field in the leaked account response |

## How the CTF part works

- Each lab has one flag. Submit it on the lab page after you have a passing
  feature and a report.
- Hints unlock over time. The first hint is free. Using a hint is allowed.
- The automated test steps prove the target is healthy and the challenge is
  solvable; they do not replace your feature.
- Your evidence is the feature file, the report, and the explanation. A flag
  without evidence is an incomplete lab.

## Safety

Every account, job, product, and balance in these labs is fictional. The target
is a local container with no external network access. Never run these tests
against a real service. If you find a real secret, stop and tell a facilitator.
