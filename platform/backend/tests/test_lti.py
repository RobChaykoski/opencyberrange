"""LTI 1.3 platform registration and login URL safety."""

from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.services.lti import (
    build_client_assertion,
    build_content_items,
    build_lineitem_payload,
    build_login_redirect,
    build_score_payload,
    normalize_roster,
    sign_deep_link_response,
    valid_lti_url,
)


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


def test_client_assertion_is_signed_private_key_jwt():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    platform = SimpleNamespace(
        client_id="client-123",
        token_url="https://lms.example.edu/lti/token",
        private_key=private_pem,
    )
    token = build_client_assertion(platform)
    claims = jwt.decode(
        token,
        key.public_key(),
        algorithms=["RS256"],
        audience=platform.token_url,
    )
    assert claims["iss"] == "client-123"
    assert claims["sub"] == "client-123"
    assert claims["aud"] == platform.token_url
    assert claims["exp"] > claims["iat"]


def test_score_payload_uses_lti_ags_fields():
    payload = build_score_payload(
        subject="lms-user-1",
        score=8,
        max_score=10,
        timestamp="2026-11-13T12:00:00Z",
    )
    assert payload == {
        "userId": "lms-user-1",
        "scoreGiven": 8,
        "scoreMaximum": 10,
        "activityProgress": "Completed",
        "gradingProgress": "FullyGraded",
        "timestamp": "2026-11-13T12:00:00Z",
    }


def test_lineitem_payload_matches_ags_shape():
    payload = build_lineitem_payload(
        label="Basic Windows Port Scan",
        max_score=100,
        resource_link_id="resource-1",
    )
    assert payload == {
        "scoreMaximum": 100,
        "label": "Basic Windows Port Scan",
        "resourceLinkId": "resource-1",
        "tag": "opencyberrange",
    }


def test_nrps_roster_keeps_only_minimal_fields():
    payload = {
        "context": {"id": "course-1"},
        "members": [
            {
                "user_id": "lms-user-1",
                "roles": ["Learner"],
                "status": "Active",
                "name": "Should not be returned",
                "email": "should-not-be-returned@example.edu",
            },
            {"roles": ["Instructor"], "status": "Active"},
        ],
    }
    assert normalize_roster(payload) == [
        {
            "user_id": "lms-user-1",
            "roles": ["Learner"],
            "status": "Active",
            "context_id": "course-1",
        }
    ]


def test_deep_link_content_items_use_lab_launch_urls():
    labs = [SimpleNamespace(slug="windows-1-1", name="Basic Port Scan")]
    items = build_content_items(labs, "https://range.example.edu")
    assert items == [
        {
            "type": "ltiResourceLink",
            "title": "Basic Port Scan",
            "url": "https://range.example.edu/api/lti/launch?lab=windows-1-1",
            "custom": {"lab_slug": "windows-1-1"},
        }
    ]


def test_deep_link_response_is_signed():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    platform = SimpleNamespace(
        client_id="client-123",
        issuer="https://lms.example.edu",
        deployment_id="dep-1",
        private_key=private_pem,
    )
    session = SimpleNamespace(nonce="nonce-1", data="opaque-data")
    labs = [SimpleNamespace(slug="lab-1", name="Lab One")]
    token = sign_deep_link_response(platform, session, labs)
    claims = jwt.decode(
        token,
        key.public_key(),
        algorithms=["RS256"],
        audience=platform.issuer,
    )
    assert claims["iss"] == "client-123"
    assert claims["nonce"] == "nonce-1"
    assert claims["https://purl.imsglobal.org/spec/lti/claim/message_type"] == "LtiDeepLinkingResponse"
    assert claims["https://purl.imsglobal.org/spec/lti-dl/claim/data"] == "opaque-data"
    assert claims["https://purl.imsglobal.org/spec/lti-dl/claim/content_items"][0]["custom"]["lab_slug"] == "lab-1"


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
