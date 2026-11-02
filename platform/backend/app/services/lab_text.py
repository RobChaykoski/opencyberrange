"""Render lab-authored text for a specific lab session.

Lab YAML uses the tester grammar (``{target.NODE}``, ``{subnet}``) so the same
lab definition works on any per-student subnet. The lab tester resolves those
placeholders at run time; student-facing text must resolve them too, otherwise
the scenario and hints show the raw placeholder and the learner cannot tell
which address to use.

Authoring rules:

- ``{target.<node id>}`` resolves to the node's address on the session subnet.
- ``{subnet}`` resolves to the session subnet in CIDR form.
- Unknown node ids are left untouched so a typo is visible in review rather
  than silently rendering an empty string.
"""
import json
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

_TARGET_RE = re.compile(r"\{target\.([A-Za-z0-9_]+)\}")
_SUBNET_RE = re.compile(r"\{subnet\}")


def target_address_map(lab, session) -> dict:
    """Map topology node ids to addresses on ``session``'s subnet."""
    subnet = getattr(session, "network_subnet", None) if session else None
    if not subnet:
        return {}
    try:
        nodes = (
            json.loads(lab.topology_nodes)
            if getattr(lab, "topology_nodes", None)
            else []
        )
    except Exception:
        logger.warning("Could not parse topology_nodes for lab %s", getattr(lab, "id", "?"))
        return {}
    base = ".".join(subnet.split("/")[0].split(".")[:3])
    addresses = {}
    for node in nodes or []:
        node_id = node.get("id")
        offset = node.get("ip_offset")
        if node_id and offset not in (None, ""):
            addresses[str(node_id)] = f"{base}.{offset}"
    return addresses


def render_lab_text(text: Optional[str], lab, session) -> Optional[str]:
    """Resolve ``{target.X}``/``{subnet}`` placeholders in student-facing text."""
    if not text or not isinstance(text, str):
        return text

    addresses = target_address_map(lab, session)
    rendered = _TARGET_RE.sub(
        lambda match: addresses.get(match.group(1), match.group(0)), text
    )

    subnet = getattr(session, "network_subnet", None) if session else None
    if subnet:
        rendered = _SUBNET_RE.sub(subnet, rendered)
    return rendered
