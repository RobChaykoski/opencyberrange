"""Modern application-security lab service.

One process, one mode. The mode selects which vulnerable endpoint the exercise
targets; the flag is injected by compose so each lab has a distinct token.
"""

import os

from flask import Flask, jsonify, request

app = Flask(__name__)
MODE = os.environ.get("LAB_MODE", "inventory")
FLAG = os.environ.get("LAB_FLAG", "OCR{missing_flag}")

USERS = {
    "1": {"id": 1, "name": "alice", "role": "user", "balance": "$120"},
    "2": {"id": 2, "name": "admin", "role": "admin", "flag": FLAG},
}


@app.get("/")
def index():
    return jsonify({"service": "modern-appsec-lab", "mode": MODE, "docs": "/api/docs"})


@app.get("/api/docs")
def docs():
    return jsonify(
        {
            "endpoints": [
                "/api/health",
                "/api/docs",
                "/api/users/<id>",
                "/api/internal/inventory",
                "/graphql",
                "/api/jwt/debug",
                "/oauth/callback",
                "/ci/secrets",
                "/api/runtime",
                "/api/k8s/secrets",
                "/api/sbom",
                "/api/admin/audit",
            ]
        }
    )


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/internal/inventory")
def inventory():
    return jsonify(
        {
            "api_inventory": ["/api/users", "/api/admin", "/api/internal/inventory"],
            "assessment_token": FLAG if MODE == "inventory" else None,
        }
    )


@app.get("/api/users/<user_id>")
def user(user_id):
    return jsonify(USERS.get(user_id, USERS["1"]))


@app.get("/api/admin/config")
def admin_config():
    return jsonify({"flag": FLAG})


@app.post("/graphql")
def graphql():
    return jsonify(
        {
            "data": {
                "__schema": {
                    "queryType": {"name": "Query"},
                    "types": [{"name": "Debug"}],
                    "fields": [{"name": "debugFlag"}],
                },
                "debugFlag": FLAG,
            }
        }
    )


@app.get("/graphql")
def graphql_get():
    return graphql()


@app.get("/api/jwt/debug")
def jwt_debug():
    return jsonify({"alg": "none", "accepted": True, "flag": FLAG})


@app.get("/oauth/callback")
def oauth_callback():
    return jsonify(
        {
            "redirect_uri": request.args.get("redirect_uri", ""),
            "validated": False,
            "flag": FLAG,
        }
    )


@app.get("/ci/secrets")
def ci_secrets():
    return jsonify(
        {
            "CI_JOB_TOKEN": "glpat-example-token",
            "workflow_permissions": "write-all",
            "flag": FLAG,
        }
    )


@app.get("/api/runtime")
def runtime():
    return jsonify(
        {
            "uid": os.getuid() if hasattr(os, "getuid") else 0,
            "user": "root",
            "capabilities": ["CAP_SYS_ADMIN"],
            "flag": FLAG,
        }
    )


@app.get("/api/k8s/secrets")
def k8s_secrets():
    return jsonify(
        {
            "service_account": "default",
            "rbac": ["get", "list", "watch", "create"],
            "flag": FLAG,
        }
    )


@app.get("/api/sbom")
def sbom():
    return jsonify(
        {
            "components": [{"name": "flask", "version": "3.0.3"}],
            "signed": False,
            "flag": FLAG,
        }
    )


@app.get("/api/admin/audit")
def admin_audit():
    return jsonify(
        {
            "chain": ["inventory", "bola", "jwt", "container", "supply-chain"],
            "flag": FLAG,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
