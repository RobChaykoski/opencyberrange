"""Tests for the optional exercise knowledge-check loader."""

from pathlib import Path

import pytest

from app.services import exercise_quiz


def _write_bank(path: Path, title: str, count: int = 3) -> None:
    questions = []
    for index in range(count):
        questions.append(
            f"""
  - id: "q{index}"
    prompt: "Question {index}?"
    options: ["A", "B", "C", "D"]
    correct: 1
    explanation: "Because B is correct."
    reference:
      label: "Reference"
      url: "https://example.org/{index}"
"""
        )
    path.write_text(
        f"""
certification:
  name: "{title}"
  code: ""
  url: ""
questions:
{''.join(questions)}
""",
        encoding="utf-8",
    )


@pytest.fixture()
def labs_root(tmp_path, monkeypatch):
    lab_dir = tmp_path / "Track" / "lab-one"
    lab_dir.mkdir(parents=True)
    (lab_dir / "lab.yaml").write_text("name: Lab One\n", encoding="utf-8")
    monkeypatch.setattr(exercise_quiz, "LABS_ROOT", tmp_path)
    exercise_quiz.reset_cache()
    yield tmp_path
    exercise_quiz.reset_cache()


def test_lab_specific_bank_is_preferred(labs_root):
    lab_dir = labs_root / "Track" / "lab-one"
    _write_bank(lab_dir / "quiz.yaml", "Lab bank", count=6)
    _write_bank(labs_root / "Track" / "_track_quiz.yaml", "Track bank", count=5)

    quiz = exercise_quiz.load_quiz("lab-one")

    assert quiz["source"] == "lab"
    assert quiz["certification"]["name"] == "Lab bank"
    assert len(quiz["questions"]) == 6


def test_track_bank_is_the_fallback(labs_root):
    _write_bank(labs_root / "Track" / "_track_quiz.yaml", "Track bank", count=5)

    quiz = exercise_quiz.load_quiz("lab-one")

    assert quiz["source"] == "track"
    assert quiz["certification"]["name"] == "Track bank"
    assert exercise_quiz.question_sample_count(quiz) == 2


def test_sample_excludes_the_previous_questions_when_possible(labs_root):
    lab_dir = labs_root / "Track" / "lab-one"
    _write_bank(lab_dir / "quiz.yaml", "Lab bank", count=6)
    quiz = exercise_quiz.load_quiz("lab-one")

    sample = exercise_quiz.sample_questions(quiz, {"q0", "q1", "q2"}, 3)

    assert len(sample) == 3
    assert not {"q0", "q1", "q2"} & {question["id"] for question in sample}


def test_invalid_correct_index_is_rejected(labs_root):
    lab_dir = labs_root / "Track" / "lab-one"
    (lab_dir / "quiz.yaml").write_text(
        """
questions:
  - id: "bad"
    prompt: "Bad question"
    options: ["A", "B"]
    correct: 9
    explanation: "No."
    reference:
      label: "Ref"
      url: "https://example.org"
""",
        encoding="utf-8",
    )

    assert exercise_quiz.load_quiz("lab-one") is None
