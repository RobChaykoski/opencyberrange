# Exercise 3.1 -- The Public Banner

**Track:** OSINT · **Difficulty:** Beginner · **Estimated time:** 25 minutes

**Framework alignment:** [MITRE ATT&CK](https://attack.mitre.org/) Reconnaissance
T1596.005 Search Open Technical Databases: Scan Databases and T1590.005 Gather
Victim Network Information: IP Addresses.

## Before You Begin

- Launch **The Public Banner** and open the **Active Lab View**.
- Note the target address for the synthetic Shodan mirror, for example
  `http://10.100.13.86:8080/`. Your session uses a different `/24`.
- A phone is recommended. The mirror is a normal web page, so any browser works.
- The mirror is synthetic. It contains fictional hosts and never queries the
  real internet or the real Shodan service.

## Scenario

Kestrel Ridge has a public build server. A synthetic Shodan-style mirror has
indexed the fictional public hosts for this exercise. The build server leaks more
than it should in its service banner.

Use your phone to open the mirror, search for Kestrel Ridge, and find the build
host. Read the banner and recover the marker.

## Objectives

1. Search the mirror by organisation.
2. Narrow the results by product or port.
3. Read a service banner for exposed metadata.
4. Recover the marker from the verbose banner.

## Background: scan databases and banners

Public scan databases index services that are reachable from the internet. A
result can include the IP address, port, product, hostname, organisation, and the
raw banner the service returned.

Banners are useful to defenders and attackers alike. A banner that includes a
product version, an internal hostname, a build number, or a custom header gives a
researcher a starting point. The defensive lesson is to return the minimum banner
needed for the service to work and to monitor your own public footprint.

!!! warning "Synthetic data only"
    This mirror is a training simulation. Do not query the real Shodan service
    for third-party hosts. Real scan data can expose real systems and is not
    reproducible for a class.

## Walkthrough

### 1. Open the mirror

Open the mirror address from the Active Lab View. The page explains the supported
filters: `org`, `hostname`, `port`, `product`, and `country`.

### 2. Search by organisation

Enter:

```text
org:"Kestrel Ridge"
```

The mirror returns three fictional hosts. Look for the build server.

### 3. Narrow by product or port

Try:

```text
product:Jenkins
```

or:

```text
port:8080
```

The build host is `build.kestrel-ridge.example` on port `8080`.

### 4. Read the banner

Open the build host result and read the raw banner. It contains an
`X-Build-Marker` header. That value is the flag.

### 5. Submit the flag

Copy the marker exactly and submit it on the exercise page.

## Analysis Questions

1. Which fields in the result helped you find the build host?
2. What does the banner reveal that a normal web page would not?
3. Why is a verbose banner useful to an attacker?
4. What would you remove from the banner before exposing the service?
5. Why is a synthetic mirror safer for this lesson than the real Shodan service?

## Defensive Takeaways

- Return the minimum banner needed for the service to work.
- Remove product versions, build numbers, internal hostnames, and custom headers
  that are not required.
- Monitor your own public scan results and certificate transparency entries.
- Treat public scan data as a permanent record.
- Do not use real scan data to target third-party systems.

## If You Get Stuck

- Start broad: `org:"Kestrel Ridge"`.
- If the query returns no matches, check the spelling and the quotes.
- The marker is in the raw banner, not in the page heading.
- If the phone cannot reach the target, use the address in your Active Lab View.
