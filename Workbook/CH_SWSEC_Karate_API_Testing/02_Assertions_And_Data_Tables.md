# Assertions and Data Tables

**Lab:** `software-security-3-2-assertions-and-examples`  
**Time:** about 35 minutes  
**Target:** `http://api.lab:8080`

## Scenario

The catalogue team keeps breaking the same two things: the echo endpoint
changes shape, and the product list loses a row during a merge. They want one
small feature that proves the contract for a table of inputs and then checks a
product by name.

The echo endpoint returns the flag only for the exact value `karate`. That is
deliberate: the flag is attached to the row your Examples table proves.

## What you will learn

- `match` for equality, containment, type, and array shape;
- `Scenario Outline` and `Examples`;
- how to read a failed assertion;
- how a negative example proves a boundary instead of only the happy path.

## Step 1 — read both endpoints

```bash
curl -s 'http://api.lab:8080/api/v1/echo?value=karate'
curl -s http://api.lab:8080/api/v1/products
```

The echo response has `value`, `length`, and — only for `karate` — `flag`.
The catalogue response has a `products` array.

## Step 2 — write the data-driven feature

Create `features/catalogue.feature`:

```gherkin
Feature: Northwind catalogue contract

  Scenario Outline: echo returns the value it was given
    * url 'http://api.lab:8080'
    * path 'api/v1/echo'
    * param value = '<value>'
    * method get
    * status 200
    * match response.value == '<value>'
    * match response.length == '#number'

    Examples:
      | value  |
      | karate |
      | kettle |
      | KARATE |

  Scenario: the catalogue has the expected shape and product
    * url 'http://api.lab:8080'
    * path 'api/v1/products'
    * method get
    * status 200
    * match response.products == '#[3]'
    * match response.products[1] contains { name: 'Karate Gi', price: 65 }
    * match each response.products contains { id: '#string', price: '#number' }
```

Why these assertions:

| Assertion | What it proves |
|---|---|
| `match response.value == '<value>'` | the service echoes the input exactly, including case |
| `match response.length == '#number'` | the field exists and is numeric, without pinning a value |
| `'#[3]'` | the array has exactly three elements |
| `contains { ... }` | the object has at least these fields with these values |
| `match each ... contains { ... }` | every element has the required type shape |

## Step 3 — run it

```bash
java -jar karate.jar features/catalogue.feature
```

You should see four scenarios pass: three outline rows and one catalogue
scenario. If a row fails, check the exact case. `karate` and `KARATE` are
different inputs and the service treats them differently.

## Step 4 — capture the flag

The `karate` row returns the `flag` field. Submit it on the lab page after the
whole feature passes. Do not copy it into a shared document.

## Step 5 — add a negative example

Add a row that proves a boundary, for example an empty value:

```gherkin
      | |
```

Then assert what the service actually does with it. The point is not to make
the service fail; it is to make the test describe the boundary explicitly.

Answer:

1. What is the difference between `match response.products == '#[3]'` and
   `match response.products[0].name == 'Kettle'`?
2. Why is `'#number'` safer than `65` when the price can change?
3. What did the failing assertion tell you that a print statement would not?

## Evidence to submit

- `features/catalogue.feature` with at least one Scenario Outline and one
  negative or boundary example
- the run summary
- a one-paragraph explanation of why the table is better than three copied
  scenarios

## Defensive takeaway

Assertions are executable requirements. A table turns one happy-path check into
a small contract suite, and a negative example proves the boundary. Keep the
table small enough to review and make each row explain a real input class.
