"""Certification question banks: mapping, sampling, and reference hygiene."""

from __future__ import annotations

from types import SimpleNamespace

from app.services import certification_quiz


def _lab(track_slug: str, name: str = "Exercise", category: str = "general"):
    return SimpleNamespace(
        name=name,
        slug=f"{track_slug}-1-1-demo",
        category=category,
        primary_competency=category,
        chapter_name=name,
        level=SimpleNamespace(
            track=SimpleNamespace(slug=track_slug, name=track_slug.title())
        ),
    )


def test_banks_are_valid_and_have_a_review_date():
    result = certification_quiz.validate_banks()
    assert result["ok"] is True
    assert result["questions"] >= 30
    assert result["pathways"] >= 8
    assert result["reviewed_at"]


def test_references_are_https_and_not_self_referencing():
    for pathway in certification_quiz.pathways():
        for question in pathway["questions"]:
            url = question["reference"]["url"]
            assert url.startswith("https://")
            assert not certification_quiz._is_self_reference(url)


def test_pathway_mapping_prefers_the_specific_pathway():
    assert certification_quiz.pathway_for_lab(_lab("network"))["id"] == "comptia-network-plus"
    assert certification_quiz.pathway_for_lab(_lab("linux"))["id"] == "comptia-linux-plus"
    assert certification_quiz.pathway_for_lab(_lab("web"))["id"] == "owasp-top-10"
    assert certification_quiz.pathway_for_lab(_lab("software-security"))["id"] == "owasp-top-10"
    assert certification_quiz.pathway_for_lab(_lab("ai"))["id"] == "owasp-llm-top-10"
    assert certification_quiz.pathway_for_lab(_lab("identity"))["id"] == "microsoft-sc-900"
    assert certification_quiz.pathway_for_lab(_lab("forensics"))["id"] == "comptia-cysa-plus"


def test_sampling_returns_three_unique_prefixed_questions():
    sample = certification_quiz.sample_for_lab(_lab("network"), count=3)
    assert len(sample) == 3
    keys = [row["key"] for row in sample]
    assert len(set(keys)) == 3
    assert all(key.startswith(certification_quiz.CERT_PREFIX) for key in keys)
    assert all(row["pathway"]["id"] == "comptia-network-plus" for row in sample)


def test_sample_avoids_a_previous_question_when_possible():
    lab = _lab("network")
    first = certification_quiz.sample_for_lab(lab, count=3)
    excluded = first[0]["key"]
    second = certification_quiz.sample_for_lab(
        lab, count=3, previous_keys={excluded}
    )
    assert len(second) == 3
    assert excluded not in {row["key"] for row in second}


def test_resolve_question_round_trips():
    sample = certification_quiz.sample_for_lab(_lab("ai"), count=1)[0]
    resolved = certification_quiz.resolve_question(sample["key"])
    assert resolved is not None
    assert resolved["prompt"] == sample["prompt"]
    assert isinstance(resolved["correct"], int)


def test_admin_payload_contains_answers_and_explanations():
    payload = certification_quiz.admin_payload()
    assert payload["validation"]["ok"] is True
    assert payload["pathways"]
    question = payload["pathways"][0]["questions"][0]
    assert "correct" in question
    assert question["explanation"]
    assert question["reference"]["url"].startswith("https://")


def test_public_pathway_has_no_answers():
    public = certification_quiz.public_pathway_for_lab(_lab("linux"))
    assert public is not None
    assert "questions" not in public
    assert "correct" not in str(public)
