from __future__ import annotations

import hmac
import logging
import os
from dataclasses import dataclass

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

from .detectors import ScanResult, scan_text
from .metadata import MetadataUnavailable, build_metadata_store
from .models import (
    ContextResponse,
    DecisionRequest,
    DecisionResponse,
    ResourceMetadata,
    ResourceRef,
    ScanDecisionRequest,
    ScanDecisionResponse,
    ScanRequest,
    ScanResponse,
)
from .policy import _metadata_hash, decide

logger = logging.getLogger("context")


@dataclass
class Settings:
    metadata_mode: str = "fixture"
    metadata_file: str = "/app/fixtures/metadata.json"
    metadata_lookup_url: str = ""
    opa_url: str | None = None
    service_token: str = ""
    fail_closed: bool = True

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            metadata_mode=os.environ.get("METADATA_MODE", "fixture").strip().lower(),
            metadata_file=os.environ.get("METADATA_FILE", "/app/fixtures/metadata.json"),
            metadata_lookup_url=os.environ.get("METADATA_LOOKUP_URL", ""),
            opa_url=os.environ.get("OPA_URL") or None,
            service_token=os.environ.get("CONTEXT_SERVICE_TOKEN", ""),
            fail_closed=os.environ.get("POLICY_FAIL_CLOSED", "1").lower()
            not in ("0", "false", "no"),
        )


def _scan_metadata(source: str, result: ScanResult) -> ResourceMetadata:
    return ResourceMetadata(
        id=source,
        classification=result.classification,
        owner="unknown",
        contains_infrastructure_metadata=result.contains_infrastructure_metadata,
        contains_assessment_answer_key=result.contains_assessment_answer_key,
        contains_secrets=result.contains_secrets,
        publication_safe=result.publication_safe,
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    store = build_metadata_store(
        settings.metadata_mode, settings.metadata_file, settings.metadata_lookup_url
    )
    if not settings.service_token:
        logger.warning(
            "CONTEXT_SERVICE_TOKEN is unset; the context service is unauthenticated. "
            "Use this only on a private development network."
        )

    app = FastAPI(title="OpenCyberRange context service", version="0.1.0")

    def require_token(x_context_token: str | None = Header(default=None)) -> None:
        if not settings.service_token:
            return
        if not x_context_token or not hmac.compare_digest(
            x_context_token, settings.service_token
        ):
            raise HTTPException(status_code=401, detail="Invalid context token")

    def _unknown(resource_id: str) -> ResourceMetadata:
        return ResourceMetadata(id=resource_id, classification="unknown", owner="unknown")

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "metadata_mode": settings.metadata_mode,
            "policy_mode": "opa" if settings.opa_url else "fixture",
        }

    @app.post("/context", response_model=ContextResponse)
    def context(
        payload: DecisionRequest,
        _: None = Depends(require_token),
    ):
        try:
            metadata = store.lookup(payload.resource.id)
        except MetadataUnavailable as exc:
            raise HTTPException(status_code=503, detail="Metadata unavailable") from exc
        if metadata is None:
            metadata = _unknown(payload.resource.id)
        return ContextResponse(resource=metadata, metadata_hash=_metadata_hash(metadata))

    @app.post("/decide", response_model=DecisionResponse)
    def decision(
        payload: DecisionRequest,
        _: None = Depends(require_token),
    ):
        try:
            metadata = store.lookup(payload.resource.id)
        except MetadataUnavailable as exc:
            if settings.fail_closed:
                raise HTTPException(status_code=503, detail="Metadata unavailable") from exc
            metadata = _unknown(payload.resource.id)
        if metadata is None:
            metadata = _unknown(payload.resource.id)
        return decide(
            payload,
            metadata,
            opa_url=settings.opa_url,
            fail_closed=settings.fail_closed,
        )

    @app.post("/scan", response_model=ScanResponse)
    def scan(
        payload: ScanRequest,
        _: None = Depends(require_token),
    ):
        result = scan_text(payload.text)
        return ScanResponse(source=payload.source, **result.as_dict())

    @app.post("/scan-and-decide", response_model=ScanDecisionResponse)
    def scan_and_decide(
        payload: ScanDecisionRequest,
        _: None = Depends(require_token),
    ):
        result = scan_text(payload.text)
        metadata = _scan_metadata(payload.source, result)
        request = DecisionRequest(
            subject=payload.subject,
            resource=ResourceRef(id=payload.source, type="document"),
            action=payload.action,
            environment=payload.environment,
        )
        decision = decide(
            request,
            metadata,
            opa_url=settings.opa_url,
            fail_closed=settings.fail_closed,
        )
        return ScanDecisionResponse(
            **decision.model_dump(),
            scan=ScanResponse(source=payload.source, **result.as_dict()),
        )

    @app.exception_handler(Exception)
    async def unhandled(request, exc):  # pragma: no cover - safety net
        logger.exception("context service error")
        return JSONResponse(status_code=500, content={"detail": "Context service error"})

    return app


app = create_app()
