"""Career Atlas: practice-linked career families and salary context.

The atlas is a *conversation aid*, not a job prediction. It links the existing
Cyber DNA practice evidence to broad career families, then shows national
salary bands from official public labour-market data.

Rules:

* A family unlocks from practice evidence. It is never a claim that the learner
  is ready for the role.
* Salary figures are national planning ranges, not offers, and are tagged with
  their source, currency, region, and as-of date.
* No learner is ranked, and no family is presented as the "best" career.
* A learner with no evidence sees a positive next step, never a negative label.

Data version ``2026.1``. Salary values are annual. Canadian values are
annualised from the national median hourly wage at 2,080 hours; US values are
the national annual 10th/50th/90th percentiles.
"""

from __future__ import annotations

from statistics import mean

from app.services.skill_dna import DIMENSION_BY_KEY, DIMENSIONS

CAREER_ATLAS_VERSION = "2026.1"

SALARY_SOURCES = {
    "ca_jobbank": {
        "key": "ca_jobbank",
        "label": "Canada Job Bank",
        "detail": (
            "Statistics Canada Labour Force Survey, 2023-2024 reference period; "
            "Job Bank wages updated 19 November 2025."
        ),
        "url": "https://www.jobbank.gc.ca/trend-analysis/search-wages",
        "as_of": "2025-11-19",
        "currency": "CAD",
        "basis": "Annualised from the national median hourly wage at 2,080 hours.",
    },
    "us_bls": {
        "key": "us_bls",
        "label": "U.S. Bureau of Labor Statistics OEWS",
        "detail": (
            "Occupational Employment and Wage Statistics, May 2025 release; "
            "national annual percentiles via O*NET OnLine."
        ),
        "url": "https://www.bls.gov/oes/",
        "as_of": "2026-05-15",
        "currency": "USD",
        "basis": (
            "National annual 10th percentile (low), 50th percentile (median), "
            "and 90th percentile (high)."
        ),
    },
}

REGIONS = (
    {"key": "ca", "label": "Canada", "currency": "CAD", "source": "ca_jobbank"},
    {"key": "us", "label": "United States", "currency": "USD", "source": "us_bls"},
)


def _band(
    *,
    ca_low: int,
    ca_median: int,
    ca_high: int,
    ca_occupation: str,
    ca_url: str,
    us_low: int,
    us_median: int,
    us_high: int,
    us_occupation: str,
    us_url: str,
) -> dict:
    return {
        "ca": {
            "low": ca_low,
            "median": ca_median,
            "high": ca_high,
            "occupation": ca_occupation,
            "source": "ca_jobbank",
            "url": ca_url,
        },
        "us": {
            "low": us_low,
            "median": us_median,
            "high": us_high,
            "occupation": us_occupation,
            "source": "us_bls",
            "url": us_url,
        },
    }


# National bands. Canadian annual values are hourly x 2,080, rounded to the
# nearest CAD 100. US values are the published annual percentiles.
SALARY_BANDS = {
    "cyber_specialist": _band(
        ca_low=62400,
        ca_median=103000,
        ca_high=150000,
        ca_occupation="Cybersecurity specialists (NOC 21220)",
        ca_url="https://www.jobbank.gc.ca/wagereport/occupation/22512",
        us_low=75090,
        us_median=129180,
        us_high=199850,
        us_occupation="Information security analysts (SOC 15-1212)",
        us_url="https://www.onetonline.org/link/localwages/15-1212.00",
    ),
    "systems_specialist": _band(
        ca_low=60000,
        ca_median=96000,
        ca_high=142900,
        ca_occupation="Information systems specialists (NOC 21222)",
        ca_url="https://www.jobbank.gc.ca/wagereport/occupation/22496",
        us_low=62640,
        us_median=99130,
        us_high=155050,
        us_occupation="Network and computer systems administrators (SOC 15-1244)",
        us_url="https://www.onetonline.org/link/localwages/15-1244.00",
    ),
    "software_engineer": _band(
        ca_low=72800,
        ca_median=117500,
        ca_high=190000,
        ca_occupation="Software engineers and designers (NOC 21231)",
        ca_url="https://www.jobbank.gc.ca/wagereport/occupation/5485",
        us_low=82460,
        us_median=135980,
        us_high=214670,
        us_occupation="Software developers (SOC 15-1252)",
        us_url="https://www.onetonline.org/link/localwages/15-1252.00",
    ),
    "cis_manager": _band(
        ca_low=91000,
        ca_median=138700,
        ca_high=215000,
        ca_occupation="Computer and information systems managers (NOC 20012)",
        ca_url="https://www.jobbank.gc.ca/wagereport/occupation/1465",
        us_low=107550,
        us_median=175140,
        us_high=297510,
        us_occupation="Computer and information systems managers (SOC 11-3021)",
        us_url="https://www.onetonline.org/link/localwages/11-3021.00",
    ),
    "data_scientist": _band(
        ca_low=62400,
        ca_median=96000,
        ca_high=145100,
        ca_occupation="Data scientists (NOC 21211)",
        ca_url="https://www.jobbank.gc.ca/wagereport/occupation/227147",
        us_low=67240,
        us_median=120230,
        us_high=199130,
        us_occupation="Data scientists (SOC 15-2051)",
        us_url="https://www.onetonline.org/link/localwages/15-2051.00",
    ),
    "network_architect": _band(
        ca_low=60000,
        ca_median=96000,
        ca_high=142900,
        ca_occupation="Information systems specialists (NOC 21222)",
        ca_url="https://www.jobbank.gc.ca/wagereport/occupation/22496",
        us_low=79900,
        us_median=134050,
        us_high=202680,
        us_occupation="Computer network architects (SOC 15-1241)",
        us_url="https://www.onetonline.org/link/localwages/15-1241.00",
    ),
    "grc_analyst": _band(
        ca_low=60000,
        ca_median=96000,
        ca_high=142900,
        ca_occupation="Information systems specialists (NOC 21222)",
        ca_url="https://www.jobbank.gc.ca/wagereport/occupation/22496",
        us_low=60640,
        us_median=101860,
        us_high=171640,
        us_occupation="Management analysts (SOC 13-1111)",
        us_url="https://www.onetonline.org/link/localwages/13-1111.00",
    ),
    "support_technician": _band(
        ca_low=43700,
        ca_median=74900,
        ca_high=114400,
        ca_occupation="Computer network and web technicians (NOC 22220)",
        ca_url="https://www.jobbank.gc.ca/wagereport/occupation/24514",
        us_low=47120,
        us_median=76220,
        us_high=127780,
        us_occupation="Computer network support specialists (SOC 15-1231)",
        us_url="https://www.onetonline.org/link/localwages/15-1231.00",
    ),
}


def _role(title: str, level: str, summary: str, band: str) -> dict:
    return {
        "title": title,
        "level": level,
        "summary": summary,
        "salary_band": band,
    }


CAREER_FAMILIES = (
    {
        "key": "intel",
        "label": "Threat Intelligence / OSINT",
        "summary": (
            "Find, verify, and explain public evidence: footprinting, open-source "
            "research, attribution, and intelligence products."
        ),
        "branch": "explorer",
        "affinity_key": "investigative",
        "dimension_keys": ("explorer", "investigator"),
        "certification_key": "osint",
        "next_step": (
            "Build one short intelligence product: a question, three verified "
            "sources, a confidence note, and a recommendation."
        ),
        "roles": (
            _role(
                "OSINT Analyst",
                "entry",
                "Collect and verify public-source evidence for investigations.",
                "cyber_specialist",
            ),
            _role(
                "Threat Intelligence Analyst",
                "core",
                "Turn adversary and sector reporting into decisions for defenders.",
                "cyber_specialist",
            ),
            _role(
                "Intelligence Lead",
                "advanced",
                "Set collection priorities and brief technical and executive audiences.",
                "cis_manager",
            ),
        ),
    },
    {
        "key": "appsec",
        "label": "Application Security / Product Security",
        "summary": (
            "Build software that resists abuse: secure design, code review, "
            "dependency and supply-chain assurance, and product threat modelling."
        ),
        "branch": "builder",
        "affinity_key": "offensive",
        "dimension_keys": ("builder", "tester"),
        "certification_key": "software-security",
        "next_step": (
            "Take one completed web exercise and write a secure-design note: the "
            "trust boundary, the failure, the fix, and the test that would catch it."
        ),
        "roles": (
            _role(
                "AppSec Analyst",
                "entry",
                "Review changes, triage findings, and help teams reproduce issues.",
                "software_engineer",
            ),
            _role(
                "AppSec Engineer",
                "core",
                "Embed secure design and testing into the delivery pipeline.",
                "software_engineer",
            ),
            _role(
                "Product Security Architect",
                "advanced",
                "Set product security architecture and assurance across a portfolio.",
                "network_architect",
            ),
        ),
    },
    {
        "key": "cloud",
        "label": "Cloud Security",
        "summary": (
            "Secure cloud identity, networks, workloads, and data across shared "
            "responsibility boundaries."
        ),
        "branch": "builder",
        "affinity_key": "defensive",
        "dimension_keys": ("builder", "defender"),
        "certification_key": "network",
        "next_step": (
            "Map one lab to a cloud control: identity, network boundary, logging, "
            "or data protection. Name the control and the evidence it produces."
        ),
        "roles": (
            _role(
                "Cloud Security Analyst",
                "entry",
                "Assess cloud configuration and triage identity and exposure findings.",
                "systems_specialist",
            ),
            _role(
                "Cloud Security Engineer",
                "core",
                "Build guardrails, detection, and secure landing zones.",
                "software_engineer",
            ),
            _role(
                "Cloud Security Architect",
                "advanced",
                "Design multi-account security architecture and control ownership.",
                "network_architect",
            ),
        ),
    },
    {
        "key": "identity",
        "label": "Identity & Access Management",
        "summary": (
            "Make sure the right people and services reach the right resources, and "
            "that the evidence of that decision is trustworthy."
        ),
        "branch": "builder",
        "affinity_key": None,
        "dimension_keys": ("builder", "defender"),
        "certification_key": "identity",
        "next_step": (
            "Draw the identity lifecycle for one lab account: join, authenticate, "
            "authorise, review, and leave."
        ),
        "roles": (
            _role(
                "IAM Analyst",
                "entry",
                "Run access reviews, joiner-mover-leaver tasks, and MFA support.",
                "systems_specialist",
            ),
            _role(
                "IAM Engineer",
                "core",
                "Implement federation, conditional access, and privileged access.",
                "software_engineer",
            ),
            _role(
                "IAM Architect",
                "advanced",
                "Design identity architecture and the control model across systems.",
                "network_architect",
            ),
        ),
    },
    {
        "key": "offensive",
        "label": "Offensive Security / Penetration Testing",
        "summary": (
            "Authorised testing inside isolated labs: reconnaissance, exploitation, "
            "privilege escalation, post-exploitation, and clear reporting."
        ),
        "branch": "tester",
        "affinity_key": "offensive",
        "dimension_keys": ("tester", "explorer"),
        "certification_key": "web",
        "next_step": (
            "Pair one exploitation exercise with a scoping note, rules of engagement, "
            "and a short finding written for a system owner."
        ),
        "roles": (
            _role(
                "Junior Penetration Tester",
                "entry",
                "Run scoped checks and document reproducible findings.",
                "cyber_specialist",
            ),
            _role(
                "Penetration Tester",
                "core",
                "Plan and deliver authorised assessments with clear evidence.",
                "cyber_specialist",
            ),
            _role(
                "Red Team Operator",
                "advanced",
                "Test detection and response through adversary simulation.",
                "cyber_specialist",
            ),
            _role(
                "Offensive Security Consultant",
                "advanced",
                "Lead engagements, manage risk, and brief executives.",
                "cis_manager",
            ),
        ),
    },
    {
        "key": "defensive",
        "label": "Defensive Security / SOC",
        "summary": (
            "Detect, triage, contain, and recover: monitoring, detection engineering, "
            "incident response, and network defence."
        ),
        "branch": "defender",
        "affinity_key": "defensive",
        "dimension_keys": ("defender", "leader"),
        "certification_key": "network",
        "next_step": (
            "Take one alert-style exercise and write the triage path: signal, "
            "hypothesis, evidence, decision, and follow-up."
        ),
        "roles": (
            _role(
                "SOC Analyst (Tier 1)",
                "entry",
                "Triage alerts, gather evidence, and escalate with a clear record.",
                "cyber_specialist",
            ),
            _role(
                "Detection Engineer",
                "core",
                "Turn adversary behaviour into reliable, tested detections.",
                "systems_specialist",
            ),
            _role(
                "Incident Responder",
                "core",
                "Coordinate containment, eradication, and recovery under pressure.",
                "cyber_specialist",
            ),
            _role(
                "Security Operations Manager",
                "advanced",
                "Run the detection and response programme, metrics, and people.",
                "cis_manager",
            ),
        ),
    },
    {
        "key": "ot",
        "label": "OT / ICS Security",
        "summary": (
            "Protect industrial and connected systems where availability and safety "
            "come before conventional IT priorities."
        ),
        "branch": "defender",
        "affinity_key": None,
        "dimension_keys": ("defender", "investigator"),
        "certification_key": "ot",
        "next_step": (
            "For one OT exercise, list the safety, availability, and security "
            "trade-offs before proposing a control."
        ),
        "roles": (
            _role(
                "OT Security Analyst",
                "entry",
                "Monitor OT estates and translate alerts into plant-safe actions.",
                "cyber_specialist",
            ),
            _role(
                "ICS Security Engineer",
                "core",
                "Design segmentation and monitoring without disrupting operations.",
                "systems_specialist",
            ),
            _role(
                "OT Security Architect",
                "advanced",
                "Set the OT security architecture and safety-aware governance model.",
                "network_architect",
            ),
        ),
    },
    {
        "key": "investigative",
        "label": "DFIR / Investigation",
        "summary": (
            "Reconstruct what happened from evidence: forensics, timeline analysis, "
            "malware behaviour, and defensible findings."
        ),
        "branch": "investigator",
        "affinity_key": "investigative",
        "dimension_keys": ("investigator", "defender"),
        "certification_key": "forensics",
        "next_step": (
            "Build a one-page timeline from a completed forensic exercise and mark "
            "which facts are observed, inferred, or unknown."
        ),
        "roles": (
            _role(
                "DFIR Analyst",
                "entry",
                "Preserve evidence, build timelines, and document findings.",
                "cyber_specialist",
            ),
            _role(
                "Forensic Examiner",
                "core",
                "Examine hosts, images, and artefacts with a defensible method.",
                "cyber_specialist",
            ),
            _role(
                "Threat Intelligence Analyst",
                "core",
                "Connect evidence to adversary behaviour and sector reporting.",
                "cyber_specialist",
            ),
            _role(
                "Malware Analyst",
                "advanced",
                "Analyse malicious code and explain behaviour to defenders.",
                "software_engineer",
            ),
        ),
    },
    {
        "key": "ai",
        "label": "AI Security",
        "summary": (
            "Assess AI systems for prompt injection, data exposure, model supply "
            "chain, misuse, and governance risk."
        ),
        "branch": "investigator",
        "affinity_key": None,
        "dimension_keys": ("investigator", "builder"),
        "certification_key": "ai",
        "next_step": (
            "Write a threat model for one AI feature: assets, trust boundaries, "
            "abuse cases, and one testable control."
        ),
        "roles": (
            _role(
                "AI Security Analyst",
                "entry",
                "Test AI features for prompt, data, and tool-use risk.",
                "data_scientist",
            ),
            _role(
                "AI Security Engineer",
                "core",
                "Build guardrails, evaluation, and monitoring for AI systems.",
                "software_engineer",
            ),
            _role(
                "AI Governance Lead",
                "advanced",
                "Set AI risk policy, evidence, and oversight across the organisation.",
                "cis_manager",
            ),
        ),
    },
    {
        "key": "leadership",
        "label": "Security Leadership / Education",
        "summary": (
            "Turn technical work into programme decisions: teaching, communication, "
            "risk, budgets, and team design."
        ),
        "branch": "leader",
        "affinity_key": "leadership",
        "dimension_keys": ("leader",),
        "certification_key": "general",
        "next_step": (
            "Present one completed lab to a non-specialist in five minutes: risk, "
            "evidence, decision, and what you would do next."
        ),
        "roles": (
            _role(
                "Security Awareness Coordinator",
                "entry",
                "Design and measure practical security education.",
                "grc_analyst",
            ),
            _role(
                "Security Programme Coordinator",
                "core",
                "Run the programme cadence, evidence, and cross-team dependencies.",
                "grc_analyst",
            ),
            _role(
                "Security Manager",
                "advanced",
                "Lead a security function, its risks, and its people.",
                "cis_manager",
            ),
            _role(
                "CISO",
                "advanced",
                "Own the security strategy and the executive risk conversation.",
                "cis_manager",
            ),
        ),
    },
    {
        "key": "grc",
        "label": "Governance, Risk & Compliance",
        "summary": (
            "Make risk visible and decisions defensible: policy, control mapping, "
            "audit evidence, privacy, and third-party risk."
        ),
        "branch": "leader",
        "affinity_key": None,
        "dimension_keys": ("leader", "investigator"),
        "certification_key": "general",
        "next_step": (
            "Map one completed lab to a control statement and the evidence an "
            "auditor could verify."
        ),
        "roles": (
            _role(
                "GRC Analyst",
                "entry",
                "Maintain risk registers, control evidence, and policy hygiene.",
                "grc_analyst",
            ),
            _role(
                "Risk & Compliance Specialist",
                "core",
                "Assess control design and translate regulation into practice.",
                "grc_analyst",
            ),
            _role(
                "Security GRC Manager",
                "advanced",
                "Lead risk, audit, privacy, and third-party assurance.",
                "cis_manager",
            ),
        ),
    },
)

FAMILY_BY_KEY = {family["key"]: family for family in CAREER_FAMILIES}
BRANCH_ORDER = tuple(spec.key for spec in DIMENSIONS)


def _match_score(family: dict, dna: dict) -> tuple[int, int, float]:
    affinities = {row["key"]: row for row in dna.get("affinities", [])}
    dimensions = {row["key"]: row for row in dna.get("dimensions", [])}
    affinity = affinities.get(family.get("affinity_key") or "")
    evidence_count = int((affinity or {}).get("evidence_count") or 0)
    dimension_scores = [
        float((dimensions.get(key) or {}).get("score") or 0)
        for key in family["dimension_keys"]
    ]
    dimension_avg = mean(dimension_scores) if dimension_scores else 0.0
    evidence_points = min(evidence_count, 6) / 6 * 60
    score = round(min(100.0, evidence_points + dimension_avg * 0.4))
    return score, evidence_count, dimension_avg


def _unlock_state(score: int) -> tuple[str, str]:
    if score >= 35:
        return "unlocked", "Unlocked by your practice evidence"
    if score >= 15:
        return "next", "One or two more labs in this branch unlocks it"
    return "locked", "Complete one or two labs in this branch to unlock"


def _salary_payload(band_key: str) -> dict:
    band = SALARY_BANDS[band_key]
    payload = {}
    for region in REGIONS:
        key = region["key"]
        row = band[key]
        source = SALARY_SOURCES[row["source"]]
        payload[key] = {
            "low": row["low"],
            "median": row["median"],
            "high": row["high"],
            "occupation": row["occupation"],
            "url": row["url"],
            "currency": source["currency"],
            "source_label": source["label"],
            "source_detail": source["detail"],
            "source_url": source["url"],
            "as_of": source["as_of"],
            "basis": source["basis"],
        }
    return payload


def build_career_atlas(
    dna: dict,
    next_labs: dict[str, dict] | None = None,
) -> dict:
    """Build the Career Atlas from an existing Cyber DNA payload.

    ``next_labs`` is an optional branch-to-exercise map from Momentum. It adds a
    concrete practice link to each branch without changing the matching rules.
    """
    next_labs = next_labs or {}
    dimensions = {row["key"]: row for row in dna.get("dimensions", [])}
    families = []
    for family in CAREER_FAMILIES:
        score, evidence_count, dimension_avg = _match_score(family, dna)
        state, hint = _unlock_state(score)
        roles = []
        for role in family["roles"]:
            roles.append(
                {
                    "title": role["title"],
                    "level": role["level"],
                    "summary": role["summary"],
                    "salary": _salary_payload(role["salary_band"]),
                }
            )
        families.append(
            {
                "key": family["key"],
                "label": family["label"],
                "summary": family["summary"],
                "branch": family["branch"],
                "branch_label": DIMENSION_BY_KEY[family["branch"]].label,
                "certification_key": family["certification_key"],
                "match_score": score,
                "evidence_count": evidence_count,
                "dimension_average": round(dimension_avg, 1),
                "unlock_state": state,
                "unlock_hint": hint,
                "next_step": family["next_step"],
                "roles": roles,
            }
        )

    families.sort(key=lambda row: (-row["match_score"], BRANCH_ORDER.index(row["branch"])))
    recommended = next(
        (row for row in families if row["match_score"] > 0),
        None,
    )
    if recommended is not None:
        recommended["recommended"] = True

    branches = []
    for key in BRANCH_ORDER:
        spec = DIMENSION_BY_KEY[key]
        branch_families = [
            row for row in families if row["branch"] == key
        ]
        branch_families.sort(key=lambda row: (-row["match_score"], row["label"]))
        branches.append(
            {
                "key": key,
                "label": spec.label,
                "class_name": spec.class_name,
                "score": int((dimensions.get(key) or {}).get("score") or 0),
                "tier": (dimensions.get(key) or {}).get("tier") or "Unranked",
                "next_lab": next_labs.get(key),
                "families": branch_families,
            }
        )

    unlocked = sum(1 for row in families if row["unlock_state"] == "unlocked")
    next_count = sum(1 for row in families if row["unlock_state"] == "next")
    locked = len(families) - unlocked - next_count

    return {
        "version": CAREER_ATLAS_VERSION,
        "regions": list(REGIONS),
        "sources": list(SALARY_SOURCES.values()),
        "summary": {
            "families": len(families),
            "unlocked": unlocked,
            "next": next_count,
            "locked": locked,
        },
        "branches": branches,
        "families": families,
        "recommended_family_key": (
            recommended["key"] if recommended is not None else None
        ),
        "disclaimer": (
            "Career families unlock from practice evidence. They are not a job "
            "prediction, a certification, or a ranking. Salary bands are national "
            "planning ranges from public labour-market data; they are not an offer "
            "and they change. Verify every figure and requirement with the source."
        ),
        "salary_note": (
            "Low, median, and high are national 10th, 50th, and 90th percentile "
            "planning points, not entry-level pay. They are not an offer or a "
            "starting salary. Regional, sector, and experience differences are "
            "large."
        ),
    }
