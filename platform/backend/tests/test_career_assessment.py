"""Short career-direction assessment: question shape and scoring."""

from app.services.career_assessment import public_questions, score_answers


def test_questions_are_short_and_have_four_options():
    questions = public_questions()
    assert 5 <= len(questions) <= 10
    for question in questions:
        assert question["prompt"]
        assert len(question["options"]) == 4
        assert [option["index"] for option in question["options"]] == [0, 1, 2, 3]


def test_scoring_is_relative_to_answered_questions():
    answers = {question["id"]: 0 for question in public_questions()}
    result = score_answers(answers)

    assert result["answered"] == 8
    assert len(result["scores"]) == 4
    assert sum(row["score"] for row in result["scores"]) == 100
    assert result["strongest"] is not None


def test_invalid_answers_are_rejected():
    try:
        score_answers({})
    except ValueError as exc:
        assert "No valid answers" in str(exc)
    else:
        raise AssertionError("empty answers should fail")


def test_unknown_question_is_ignored_when_another_answer_is_valid():
    question = public_questions()[0]
    result = score_answers({"unknown": 0, question["id"]: 1})
    assert result["answered"] == 1
