# Chapter Review: API Testing with Karate

Use this page to check your evidence before you submit the chapter. The flags
are necessary but not sufficient: an instructor should be able to read your
feature files and your finding without asking you what happened.

## Knowledge check

1. What does each of these Karate steps do?
   - `* url`
   - `* path`
   - `* method`
   - `* status`
   - `* match`
2. What is the difference between a status assertion and a body assertion?
3. When would you use `match contains` instead of `match ==`?
4. What does `'#[3]'` assert, and why is it useful?
5. What does `karate.callSingle` cache, and why does that matter for a login?
6. Why is a failing `status 403` test a finding rather than a broken test?
7. What does a report add that a screenshot of a passing run does not?

## Evidence checklist

- [ ] Lab 1: `features/jobs.feature` passes and includes a business assertion.
- [ ] Lab 2: `features/catalogue.feature` has a Scenario Outline, an Examples
      table, and a boundary or negative row.
- [ ] Lab 3: `features/login.feature` and `features/profile.feature` pass,
      including the missing-token scenario.
- [ ] Lab 4: `features/accounts.feature` contains the failing `403` test, and
      you kept the report.
- [ ] All four flags are submitted.
- [ ] The finding table for Lab 4 is complete.
- [ ] You can explain one control change that would prevent the BOLA bug.

## Review questions

### Design

The jobs and catalogue APIs are small on purpose. What would you add to the
suite before trusting it in a release gate?

### Security

The account endpoint authenticates the caller but does not authorize the
object. Name two places the check could live and one trade-off for each.

### Evidence

A reviewer asks, "How do you know the test failed because of the service and not
because of the test?" Write the two-line answer you would give, using the
report.

## Stretch exercise

Create a `karate-config.js` for the chapter:

```javascript
function fn() {
  return {
    baseUrl: 'http://api.lab:8080'
  };
}
```

Then replace the hard-coded URL in each feature with `baseUrl`. Run the suite
from a different working directory and confirm it still passes. This is how a
suite becomes portable between a laptop, CI, and a lab range.

## Chapter score

| Criterion | Weight | Evidence |
|---|---:|---|
| Features run and assert the intended behaviour | 30 | Four passing features, one intentional security failure |
| Data-driven and reusable structure | 20 | Scenario Outline, Examples, shared login |
| Negative and security testing | 20 | 401 and 403 expectations, BOLA finding |
| Evidence quality | 20 | Reports, finding table, explanations |
| Safety and least privilege | 10 | No real data, no real target, token handling |

A complete chapter is 80 or above with every evidence item present. The flags
are required, but they do not replace the evidence.
