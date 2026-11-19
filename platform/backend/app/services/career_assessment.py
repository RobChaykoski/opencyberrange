"""Short career-direction check.

This is a reflection tool, not a personality test. Eight scenario questions map
to four work clusters: discovery, construction, operations, and people. The
result is a conversation starter, not a hiring decision.
"""

from __future__ import annotations

CLUSTERS = {
    "discovery": {
        "label": "Discovery and evidence",
        "description": "Research, investigation, intelligence, and finding the story in the evidence.",
        "directions": ["OSINT", "Threat intelligence", "Detection engineering", "Incident investigation"],
    },
    "construction": {
        "label": "Construction and design",
        "description": "Building, automating, engineering, and designing systems that hold up.",
        "directions": ["AppSec", "DevSecOps", "Cloud security", "Security architecture"],
    },
    "operations": {
        "label": "Security operations",
        "description": "Monitoring, hunting, responding, and keeping the defence working under pressure.",
        "directions": ["SOC analyst", "Threat hunter", "Incident responder", "Detection engineer"],
    },
    "people": {
        "label": "People and organisation",
        "description": "Explaining risk, coordinating teams, and connecting security to the business.",
        "directions": ["GRC", "Security consulting", "Security architecture", "Security leadership"],
    },
}

QUESTIONS = [
    {
        "id": "new-tool",
        "prompt": "A new security tool appears. What do you do first?",
        "options": [
            ("Read the docs and explore what it can reveal", "discovery"),
            ("Deploy it in a lab and see how it works", "construction"),
            ("Check whether it improves detection or response", "operations"),
            ("Ask the team what problem it should solve", "people"),
        ],
    },
    {
        "id": "satisfying-task",
        "prompt": "Which task feels most satisfying?",
        "options": [
            ("Tracing an attacker through logs and evidence", "operations"),
            ("Building a script that removes a repetitive task", "construction"),
            ("Researching a threat and its public footprint", "discovery"),
            ("Explaining a risk to a decision-maker", "people"),
        ],
    },
    {
        "id": "broken-lab",
        "prompt": "A lab environment is broken. What do you try first?",
        "options": [
            ("Inspect the logs and narrow the failure", "operations"),
            ("Fix the container or configuration", "construction"),
            ("Find another source or a different route", "discovery"),
            ("Ask a peer what they are seeing", "people"),
        ],
    },
    {
        "id": "artifact",
        "prompt": "Which artifact would you rather produce?",
        "options": [
            ("A threat-hunting report with hypotheses and evidence", "discovery"),
            ("A working automation script with tests", "construction"),
            ("An incident timeline and containment record", "operations"),
            ("An executive brief with impact and decisions", "people"),
        ],
    },
    {
        "id": "team-role",
        "prompt": "In a team incident, which role appeals most?",
        "options": [
            ("Detection analyst", "operations"),
            ("Cloud engineer", "construction"),
            ("Threat-intelligence researcher", "discovery"),
            ("Incident commander", "people"),
        ],
    },
    {
        "id": "learning",
        "prompt": "How do you prefer to learn?",
        "options": [
            ("Explore references and follow a question", "discovery"),
            ("Build a small project", "construction"),
            ("Run a drill or a live exercise", "operations"),
            ("Discuss it with peers", "people"),
        ],
    },
    {
        "id": "metric",
        "prompt": "Which metric would you most want to improve?",
        "options": [
            ("New sources explored and questions answered", "discovery"),
            ("Manual steps removed by automation", "construction"),
            ("Mean time to detect and respond", "operations"),
            ("Stakeholder confidence and clarity", "people"),
        ],
    },
    {
        "id": "programme-gap",
        "prompt": "What would you improve first in a security programme?",
        "options": [
            ("Visibility and evidence", "operations"),
            ("Automation and engineering", "construction"),
            ("Research and threat understanding", "discovery"),
            ("Communication and governance", "people"),
        ],
    },
]


def public_questions() -> list[dict]:
    return [
        {
            "id": question["id"],
            "prompt": question["prompt"],
            "options": [
                {"index": index, "label": label}
                for index, (label, _cluster) in enumerate(question["options"])
            ],
        }
        for question in QUESTIONS
    ]


def score_answers(answers: dict[str, int]) -> dict:
    by_id = {question["id"]: question for question in QUESTIONS}
    counts = {key: 0 for key in CLUSTERS}
    answered = 0

    for question_id, option_index in answers.items():
        question = by_id.get(question_id)
        if question is None:
            continue
        try:
            index = int(option_index)
        except (TypeError, ValueError):
            continue
        options = question["options"]
        if index < 0 or index >= len(options):
            continue
        cluster = options[index][1]
        counts[cluster] += 1
        answered += 1

    if not answered:
        raise ValueError("No valid answers were supplied.")

    scores = {
        key: {
            "id": key,
            "label": cluster["label"],
            "description": cluster["description"],
            "score": round(counts[key] / answered * 100),
            "answers": counts[key],
            "directions": cluster["directions"],
        }
        for key, cluster in CLUSTERS.items()
    }
    ordered = sorted(scores.values(), key=lambda row: (-row["score"], row["label"]))
    return {
        "answered": answered,
        "total_questions": len(QUESTIONS),
        "scores": ordered,
        "strongest": ordered[0]["id"] if ordered else None,
        "growth": ordered[-1]["id"] if ordered else None,
        "note": (
            "This is a short reflection tool, not a personality test or a hiring "
            "decision. Use it to choose a direction to explore, not to narrow "
            "your options."
        ),
    }
