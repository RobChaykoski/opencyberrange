"""LTI 1.3 platform registration and login URL safety."""

from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.services.lti import (
    LTIError,
    build_client_assertion,
    build_content_items,
    build_lineitem_payload,
    build_login_redirect,
    build_score_payload,
    create_deep_link_session,
    create_launch_grant,
    lineitem_subpath,
    normalize_roster,
    platform_kid,
    public_jwk,
    sign_deep_link_response,
    tool_jwks,
    valid_lti_url,
    verify_launch_grant,
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
        lti_message_hint='{"launchid":"abc"}',
    )
    assert url.startswith("https://lms.example.edu/lti/login?")
    assert "response_type=id_token" in url
    assert "response_mode=form_post" in url
    assert "client_id=client-123" in url
    assert "deployment_id=deployment-1" in url
    assert "state=state-value" in url
    assert "nonce=nonce-value" in url
    assert "login_hint=learner-1" in url
    assert "lti_message_hint=%7B%22launchid%22%3A%22abc%22%7D" in url


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

    generated = build_score_payload(subject="lms-user-1", score=8, max_score=10)
    assert generated["timestamp"].endswith("Z")
    assert "." not in generated["timestamp"]
    assert ":" in generated["timestamp"]


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


def test_nrps_roster_reads_the_lis_membership_container():
    payload = {
        "@context": "http://purl.imsglobal.org/ctx/lis/v2/MembershipContainer",
        "@type": "Page",
        "pageOf": {
            "@type": "LISMembershipContainer",
            "membershipSubject": {
                "@type": "Context",
                "contextId": "2",
                "membership": [
                    {
                        "status": "Active",
                        "role": ["Learner"],
                        "member": {
                            "@type": "LISPerson",
                            "userId": "3",
                            "sourcedId": "",
                        },
                    },
                    {
                        "status": "Active",
                        "role": ["Instructor"],
                        "member": {"@type": "LISPerson", "userId": "2"},
                    },
                ],
            },
        },
    }
    assert normalize_roster(payload) == [
        {
            "user_id": "3",
            "roles": ["Learner"],
            "status": "Active",
            "context_id": "2",
        },
        {
            "user_id": "2",
            "roles": ["Instructor"],
            "status": "Active",
            "context_id": "2",
        },
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


def test_tool_jwks_exposes_only_public_material():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    platform = SimpleNamespace(
        private_key=private_pem,
        enabled=True,
    )
    jwk = public_jwk(platform)
    assert jwk["kty"] == "RSA"
    assert jwk["alg"] == "RS256"
    assert jwk["kid"] == platform_kid(platform)
    assert "d" not in jwk and "p" not in jwk and "q" not in jwk
    bundle = tool_jwks([platform, SimpleNamespace(private_key=None, enabled=True),
                        SimpleNamespace(private_key=private_pem, enabled=False)])
    assert bundle == {"keys": [jwk]}


def test_signed_messages_carry_the_jwks_kid():
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
        token_url="https://lms.example.edu/lti/token",
        private_key=private_pem,
        enabled=True,
    )
    assertion = build_client_assertion(platform)
    header = jwt.get_unverified_header(assertion)
    assert header["kid"] == platform_kid(platform)

    session = SimpleNamespace(nonce="nonce-1", data="opaque")
    response = sign_deep_link_response(
        platform, session, [SimpleNamespace(slug="lab-1", name="Lab One")]
    )
    assert jwt.get_unverified_header(response)["kid"] == platform_kid(platform)


def test_lineitem_subpath_keeps_the_query_string():
    url = "https://lms.example.edu/mod/lti/services.php/2/lineitems/2/lineitem?type_id=1"
    assert (
        lineitem_subpath(url, "scores")
        == "https://lms.example.edu/mod/lti/services.php/2/lineitems/2/lineitem/scores?type_id=1"
    )
    assert (
        lineitem_subpath(url, "/results")
        == "https://lms.example.edu/mod/lti/services.php/2/lineitems/2/lineitem/results?type_id=1"
    )


def test_launch_grant_is_scoped_to_user_and_lab():
    user = SimpleNamespace(id=7)
    grant = create_launch_grant(user, 141)
    assert verify_launch_grant(grant, 7, 141)
    assert not verify_launch_grant(grant, 8, 141)
    assert not verify_launch_grant(grant, 7, 142)
    assert not verify_launch_grant(None, 7, 141)


def test_deep_link_session_rejects_non_https_return_url():
    platform = SimpleNamespace(id=1)
    user = SimpleNamespace(id=2)
    with pytest.raises(LTIError):
        create_deep_link_session(
            None,
            platform=platform,
            user=user,
            return_url="http://lms.example.edu/deep-link-return",
            data="opaque",
        )


def test_callback_url_can_target_the_lti_callback():
    from app.services import sso_flow

    url = sso_flow.callback_url({"ticket": "ticket-1"}, path="/lti/callback")
    assert "/lti/callback?ticket=ticket-1" in url


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
