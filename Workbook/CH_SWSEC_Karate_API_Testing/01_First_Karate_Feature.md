# Your First API Test

**Lab:** `software-security-3-1-first-karate-feature`  
**Time:** about 25 minutes  
**Target:** `http://api.lab:8080`

## Scenario

Northwind Training runs a small jobs board. The quality engineer wants the
smallest useful smoke test: call the jobs endpoint, prove it answers, and prove
the first job is the one the team expects.

The service is a fictional, isolated target. You cannot reach the public
internet from it.

## What you will learn

- how a Karate feature maps to one HTTP request;
- the five steps every first test needs: `url`, `path`, `method`, `status`,
  `match`;
- how to run one feature and read the summary;
- why a flag is evidence only when the assertion around it is understood.

## Step 1 — look at the response

Start with the browser or `curl`:

```bash
curl -s http://api.lab:8080/api/v1/health
curl -s http://api.lab:8080/api/v1/jobs
```

You should see a JSON object with `jobs` and a `flag` field. Read the shape
before writing the test. Notice that `jobs` is an array and each job has
`id`, `title`, `location`, and `team`.

## Step 2 — write the feature

Create `features/jobs.feature`:

```gherkin
Feature: Northwind jobs API

  Scenario: the jobs board answers with the expected first role
    * url 'http://api.lab:8080'
    * path 'api/v1/jobs'
    * method get
    * status 200
    * match response.jobs[0].title == 'Junior API Tester'
    * match response.jobs == '#[2]'
```

Line by line:

| Step | What it does |
|---|---|
| `url` | sets the base URL for the scenario |
| `path` | appends the endpoint path |
| `method get` | sends a GET request |
| `status 200` | fails the scenario if the status is not 200 |
| `match ... ==` | compares the value exactly |
| `'#[2]'` | asserts that `jobs` has exactly two elements |

## Step 3 — run it

```bash
java -jar karate.jar features/jobs.feature
```

Expected summary:

```text
scenarios: 1 | passed: 1 | failed: 0
```

If the run fails, read the first failing line. Karate prints the actual and
expected values. Fix one step at a time; do not weaken an assertion to make a
red run green.

## Step 4 — capture the flag

The `flag` field in the jobs response is your flag. Submit it on the lab page
after the run passes. Do not copy it into your notes or a shared document; the
platform records the submission.

## Step 5 — prove the lesson

Add one more assertion that matters to the business, for example:

```gherkin
* match response.jobs[1].team == 'Product Security'
```

Then answer:

1. What would this test catch if the endpoint returned `200` with an empty
   `jobs` array?
2. Which assertion proves the endpoint answered, and which proves it answered
   correctly?
3. Why is a passing test better evidence than a screenshot of the JSON?

## Evidence to submit

- `features/jobs.feature`
- the run summary or the HTML report path
- a one-sentence explanation of what `status 200` proves and what it does not
  prove

## Defensive takeaway

A smoke test is a control. Assert the status, the shape, and one business fact
so a broken deploy fails the test instead of silently returning an empty page.
