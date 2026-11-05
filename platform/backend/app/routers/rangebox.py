"""
RangeBox routes â€” browser-based Kali attack desktop via noVNC.

Provides WebSocket proxy between the browser's noVNC client and the
RangeBox container's websockify server. Authentication is handled here
so the VNC server inside the container needs no password.
"""

import asyncio
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.auth import get_current_active_user, create_ws_ticket, validate_ws_ticket
from app.models import User, Lab, LabSession, LabCompletion, CourseEnrollment, CourseLabAssignment
from app.services.docker_manager import DockerManager, RangeBoxCapacityError

logger = logging.getLogger(__name__)
router = APIRouter()

docker_manager = DockerManager()


# â”€â”€â”€ Helper: authenticate WebSocket connections â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async def _authenticate_ws(token: str) -> tuple[int | None, bool]:
    """
    Validate a WebSocket ticket (preferred) or JWT token and return
    ``(user_id, is_impersonating)``, or ``(None, False)`` on failure.
    Short-lived tickets prevent JWTs from leaking into logs and browser history.

    ``is_impersonating`` surfaces the JWT ``imp`` claim so the VNC relays can
    enforce read-only "View As": the HTTP impersonation middleware does not run
    in WebSocket scope, so the guard has to live in the handler.
    """
    # Try single-use ticket first (preferred path). Tickets are minted via a
    # POST the impersonation middleware blocks, so a ticket is never an
    # impersonation session.
    user_id = validate_ws_ticket(token)
    if user_id is not None:
        return user_id, False

    # Fall back to JWT for backward compatibility
    import jwt
    from jwt import PyJWTError as JWTError
    from app.config import settings

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None, False
        is_imp = bool(payload.get("imp", False))
    except JWTError:
        return None, False

    # Look up user in DB
    db = SessionLocal()
    try:
        from app.models import User
        user = db.query(User).filter(User.username == username, User.is_active == True).first()
        return (user.id if user else None), is_imp
    finally:
        db.close()


# â”€â”€â”€ WebSocket ticket endpoint â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.post("/ws-ticket")
async def get_ws_ticket(
    current_user: User = Depends(get_current_active_user),
):
    """Exchange a JWT for a short-lived, single-use WebSocket ticket.
    The ticket replaces the JWT in WebSocket URLs to prevent token leakage."""
    ticket = create_ws_ticket(current_user.id)
    return {"ticket": ticket}


# â”€â”€â”€ Standalone RangeBox (not tied to a lab session) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# NOTE: These MUST be defined before /{session_id}/... routes,
# otherwise FastAPI matches "standalone" as a session_id int and returns 422.

@router.get("/capacity")
async def rangebox_capacity(
    current_user: User = Depends(get_current_active_user),
):
    """Return current and maximum RangeBox capacity."""
    running = docker_manager._count_running_rangeboxes()
    maximum = docker_manager.MAX_CONCURRENT_RANGEBOXES
    return {
        "running": running,
        "max": maximum,
        "available": running < maximum,
    }


@router.post("/standalone/launch")
async def standalone_rangebox_launch(
    current_user: User = Depends(get_current_active_user),
    image: str = Query(default=None, description="Image shorthand: 'kali', 'ubuntu', or 'remnux'"),
):
    """Launch a standalone RangeBox (not tied to any lab session)."""
    try:
        result = docker_manager.spawn_standalone_rangebox(current_user.id, image=image, username=current_user.username)
    except RangeBoxCapacityError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to launch standalone RangeBox",
        )

    # Auto-bridge if admin has an active impersonation session
    if current_user.role == "admin":
        from app.routers.admin import _admin_impersonation
        imp = _admin_impersonation.get(current_user.id)
        if imp:
            docker_manager.bridge_standalone_rangebox_to_lab(
                current_user.id, imp["lab_slug"], imp["user_id"]
            )

    return {
        "message": "Standalone RangeBox launched",
        "container_id": result,
        "ip": docker_manager.get_standalone_rangebox_ip(current_user.id),
    }


@router.delete("/standalone/destroy")
async def standalone_rangebox_destroy(
    current_user: User = Depends(get_current_active_user),
):
    """Stop and remove the standalone RangeBox."""
    docker_manager.destroy_standalone_rangebox(current_user.id)
    return {"message": "Standalone RangeBox destroyed"}


@router.get("/standalone/status")
async def standalone_rangebox_status(
    current_user: User = Depends(get_current_active_user),
):
    """Get standalone RangeBox container status."""
    return docker_manager.get_standalone_rangebox_status(current_user.id)


@router.websocket("/standalone/vnc")
async def standalone_rangebox_vnc_proxy(
    websocket: WebSocket,
    token: str = Query(default=""),
):
    """
    Bidirectional WebSocket proxy for standalone RangeBox VNC.
    Auth: JWT passed as ?token= query parameter.
    """
    if not token:
        await websocket.close(code=4401, reason="Missing token")
        return

    user_id, ws_imp = await _authenticate_ws(token)
    if user_id is None:
        await websocket.close(code=4401, reason="Invalid token")
        return

    rangebox_ip = docker_manager.get_standalone_rangebox_ip(user_id)
    rangebox_ws_url = f"ws://{rangebox_ip}:{docker_manager.RANGEBOX_NOVNC_PORT}/websockify"

    try:
        import aiohttp
    except ImportError:
        logger.error("aiohttp is required for RangeBox WebSocket proxy")
        await websocket.close(code=4500, reason="Server configuration error")
        return

    await websocket.accept(subprotocol="binary")

    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.ws_connect(
                rangebox_ws_url,
                protocols=["binary"],
                max_msg_size=16 * 1024 * 1024,
            ) as upstream:

                async def browser_to_container():
                    try:
                        while True:
                            msg = await websocket.receive()
                            if msg["type"] == "websocket.receive":
                                # Read-only "View As": drain browser frames but
                                # never inject input into the student's session.
                                if ws_imp:
                                    continue
                                if "bytes" in msg and msg["bytes"]:
                                    await upstream.send_bytes(msg["bytes"])
                                elif "text" in msg and msg["text"]:
                                    await upstream.send_str(msg["text"])
                            elif msg["type"] == "websocket.disconnect":
                                break
                    except WebSocketDisconnect:
                        pass
                    except Exception as e:
                        logger.debug(f"standalone browserâ†’container relay ended: {e}")
                    finally:
                        await upstream.close()

                async def container_to_browser():
                    try:
                        async for msg in upstream:
                            if msg.type == aiohttp.WSMsgType.BINARY:
                                await websocket.send_bytes(msg.data)
                            elif msg.type == aiohttp.WSMsgType.TEXT:
                                await websocket.send_text(msg.data)
                            elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
                                break
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                break
                    except Exception as e:
                        logger.debug(f"standalone containerâ†’browser relay ended: {e}")
                    finally:
                        try:
                            await websocket.close()
                        except Exception:
                            pass

                done, pending = await asyncio.wait(
                    [
                        asyncio.create_task(browser_to_container()),
                        asyncio.create_task(container_to_browser()),
                    ],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

    except aiohttp.ClientError as e:
        logger.warning(f"Failed to connect to standalone RangeBox websockify at {rangebox_ws_url}: {e}")
        try:
            await websocket.close(code=4502, reason="RangeBox not ready")
        except Exception:
            pass
    except Exception as e:
        logger.warning(f"Standalone RangeBox VNC proxy error: {e}")
        try:
            await websocket.close(code=4500, reason="Proxy error")
        except Exception:
            pass




























# â”€â”€â”€ Session-based REST endpoints â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _subnet_base(network_subnet: str | None) -> str | None:
    if not network_subnet:
        return None
    try:
        return ".".join(network_subnet.split("/")[0].split(".")[:3])
    except (AttributeError, IndexError):
        return None


def _json_list(raw) -> list:
    if not raw:
        return []
    try:
        value = json.loads(raw) if isinstance(raw, str) else raw
        return value if isinstance(value, list) else []
    except (TypeError, ValueError):
        return []


def _rangebox_lab_context(db: Session, session: LabSession, current_user: User) -> dict:
    """Lab details the RangeBox window needs for the flag and IP dock.

    The exercise page used to be the only place that knew the target IPs and
    the flag form. Passing the same information into the RangeBox page lets a
    learner stay on the desktop while reading the addresses and submitting the
    flag.
    """
    lab = db.query(Lab).filter(Lab.id == session.lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Exercise not found")

    reveal_ips = bool(getattr(lab, "show_target_ips", False))
    base = _subnet_base(session.network_subnet) if reveal_ips else None

    target_ips = []
    if base:
        for node in _json_list(lab.topology_nodes):
            try:
                offset = int(node.get("ip_offset"))
            except (TypeError, ValueError, AttributeError):
                continue
            target_ips.append({
                "id": node.get("id", ""),
                "label": node.get("label") or node.get("id") or "Target",
                "ip": f"{base}.{offset}",
            })

    hostnames = []
    for entry in _json_list(lab.hostnames):
        if not isinstance(entry, dict):
            continue
        hostname = entry.get("hostname")
        if not hostname:
            continue
        ip = None
        if base:
            try:
                ip = f"{base}.{int(entry.get('ip_offset'))}"
            except (TypeError, ValueError):
                ip = None
        hostnames.append({
            "hostname": hostname,
            "description": entry.get("description", ""),
            "ip": ip,
        })

    completed = db.query(LabCompletion.id).filter(
        LabCompletion.user_id == current_user.id,
        LabCompletion.lab_id == lab.id,
        LabCompletion.flag_submitted.isnot(None),
        LabCompletion.flag_submitted != "",
    ).first() is not None

    # Prefer the course that assigned this lab, so a correct answer counts for
    # course credit when the RangeBox was opened from a course exercise.
    course_id = None
    enrollment = db.query(CourseEnrollment).join(
        CourseLabAssignment,
        CourseLabAssignment.course_id == CourseEnrollment.course_id,
    ).filter(
        CourseEnrollment.user_id == current_user.id,
        CourseLabAssignment.lab_id == lab.id,
    ).order_by(CourseEnrollment.enrolled_at.desc()).first()
    if enrollment:
        course_id = enrollment.course_id

    return {
        "session_id": session.id,
        "lab_id": lab.id,
        "lab_slug": lab.slug,
        "lab_name": lab.name,
        "network_subnet": session.network_subnet,
        "target_ips": target_ips,
        "hostnames": hostnames,
        "completed": completed,
        "course_id": course_id,
    }


@router.get("/{session_id}/lab")
async def rangebox_lab(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return the lab name, target IPs, and flag state for this RangeBox."""
    session = db.query(LabSession).filter(
        LabSession.id == session_id,
        LabSession.user_id == current_user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _rangebox_lab_context(db, session, current_user)


@router.get("/{session_id}/status")
async def rangebox_status(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get RangeBox container status for an active lab session."""
    session = db.query(LabSession).filter(
        LabSession.id == session_id,
        LabSession.user_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.rangebox_enabled:
        raise HTTPException(status_code=400, detail="RangeBox not enabled for this session")

    lab = db.query(Lab).filter(Lab.id == session.lab_id).first()
    lab_slug = lab.slug if lab else "unknown"

    return docker_manager.get_rangebox_status(current_user.id, lab_slug)


# â”€â”€â”€ Session-based WebSocket VNC proxy â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.websocket("/{session_id}/vnc")
async def rangebox_vnc_proxy(
    websocket: WebSocket,
    session_id: int,
    token: str = Query(default=""),
):
    """
    Bidirectional WebSocket proxy between the browser (noVNC client)
    and the RangeBox container's websockify server.

    Auth: JWT passed as ?token= query parameter.
    """
    # â”€â”€ 1. Authenticate â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if not token:
        await websocket.close(code=4401, reason="Missing token")
        return

    user_id, ws_imp = await _authenticate_ws(token)
    if user_id is None:
        await websocket.close(code=4401, reason="Invalid token")
        return

    # â”€â”€ 2. Validate session ownership â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    db = SessionLocal()
    try:
        session = db.query(LabSession).filter(
            LabSession.id == session_id,
            LabSession.user_id == user_id,
            LabSession.status == "running",
        ).first()

        if not session:
            await websocket.close(code=4404, reason="No active session")
            return

        if not session.rangebox_enabled:
            await websocket.close(code=4400, reason="RangeBox not enabled")
            return

        lab = db.query(Lab).filter(Lab.id == session.lab_id).first()
        lab_slug = lab.slug if lab else "unknown"
    finally:
        db.close()

    # â”€â”€ 3. Resolve RangeBox container address â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    rangebox_ip = docker_manager.get_rangebox_ip(user_id, lab_slug)
    if not rangebox_ip:
        await websocket.close(code=4500, reason="RangeBox IP not found")
        return

    rangebox_ws_url = f"ws://{rangebox_ip}:{docker_manager.RANGEBOX_NOVNC_PORT}/websockify"

    # â”€â”€ 4. Connect to the upstream RangeBox websockify â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    try:
        import aiohttp
    except ImportError:
        logger.error("aiohttp is required for RangeBox WebSocket proxy. pip install aiohttp")
        await websocket.close(code=4500, reason="Server configuration error")
        return

    await websocket.accept(subprotocol="binary")

    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.ws_connect(
                rangebox_ws_url,
                protocols=["binary"],
                max_msg_size=16 * 1024 * 1024,  # 16MB â€” VNC can send large frames
            ) as upstream:
                # â”€â”€ 5. Bidirectional relay â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

                async def browser_to_container():
                    """Forward messages from browser â†’ RangeBox."""
                    try:
                        while True:
                            msg = await websocket.receive()
                            if msg["type"] == "websocket.receive":
                                # Read-only "View As": drain browser frames but
                                # never inject input into the student's session.
                                if ws_imp:
                                    continue
                                if "bytes" in msg and msg["bytes"]:
                                    await upstream.send_bytes(msg["bytes"])
                                elif "text" in msg and msg["text"]:
                                    await upstream.send_str(msg["text"])
                            elif msg["type"] == "websocket.disconnect":
                                break
                    except WebSocketDisconnect:
                        pass
                    except Exception as e:
                        logger.debug(f"browserâ†’container relay ended: {e}")
                    finally:
                        await upstream.close()

                async def container_to_browser():
                    """Forward messages from RangeBox â†’ browser."""
                    try:
                        async for msg in upstream:
                            if msg.type == aiohttp.WSMsgType.BINARY:
                                await websocket.send_bytes(msg.data)
                            elif msg.type == aiohttp.WSMsgType.TEXT:
                                await websocket.send_text(msg.data)
                            elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
                                break
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                break
                    except Exception as e:
                        logger.debug(f"containerâ†’browser relay ended: {e}")
                    finally:
                        try:
                            await websocket.close()
                        except Exception:
                            pass

                # Run both directions concurrently; when either ends, cancel the other
                done, pending = await asyncio.wait(
                    [
                        asyncio.create_task(browser_to_container()),
                        asyncio.create_task(container_to_browser()),
                    ],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

    except aiohttp.ClientError as e:
        logger.warning(f"Failed to connect to RangeBox websockify at {rangebox_ws_url}: {e}")
        try:
            await websocket.close(code=4502, reason="RangeBox not ready")
        except Exception:
            pass
    except Exception as e:
        logger.warning(f"RangeBox VNC proxy error: {e}")
        try:
            await websocket.close(code=4500, reason="Proxy error")
        except Exception:
            pass


# â”€â”€â”€ Admin: view a student's RangeBox VNC session â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.websocket("/admin/{target_user_id}/{session_id}/vnc")
async def admin_rangebox_vnc_proxy(
    websocket: WebSocket,
    target_user_id: int,
    session_id: int,
    token: str = Query(default=""),
):
    """
    Admin-only WebSocket proxy to view a student's RangeBox.
    Authenticates the caller as an admin, then proxies VNC to
    the target student's RangeBox container.
    """
    # â”€â”€ 1. Authenticate caller â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if not token:
        await websocket.close(code=4401, reason="Missing token")
        return

    admin_user_id, _ws_imp = await _authenticate_ws(token)
    if admin_user_id is None:
        await websocket.close(code=4401, reason="Invalid token")
        return

    # â”€â”€ 2. Verify caller is an admin â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.id == admin_user_id, User.is_active == True).first()
        if not admin or admin.role != "admin":
            await websocket.close(code=4403, reason="Admin access required")
            return

        # â”€â”€ 3. Look up the target student's session â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        session = db.query(LabSession).filter(
            LabSession.id == session_id,
            LabSession.user_id == target_user_id,
            LabSession.status == "running",
        ).first()

        if not session:
            await websocket.close(code=4404, reason="No active session for target user")
            return

        lab = db.query(Lab).filter(Lab.id == session.lab_id).first()
        lab_slug = lab.slug if lab else "unknown"
        has_session_rangebox = bool(session.rangebox_enabled)
    finally:
        db.close()

    # â”€â”€ 4. Resolve target student's RangeBox IP â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Try lab-specific RangeBox first, then fall back to standalone.
    # get_rangebox_ip() always returns a computed IP (never None),
    # so we verify the container actually exists before using it.
    rangebox_ip = None
    if has_session_rangebox:
        lab_rb_status = docker_manager.get_rangebox_status(target_user_id, lab_slug, include_stats=False)
        if lab_rb_status.get("status") == "running":
            rangebox_ip = docker_manager.get_rangebox_ip(target_user_id, lab_slug)

    # Fall back to standalone RangeBox (student may be using standalone
    # even if the lab session itself doesn't have rangebox_enabled)
    if not rangebox_ip:
        standalone_status = docker_manager.get_standalone_rangebox_status(target_user_id, include_stats=False)
        if standalone_status.get("status") == "running":
            rangebox_ip = docker_manager.get_standalone_rangebox_ip(target_user_id)

    if not rangebox_ip:
        await websocket.close(code=4500, reason="Student RangeBox not found or not running")
        return

    rangebox_ws_url = f"ws://{rangebox_ip}:{docker_manager.RANGEBOX_NOVNC_PORT}/websockify"
    logger.info(f"Admin {admin.username} viewing RangeBox for user {target_user_id} session {session_id}")

    # â”€â”€ 5. Proxy (same relay logic as regular endpoint) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    try:
        import aiohttp
    except ImportError:
        await websocket.close(code=4500, reason="Server configuration error")
        return

    await websocket.accept(subprotocol="binary")

    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.ws_connect(
                rangebox_ws_url,
                protocols=["binary"],
                max_msg_size=16 * 1024 * 1024,
            ) as upstream:

                async def browser_to_container():
                    try:
                        while True:
                            msg = await websocket.receive()
                            if msg["type"] == "websocket.receive":
                                if "bytes" in msg and msg["bytes"]:
                                    await upstream.send_bytes(msg["bytes"])
                                elif "text" in msg and msg["text"]:
                                    await upstream.send_str(msg["text"])
                            elif msg["type"] == "websocket.disconnect":
                                break
                    except WebSocketDisconnect:
                        pass
                    except Exception as e:
                        logger.debug(f"admin browserâ†’container relay ended: {e}")
                    finally:
                        await upstream.close()

                async def container_to_browser():
                    try:
                        async for msg in upstream:
                            if msg.type == aiohttp.WSMsgType.BINARY:
                                await websocket.send_bytes(msg.data)
                            elif msg.type == aiohttp.WSMsgType.TEXT:
                                await websocket.send_text(msg.data)
                            elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
                                break
                            elif msg.type == aiohttp.WSMsgType.ERROR:
                                break
                    except Exception as e:
                        logger.debug(f"admin containerâ†’browser relay ended: {e}")
                    finally:
                        try:
                            await websocket.close()
                        except Exception:
                            pass

                done, pending = await asyncio.wait(
                    [
                        asyncio.create_task(browser_to_container()),
                        asyncio.create_task(container_to_browser()),
                    ],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

    except Exception as e:
        logger.warning(f"Admin RangeBox VNC proxy error: {e}")
        try:
            await websocket.close(code=4500, reason="Proxy error")
        except Exception:
            pass
