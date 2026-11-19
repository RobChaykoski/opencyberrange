"""Cloud-posture scanner for the simulated cloud range.

This is a teaching scanner, not a compliance product. It looks for the same
classes of finding the labs ask learners to fix:

* public object-store policies;
* missing bucket versioning;
* wildcard IAM policies and long-lived access keys;
* privileged or host-mounted Kubernetes workloads;
* plaintext secrets in manifests and configuration files.

Findings are written as JSON and can be indexed into OpenSearch so the
Sentinel-like dashboards have a posture index to query.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path

import boto3
import requests
import yaml
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}

SECRET_PATTERNS = (
    (re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?([^'\"\s]{6,})"), "password"),
    (re.compile(r"(?i)(secret|token|api[_-]?key)\s*[:=]\s*['\"]?([A-Za-z0-9_\-/+=]{12,})"), "secret"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "aws-access-key"),
    (re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"), "private-key"),
)

SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", "dist", "site", "_site"}


def finding(
    *,
    check_id: str,
    title: str,
    severity: str,
    resource: str,
    evidence: str,
    remediation: str,
    control: str,
    azure_concept: str,
    local_service: str,
) -> dict:
    return {
        "id": check_id,
        "title": title,
        "severity": severity,
        "resource": resource,
        "evidence": evidence,
        "remediation": remediation,
        "control": control,
        "azure_concept": azure_concept,
        "local_service": local_service,
        "detected_at": datetime.now(UTC).isoformat(),
    }


def s3_client(endpoint: str, user: str, password: str):
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=user,
        aws_secret_access_key=password,
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}, connect_timeout=5, read_timeout=10),
    )


def scan_object_store(endpoint: str, user: str, password: str) -> list[dict]:
    found: list[dict] = []
    try:
        s3 = s3_client(endpoint, user, password)
        buckets = s3.list_buckets().get("Buckets", [])
    except (BotoCoreError, ClientError) as exc:
        return [
            finding(
                check_id="cloud-store-unreachable",
                title="Object store could not be reached",
                severity="info",
                resource=endpoint,
                evidence=str(exc),
                remediation="Start MinIO and confirm the endpoint and credentials.",
                control="NIST CSF 2.0 ID.AM",
                azure_concept="Storage account",
                local_service="MinIO",
            )
        ]

    for bucket in buckets:
        name = bucket.get("Name", "")
        try:
            policy = s3.get_bucket_policy(Bucket=name).get("Policy", "")
        except ClientError:
            policy = ""
        if policy:
            try:
                document = json.loads(policy)
                statements = document.get("Statement", [])
                if isinstance(statements, dict):
                    statements = [statements]
                public = any(
                    str(statement.get("Principal")) in {"*", '{"AWS":"*"}'}
                    or statement.get("Principal") == {"AWS": "*"}
                    for statement in statements
                )
                if public:
                    found.append(
                        finding(
                            check_id="storage-public-policy",
                            title="Bucket policy allows public principals",
                            severity="critical",
                            resource=name,
                            evidence=json.dumps(document)[:600],
                            remediation="Remove the public principal and enable block-public-access.",
                            control="NIST CSF 2.0 PR.AC",
                            azure_concept="Public blob container",
                            local_service="MinIO",
                        )
                    )
            except json.JSONDecodeError:
                pass

        try:
            versioning = s3.get_bucket_versioning(Bucket=name).get("Status", "")
            if versioning != "Enabled":
                found.append(
                    finding(
                        check_id="storage-versioning-off",
                        title="Bucket versioning is not enabled",
                        severity="medium",
                        resource=name,
                        evidence=f"Versioning status: {versioning or 'unset'}",
                        remediation="Enable versioning before storing evidence or backups.",
                        control="NIST CSF 2.0 PR.DS",
                        azure_concept="Blob soft delete and versioning",
                        local_service="MinIO",
                    )
                )
        except ClientError:
            pass

    return found


def scan_iam(endpoint: str) -> list[dict]:
    found: list[dict] = []
    try:
        iam = boto3.client(
            "iam",
            endpoint_url=endpoint,
            aws_access_key_id="test",
            aws_secret_access_key="test",
            region_name="us-east-1",
            config=Config(connect_timeout=5, read_timeout=10),
        )
        users = iam.list_users().get("Users", [])
    except (BotoCoreError, ClientError) as exc:
        return [
            finding(
                check_id="iam-unreachable",
                title="IAM control plane could not be reached",
                severity="info",
                resource=endpoint,
                evidence=str(exc),
                remediation="Start LocalStack with the aws profile.",
                control="NIST CSF 2.0 ID.AM",
                azure_concept="Microsoft Entra ID",
                local_service="LocalStack IAM",
            )
        ]

    for user in users:
        name = user.get("UserName", "")
        try:
            policies = iam.list_attached_user_policies(UserName=name).get("AttachedPolicies", [])
        except ClientError:
            policies = []
        for policy in policies:
            arn = policy.get("PolicyArn", "")
            try:
                version = iam.get_policy(PolicyArn=arn)["Policy"]["DefaultVersionId"]
                document = iam.get_policy_version(PolicyArn=arn, VersionId=version)["PolicyVersion"]["Document"]
                text = json.dumps(document)
                if '"*"' in text and ("Action" in text or "Resource" in text):
                    found.append(
                        finding(
                            check_id="iam-wildcard-policy",
                            title="IAM policy grants wildcard action or resource",
                            severity="high",
                            resource=f"{name} / {policy.get('PolicyName', arn)}",
                            evidence=text[:600],
                            remediation="Scope Action and Resource to the minimum the role needs.",
                            control="NIST CSF 2.0 PR.AC",
                            azure_concept="Role assignment and least privilege",
                            local_service="LocalStack IAM",
                        )
                    )
            except (ClientError, KeyError):
                pass

        try:
            keys = iam.list_access_keys(UserName=name).get("AccessKeyMetadata", [])
            for key in keys:
                created = key.get("CreateDate")
                if created and (datetime.now(UTC) - created).days > 90:
                    found.append(
                        finding(
                            check_id="iam-stale-access-key",
                            title="Access key is older than 90 days",
                            severity="medium",
                            resource=f"{name} / {key.get('AccessKeyId', '')}",
                            evidence=f"Created {created.isoformat()}",
                            remediation="Rotate the key and record the rotation evidence.",
                            control="NIST CSF 2.0 PR.AC",
                            azure_concept="Access key and secret rotation",
                            local_service="LocalStack IAM",
                        )
                    )
        except (ClientError, KeyError):
            pass

    return found


def scan_kubernetes(root: Path) -> list[dict]:
    found: list[dict] = []
    paths = [root] if root.is_file() else sorted(root.rglob("*.yaml")) + sorted(root.rglob("*.yml"))
    for path in paths:
        try:
            documents = list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
        except (OSError, yaml.YAMLError):
            continue
        for document in documents:
            if not isinstance(document, dict):
                continue
            kind = document.get("kind", "")
            name = document.get("metadata", {}).get("name", path.name)
            if kind not in {"Pod", "Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"}:
                continue
            spec = document.get("spec", {}) or {}
            pod_spec = spec.get("template", {}).get("spec", spec) if kind not in {"Pod", "CronJob"} else spec
            if kind == "CronJob":
                pod_spec = spec.get("jobTemplate", {}).get("spec", {}).get("template", {}).get("spec", {})
            if pod_spec.get("hostNetwork"):
                found.append(
                    finding(
                        check_id="k8s-host-network",
                        title="Workload uses host networking",
                        severity="high",
                        resource=f"{kind}/{name}",
                        evidence=str(path),
                        remediation="Remove hostNetwork and expose the service through a Service and NetworkPolicy.",
                        control="NIST CSF 2.0 PR.AC",
                        azure_concept="VNet and private endpoint",
                        local_service="k3s / kind",
                    )
                )
            for container in (pod_spec.get("containers") or []) + (pod_spec.get("initContainers") or []):
                context = container.get("securityContext", {}) or {}
                if context.get("privileged"):
                    found.append(
                        finding(
                            check_id="k8s-privileged-container",
                            title="Container runs privileged",
                            severity="critical",
                            resource=f"{kind}/{name} / {container.get('name', '')}",
                            evidence=str(path),
                            remediation="Drop privileged mode, drop all capabilities, and use a minimal image.",
                            control="NIST CSF 2.0 PR.IP",
                            azure_concept="AKS pod security",
                            local_service="k3s / kind",
                        )
                    )
                if context.get("allowPrivilegeEscalation") is not False:
                    found.append(
                        finding(
                            check_id="k8s-privilege-escalation",
                            title="allowPrivilegeEscalation is not disabled",
                            severity="medium",
                            resource=f"{kind}/{name} / {container.get('name', '')}",
                            evidence=str(path),
                            remediation="Set allowPrivilegeEscalation: false.",
                            control="NIST CSF 2.0 PR.IP",
                            azure_concept="AKS pod security",
                            local_service="k3s / kind",
                        )
                    )
                if context.get("runAsNonRoot") is not True:
                    found.append(
                        finding(
                            check_id="k8s-run-as-root",
                            title="Container does not require a non-root user",
                            severity="medium",
                            resource=f"{kind}/{name} / {container.get('name', '')}",
                            evidence=str(path),
                            remediation="Set runAsNonRoot: true and a numeric runAsUser.",
                            control="NIST CSF 2.0 PR.IP",
                            azure_concept="AKS pod security",
                            local_service="k3s / kind",
                        )
                    )
            for volume in pod_spec.get("volumes") or []:
                if "hostPath" in volume:
                    found.append(
                        finding(
                            check_id="k8s-host-path",
                            title="Workload mounts a host path",
                            severity="high",
                            resource=f"{kind}/{name} / {volume.get('name', '')}",
                            evidence=str(path),
                            remediation="Replace hostPath with a PersistentVolumeClaim or a projected secret.",
                            control="NIST CSF 2.0 PR.AC",
                            azure_concept="AKS storage boundary",
                            local_service="k3s / kind",
                        )
                    )
    return found


def scan_secrets(root: Path) -> list[dict]:
    found: list[dict] = []
    allowed = {".yaml", ".yml", ".json", ".env", ".ini", ".conf", ".tf", ".tfvars", ".md", ".sh", ".py"}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in allowed:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern, label in SECRET_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            # Ignore obvious placeholders and references.
            snippet = match.group(0)
            if any(token in snippet.lower() for token in ("change-me", "replace", "example", "dummy", "${")):
                continue
            found.append(
                finding(
                    check_id=f"secret-{label}",
                    title=f"Possible plaintext {label}",
                    severity="high",
                    resource=str(path),
                    evidence=snippet[:80],
                    remediation="Move the value to Vault or Kubernetes Secret and rotate it.",
                    control="NIST CSF 2.0 PR.DS",
                    azure_concept="Key Vault",
                    local_service="HashiCorp Vault",
                )
            )
            break
    return found


def index_findings(url: str, index: str, findings: list[dict]) -> None:
    for item in findings:
        try:
            requests.post(f"{url.rstrip('/')}/{index}/_doc", json=item, timeout=5)
        except requests.RequestException:
            return


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="/workspace", help="Repository or lab directory to scan")
    parser.add_argument("--minio-endpoint", default=os.environ.get("MINIO_ENDPOINT", "http://minio:9000"))
    parser.add_argument("--minio-user", default=os.environ.get("MINIO_ROOT_USER", ""))
    parser.add_argument("--minio-password", default=os.environ.get("MINIO_ROOT_PASSWORD", ""))
    parser.add_argument("--localstack-endpoint", default=os.environ.get("LOCALSTACK_ENDPOINT", ""))
    parser.add_argument("--opensearch-url", default=os.environ.get("OPENSEARCH_URL", ""))
    parser.add_argument("--index", default=f"cloud-posture-{datetime.now(UTC):%Y.%m.%d}")
    parser.add_argument("--output", default="findings.json")
    parser.add_argument("--skip-object-store", action="store_true")
    parser.add_argument("--skip-iam", action="store_true")
    parser.add_argument("--skip-kubernetes", action="store_true")
    parser.add_argument("--skip-secrets", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    findings: list[dict] = []
    if not args.skip_object_store and args.minio_user:
        findings.extend(scan_object_store(args.minio_endpoint, args.minio_user, args.minio_password))
    if not args.skip_iam and args.localstack_endpoint:
        findings.extend(scan_iam(args.localstack_endpoint))
    if not args.skip_kubernetes and root.exists():
        findings.extend(scan_kubernetes(root))
    if not args.skip_secrets and root.exists():
        findings.extend(scan_secrets(root))

    findings.sort(key=lambda item: (SEVERITY_ORDER.get(item["severity"], 9), item["id"]))
    output = Path(args.output)
    output.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    print(f"{len(findings)} findings written to {output}")
    for item in findings:
        print(f"[{item['severity'].upper():8}] {item['id']}: {item['title']} ({item['resource']})")

    if args.opensearch_url and findings:
        index_findings(args.opensearch_url, args.index, findings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
