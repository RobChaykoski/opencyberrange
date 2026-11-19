"""NICE Framework ingestion and mapping tests."""

from app.models import LabNiceComponent
from app.services import nice_framework

SAMPLE = {
    "documents": [{"version": "2.2.0"}],
    "elements": [
        {
            "element_type": "category",
            "element_identifier": "PD",
            "title": "PROTECTION and DEFENSE",
            "text": "Defensive work.",
        },
        {
            "element_type": "work_role",
            "element_identifier": "PD-WRL-001",
            "title": "Defensive Cybersecurity",
            "text": "Defends systems.",
        },
        {
            "element_type": "task",
            "element_identifier": "T0001",
            "title": "",
            "text": "Analyze alerts.",
        },
        {
            "element_type": "knowledge",
            "element_identifier": "K0001",
            "title": "",
            "text": "Knowledge of network security.",
        },
        {
            "element_type": "skill",
            "element_identifier": "S0001",
            "title": "",
            "text": "Skill in triage.",
        },
    ],
    "relationships": [
        {
            "source_element_identifier": "PD-WRL-001",
            "dest_element_identifier": "T0001",
        },
        {
            "source_element_identifier": "PD-WRL-001",
            "dest_element_identifier": "K0001",
        },
        {
            "source_element_identifier": "PD-WRL-001",
            "dest_element_identifier": "S0001",
        },
    ],
}


def test_prepare_official_shape():
    prepared = nice_framework._prepare(SAMPLE)
    assert prepared["version"] == "2.2.0"
    work_role = next(
        item for item in prepared["components"] if item["component_type"] == "work_role"
    )
    assert work_role["code"] == "PD-WRL-001"
    assert work_role["category_name"] == "PROTECTION and DEFENSE"
    assert len(prepared["links"]) == 3


def test_bundled_snapshot_has_expected_counts():
    prepared = nice_framework._prepare(nice_framework._load_snapshot())
    counts = {
        item_type: sum(
            1
            for item in prepared["components"]
            if item["component_type"] == item_type
        )
        for item_type in nice_framework.COMPONENT_TYPES
    }
    assert prepared["version"].startswith("2.2")
    assert counts["work_role"] == 42
    assert counts["task"] == 962
    assert counts["knowledge"] == 693
    assert counts["skill"] == 556
    assert len(prepared["links"]) == 5410


def test_ingest_and_map_lab(db_session, test_lab):
    db_session.query(LabNiceComponent).filter(
        LabNiceComponent.lab_id == test_lab.id
    ).delete()
    db_session.commit()
    nice_framework.ingest_payload(db_session, SAMPLE, source="test")
    assert nice_framework.status(db_session)["version"] == "2.2.0"

    mapping = nice_framework.set_lab_mappings(
        db_session,
        lab_id=test_lab.id,
        selections={
            "work_role": ["PD-WRL-001"],
            "task": ["T0001"],
            "knowledge": ["K0001"],
            "skill": ["S0001"],
        },
        created_by_id=None,
    )
    assert mapping["work_role"][0]["code"] == "PD-WRL-001"
    assert mapping["task"][0]["code"] == "T0001"

    tasks = nice_framework.list_components(
        db_session,
        component_type="task",
        work_role_code="PD-WRL-001",
    )
    assert tasks["total"] == 1
    assert tasks["items"][0]["code"] == "T0001"
