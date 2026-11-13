"""The wiki session cookie must be HttpOnly and clearable."""


def test_wiki_cookie_is_httponly(client, auth_headers):
    response = client.post("/api/auth/wiki-cookie", headers=auth_headers)
    assert response.status_code == 204
    header = response.headers.get("set-cookie", "")
    assert "wiki_session=" in header
    assert "HttpOnly" in header
    assert "Secure" in header or "SameSite=lax" in header
    assert "no-store" in response.headers.get("cache-control", "")


def test_wiki_cookie_can_be_cleared(client, auth_headers):
    response = client.delete("/api/auth/wiki-cookie", headers=auth_headers)
    assert response.status_code == 204
    header = response.headers.get("set-cookie", "")
    assert "wiki_session=" in header
    assert "Max-Age=0" in header or "max-age=0" in header
