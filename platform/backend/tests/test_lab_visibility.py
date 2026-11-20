"""Visibility rules for labs, including the LTI launch bypass.

An LTI launch grant proves that a specific exercise was assigned through the
LMS. It may open a course-only exercise for the provisioned LTI user, who is
not enrolled locally. It must not bypass inactive, draft, or minor/OSINT safety
rules.
"""

from types import SimpleNamespace

from app.routers.curriculum import _is_lab_visible


def _student(*, is_minor=False, role="student"):
    return SimpleNamespace(id=7, role=role, is_minor=is_minor)


def _lab(visibility="course", *, active=True, category="network", created_by=None):
    return SimpleNamespace(
        id=141,
        visibility=visibility,
        is_active=active,
        category=category,
        created_by=created_by,
    )


def test_course_lab_requires_assignment_without_lti_launch():
    assert not _is_lab_visible(_lab(), _student(), set(), course_context=True)
    assert _is_lab_visible(
        _lab(), _student(), {141}, course_context=True
    )


def test_lti_launch_opens_a_course_lab_without_local_enrolment():
    assert _is_lab_visible(
        _lab(), _student(), set(), course_context=True, lti_launch=True
    )
    assert _is_lab_visible(
        _lab("pending_public"),
        _student(),
        set(),
        course_context=True,
        lti_launch=True,
    )


def test_lti_launch_does_not_bypass_minor_osint_rule():
    assert not _is_lab_visible(
        _lab(category="osint"),
        _student(is_minor=True),
        set(),
        course_context=True,
        lti_launch=True,
    )


def test_lti_launch_does_not_open_an_inactive_or_foreign_draft_lab():
    assert not _is_lab_visible(
        _lab(active=False),
        _student(),
        set(),
        course_context=True,
        lti_launch=True,
    )
    assert not _is_lab_visible(
        _lab("draft", created_by=99),
        _student(),
        set(),
        course_context=True,
        lti_launch=True,
    )


def test_lti_launch_still_opens_public_labs():
    assert _is_lab_visible(
        _lab("public"), _student(), set(), course_context=True, lti_launch=True
    )
