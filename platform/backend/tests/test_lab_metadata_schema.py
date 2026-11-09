"""Static checks for the canonical lab.yaml metadata schema."""
from pathlib import Path

import yaml

from app.scripts.standardize_lab_metadata import (
    AXIS_KEYS,
    LEGACY_KEYS,
    OUTCOME_INTRO,
    REQUIRED_KEYS,
    VAGUE_OUTCOME_RE,
    _validate,
)
from app.services.competency_model import mapping_for_lab
from app.services.mitre_mapping import validate_mapping

REPO_ROOT = Path(__file__).resolve().parents[3]
LABS_ROOT = REPO_ROOT / "platform" / "labs"


def _labs():
    return sorted(LABS_ROOT.glob("**/lab.yaml"))


def test_every_lab_has_the_canonical_metadata_header():
    files = _labs()
    assert len(files) >= 100, "lab catalog unexpectedly small"

    slugs = {path.parent.name for path in files}
    titles = set()
    problems = []

    for path in files:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        data = yaml.safe_load(text) or {}

        if f"# {OUTCOME_INTRO}\nlearning_outcomes:" not in text:
            problems.append(f"{path}: missing the '{OUTCOME_INTRO}' heading")

        missing = [key for key in REQUIRED_KEYS if key not in data]
        legacy = [key for key in LEGACY_KEYS if key in data]
        if missing:
            problems.append(f"{path}: missing {', '.join(missing)}")
        if legacy:
            problems.append(f"{path}: legacy keys {', '.join(legacy)}")
        if missing:
            continue

        outcomes = data.get("learning_outcomes") or []
        if not 3 <= len(outcomes) <= 5:
            problems.append(
                f"{path}: expected 3-5 learning outcomes, found {len(outcomes)}"
            )
        for outcome in outcomes:
            if VAGUE_OUTCOME_RE.match(outcome):
                problems.append(f"{path}: vague learning outcome {outcome!r}")
            if len(str(outcome).split()) < 3:
                problems.append(f"{path}: learning outcome too short {outcome!r}")

        metadata = {key: data[key] for key in REQUIRED_KEYS}
        for error in _validate(metadata):
            problems.append(f"{path}: {error}")

        mappings = data.get("mitre_attack") or []
        if not mappings:
            problems.append(f"{path}: mitre_attack must contain at least one mapping")
        for mapping in mappings:
            for error in validate_mapping(mapping):
                problems.append(f"{path}: {error}")

        unknown = set(metadata["mapped_skills"]) - set(AXIS_KEYS)
        if unknown:
            problems.append(f"{path}: unknown skills {sorted(unknown)}")

        unknown_prereqs = set(metadata["prerequisites"]) - slugs
        if unknown_prereqs:
            problems.append(f"{path}: unknown prerequisites {sorted(unknown_prereqs)}")

        if metadata["title"] in titles:
            problems.append(f"{path}: duplicate title {metadata['title']!r}")
        titles.add(metadata["title"])

        if any(
            outcome.lower().startswith(("capture the flag", "submit the flag"))
            for outcome in metadata["learning_outcomes"]
        ):
            problems.append(f"{path}: flag capture is not a learning outcome")

    assert not problems, "\n".join(problems)


def test_competency_mapping_uses_authored_skills():
    class LabStub:
        name = "Authored Mapping Lab"
        category = "general"
        difficulty = "beginner"
        level = None
        mapped_skills = '["web_api", "ai_security"]'

    mapping = mapping_for_lab(LabStub())
    assert mapping["weights"] == {"web_api": 0.5, "ai_security": 0.5}
