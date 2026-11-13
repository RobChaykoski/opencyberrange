"""LTI 1.3 platform registration and login URL safety."""

from types import SimpleNamespace

import pytest

from app.services.lti import build_login_redirect, valid_lti_url


def test_lti_urls_require_http_or_https():
    assert valid_lti_url("https://lms.example.edu/lti/login")
    assert valid_lti_url("http://localhost:8081/lti/login", allow_http=True)
    assert not valid_lti_url("http://lms.example.edu/lti/login")
    assert not valid_lti_url("javascript:alert(1)")
    assert not valid_lti_url("https://lms.example.edu/lti/login#frag")


def test_login_redirect_carries_required_parameters():
    platform = SimpleNamespace(
        auth_login_url="https://lms.example.edu/lti/login",
        client_id="client-123",
        deployment_id="deployment-1",
    )
    url = build_login_redirect(
        platform,
        state="state-value",
        nonce="nonce-value",
        login_hint="learner-1",
        launch_url="https://range.example.edu/api/lti/launch",
    )
    assert url.startswith("https://lms.example.edu/lti/login?")
    assert "response_type=id_token" in url
    assert "response_mode=form_post" in url
    assert "client_id=client-123" in url
    assert "deployment_id=deployment-1" in url
    assert "state=state-value" in url
    assert "nonce=nonce-value" in url
    assert "login_hint=learner-1" in url


def test_login_redirect_escapes_values():
    platform = SimpleNamespace(
        auth_login_url="https://lms.example.edu/lti/login",
        client_id="a&b",
        deployment_id="d 1",
    )
    url = build_login_redirect(
        platform,
        state="s",
        nonce="n",
        login_hint="user+name",
        launch_url="https://range.example.edu/api/lti/launch",
    )
    assert "client_id=a%26b" in url
    assert "deployment_id=d+1" in url
