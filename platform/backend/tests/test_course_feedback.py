"""Unit tests for the two-way course feedback model helpers."""

import pytest
from pydantic import ValidationError

from app.routers.courses import _feedback_avg, _feedback_pct
from app.schemas import CourseFeedbackRequest


def test_feedback_avg_ignores_missing_values():
    assert _feedback_avg([5, None, 3, 4]) == 4.0
    assert _feedback_avg([None, None]) is None
    assert _feedback_avg([]) is None


def test_feedback_pct_handles_empty_denominator():
    assert _feedback_pct(3, 12) == 25.0
    assert _feedback_pct(0, 0) == 0.0


def test_feedback_request_accepts_a_comment_only_checkin():
    body = CourseFeedbackRequest(comment="The pivot exercise needs a clearer hint.")
    assert body.comment.startswith("The pivot")
    assert body.clarity is None


def test_feedback_request_rejects_out_of_range_ratings():
    with pytest.raises(ValidationError):
        CourseFeedbackRequest(clarity=6)
    with pytest.raises(ValidationError):
        CourseFeedbackRequest(engagement=0)
