"""Canonical MITRE ATT&CK mapping for lab manifests.

Every lab declares at least one tactic/technique/detection opportunity. The
rules here keep the catalog aligned with one taxonomy while still allowing a
hand-authored ``mitre_attack:`` block to override the default.
"""
from __future__ import annotations

import re

TECHNIQUE_NAMES = {
    "T1595": "Active Scanning",
    "T1592": "Gather Victim Host Information",
    "T1593": "Search Open Websites/Domains",
    "T1596": "Search Open Technical Databases",
    "T1590": "Gather Victim Network Information",
    "T1190": "Exploit Public-Facing Application",
    "T1078": "Valid Accounts",
    "T1566": "Phishing",
    "T1566.001": "Spearphishing Attachment",
    "T1204": "User Execution",
    "T1204.002": "Malicious File",
    "T1059": "Command and Scripting Interpreter",
    "T1059.004": "Unix Shell",
    "T1548": "Abuse Elevation Control Mechanism",
    "T1548.001": "Setuid and Setgid",
    "T1068": "Exploitation for Privilege Escalation",
    "T1562": "Impair Defenses",
    "T1027": "Obfuscated Files or Information",
    "T1003": "OS Credential Dumping",
    "T1110": "Brute Force",
    "T1110.001": "Password Guessing",
    "T1110.002": "Password Cracking",
    "T1552": "Unsecured Credentials",
    "T1552.003": "Bash History",
    "T1539": "Steal Web Session Cookie",
    "T1557": "Adversary-in-the-Middle",
    "T1040": "Network Sniffing",
    "T1046": "Network Service Discovery",
    "T1087": "Account Discovery",
    "T1083": "File and Directory Discovery",
    "T1018": "Remote System Discovery",
    "T1016": "System Network Configuration Discovery",
    "T1021": "Remote Services",
    "T1021.001": "Remote Desktop Protocol",
    "T1021.004": "SSH",
    "T1021.006": "Windows Remote Management",
    "T1039": "Data from Network Shared Drive",
    "T1005": "Data from Local System",
    "T1114": "Email Collection",
    "T1071": "Application Layer Protocol",
    "T1071.004": "DNS",
    "T1048.003": "Exfiltration Over Unencrypted Non-C2 Protocol",
    "T1041": "Exfiltration Over C2 Channel",
    "T1486": "Data Encrypted for Impact",
    "T0846": "Remote System Discovery (ICS)",
}

DETECTIONS = {
    "T1595": "Alert on active scanning and vulnerability-probe patterns in IDS/WAF logs.",
    "T1592": "Review service banners and host-identification telemetry for unusual fingerprinting.",
    "T1593": "Monitor public content, DNS, and certificate-transparency sources for exposure.",
    "T1596": "Scan code repositories and public datasets for leaked credentials or infrastructure.",
    "T1590": "Review DNS and network registration records for unexpected exposure.",
    "T1190": "Monitor web/WAF logs for exploit payloads and abnormal application errors.",
    "T1078": "Review authentication logs for valid-account use from unexpected sources.",
    "T1566": "Inspect mail-gateway and user-report telemetry for suspicious messages.",
    "T1566.001": "Detonate or sandbox attachments at the mail gateway and alert on execution.",
    "T1204": "Alert on user-launched files and suspicious child processes.",
    "T1204.002": "Monitor document and script execution with EDR and macro telemetry.",
    "T1059": "Log process creation and command-line arguments for unexpected interpreters.",
    "T1059.004": "Audit shell command history and process-execution telemetry.",
    "T1548": "Alert on privilege changes, sudo use, and elevated process creation.",
    "T1548.001": "Audit SUID/SGID binaries and execve telemetry for unexpected escalation.",
    "T1068": "Correlate exploit attempts with privilege changes and EDR alerts.",
    "T1562": "Alert on policy, filter, or logging changes that weaken defences.",
    "T1027": "Review static indicators, entropy, and signature results for obfuscated files.",
    "T1003": "Monitor credential-store access and LSASS or memory-analysis activity.",
    "T1110": "Alert on repeated authentication failures and account lockout events.",
    "T1110.001": "Correlate failed logons by source, account, and authentication service.",
    "T1110.002": "Monitor password-hash access and offline cracking indicators.",
    "T1552": "Review file, configuration, and secret-store access for exposed credentials.",
    "T1552.003": "Audit access to shell history files and command-line secrets.",
    "T1539": "Detect session-cookie reuse from different clients or networks.",
    "T1557": "Correlate authentication relay and man-in-the-middle network anomalies.",
    "T1040": "Inspect cleartext protocol traffic and span/mirror telemetry for sensitive data.",
    "T1046": "Monitor IDS/flow logs for service and port scanning.",
    "T1087": "Review directory, SAMR, and authentication logs for account enumeration.",
    "T1083": "Audit file and directory access telemetry for unusual enumeration.",
    "T1018": "Monitor host-discovery and ICMP sweep patterns.",
    "T1016": "Review host network-configuration and interface changes.",
    "T1021": "Correlate remote logons across hosts and protocols.",
    "T1021.001": "Review RDP authentication, session, and source-host logs.",
    "T1021.004": "Review SSH authentication and command-execution logs.",
    "T1021.006": "Review WinRM authentication and command logs.",
    "T1039": "Audit network-share file access and transfer volume.",
    "T1005": "Monitor bulk file access and collection from local systems.",
    "T1114": "Review mail-gateway and mailbox access logs for collection activity.",
    "T1071": "Detect beaconing and application-layer C2 in network flow data.",
    "T1071.004": "Alert on DNS query volume, entropy, and unusual record types.",
    "T1048.003": "Monitor outbound non-standard protocols for data volume anomalies.",
    "T1041": "Correlate egress volume with known C2 channels and blocked destinations.",
    "T1486": "Alert on mass file encryption and backup-integrity changes.",
    "T0846": "Monitor Modbus function-code scans and unauthorized register reads.",
}

# (pattern, [(tactic, technique[, detection])...]) in priority order.
_RULES = [
    ("^linux-1-7-", [("Discovery", "T1018")]),
    ("^linux-1-8-", [("Discovery", "T1046")]),
    ("^linux-2-1-", [("Initial Access", "T1078")]),
    ("^linux-2-2-", [("Discovery", "T1087")]),
    ("^linux-2-3-", [("Discovery", "T1083")]),
    ("^linux-2-4-", [("Execution", "T1059.004")]),
    ("^linux-2-5-", [("Credential Access", "T1552.003")]),
    ("^linux-2-6-", [("Privilege Escalation", "T1548")]),
    ("^linux-2-[78]-", [("Discovery", "T1083")]),
    ("^linux-2-[89]-", [("Credential Access", "T1552")]),
    ("^linux-2-10-", [("Discovery", "T1087")]),
    ("^linux-3-[13]-", [("Privilege Escalation", "T1548.001")]),
    ("^linux-3-2-", [("Credential Access", "T1110.002")]),
    ("^linux-3-4-", [("Credential Access", "T1557")]),
    ("^linux-4-[13]-", [("Lateral Movement", "T1021")]),
    ("^linux-4-2-", [("Collection", "T1005")]),
    ("^linux-4-4-", [("Exfiltration", "T1041")]),
    ("^linux-5-[46]-", [("Credential Access", "T1110")]),
    ("^linux-5-[57]-", [("Initial Access", "T1190")]),
    ("^linux-(?:9-|midterm|final)", [("Lateral Movement", "T1021")]),
    ("^linux-1-", [("Discovery", "T1046")]),

    ("^network-0-1-", [("Discovery", "T1018")]),
    ("^network-0-2-", [("Reconnaissance", "T1590")]),
    ("^network-0-3-", [("Discovery", "T1016")]),
    ("^network-1-1-packet-capture-analysis", [("Command and Control", "T1071")]),
    ("^network-1-1-port-scan-detection", [("Discovery", "T1046")]),
    ("^network-1-2-http-traffic-analysis", [("Collection", "T1040")]),
    ("^network-1-2-log-correlation", [("Credential Access", "T1110")]),
    ("^network-1-3-dns-anomaly-detection", [("Command and Control", "T1071.004")]),
    ("^network-1-4-failed-login-analysis", [("Credential Access", "T1110")]),
    ("^network-1-", [("Discovery", "T1046")]),
    ("^network-2-1-", [("Credential Access", "T1040")]),
    ("^network-2-2-", [("Collection", "T1114")]),
    ("^network-2-3-", [("Credential Access", "T1539")]),
    ("^network-2-4-", [("Exfiltration", "T1048.003")]),
    ("^network-2-5-", [("Command and Control", "T1071")]),
    ("^network-2-", [("Collection", "T1040")]),
    ("^network-12-1-", [("Initial Access", "T1190")]),
    ("^network-12-2-", [("Lateral Movement", "T1021")]),

    ("^windows-1-", [("Discovery", "T1046")]),
    ("^windows-2-3-", [("Discovery", "T1083")]),
    ("^windows-2-4-", [("Collection", "T1039")]),
    ("^windows-2-5-", [("Discovery", "T1087")]),
    ("^windows-2-6-", [("Discovery", "T1083")]),
    ("^windows-2-7-", [("Discovery", "T1087")]),
    ("^windows-2-8-", [("Discovery", "T1087"), ("Discovery", "T1083")]),
    ("^windows-2-", [("Discovery", "T1083")]),
    ("^windows-3-4-", [("Discovery", "T1087"), ("Credential Access", "T1110")]),
    ("^windows-3-", [("Credential Access", "T1110")]),
    ("^windows-4-[12]-", [("Discovery", "T1046")]),
    ("^windows-4-[3-6]-", [("Lateral Movement", "T1021.001")]),
    ("^windows-5-[12]-", [("Discovery", "T1046")]),
    ("^windows-5-[34]-", [("Credential Access", "T1110")]),
    ("^windows-5-[56]-", [("Execution", "T1021.006")]),
    ("^windows-6-[12]-", [("Discovery", "T1046")]),
    ("^windows-6-[34]-", [("Credential Access", "T1110")]),
    ("^windows-6-[5-7]-", [("Execution", "T1059")]),
    ("^windows-7-", [("Discovery", "T1087")]),
    ("^windows-8-", [("Credential Access", "T1552")]),
    ("^windows-(?:9-|10-)", [("Lateral Movement", "T1021")]),

    ("^malware-1-1-", [("Execution", "T1204")]),
    ("^malware-1-[23]-", [("Defense Evasion", "T1027")]),
    ("^malware-1-[45]-", [("Command and Control", "T1071")]),
    ("^malware-1-6-", [("Initial Access", "T1566.001")]),
    ("^malware-1-7-", [("Execution", "T1204.002")]),
    ("^malware-2-1-", [("Defense Evasion", "T1027")]),
    ("^forensics-1-1-", [("Credential Access", "T1003")]),
    ("^forensics-2-1-", [("Collection", "T1040")]),
    ("^osint-1-1-", [("Reconnaissance", "T1593")]),
    ("^osint-1-2-", [("Reconnaissance", "T1592")]),
    ("^osint-1-3-", [("Reconnaissance", "T1592")]),
    ("^osint-2-1-", [("Reconnaissance", "T1596")]),
    ("^osint-2-2-", [("Reconnaissance", "T1593")]),
    ("^ai-1-1-", [("Initial Access", "T1190")]),
    ("^ai-1-2-", [("Defense Evasion", "T1562")]),
    ("^ai-1-3-", [("Initial Access", "T1566")]),
    ("^ot-1-1-", [("Discovery", "T0846")]),
    ("^high-school-9-", [("Discovery", "T1083")]),
    ("^high-school-10-1-", [("Discovery", "T1016")]),
    ("^high-school-10-2-", [("Reconnaissance", "T1593")]),
    ("^high-school-11-1-", [("Discovery", "T1046")]),
    ("^high-school-12-1-", [("Reconnaissance", "T1593")]),
    ("^software-security-1-1-", [("Initial Access", "T1190")]),
    ("^software-security-2-1-", [("Execution", "T1059")]),

    ("^web-1-1-", [("Discovery", "T1083")]),
    ("^web-1-2-", [("Reconnaissance", "T1592")]),
    ("^web-1-3-", [("Reconnaissance", "T1595")]),
    ("^web-1-4-", [("Reconnaissance", "T1592")]),
    ("^web-1-5-", [("Reconnaissance", "T1593")]),
    ("^web-1-6-", [("Reconnaissance", "T1595")]),
    ("^web-1-[78]-", [("Initial Access", "T1190")]),
    ("^web-2-[125]-", [("Initial Access", "T1190")]),
    ("^web-2-3-", [("Execution", "T1059")]),
    ("^web-2-4-", [("Reconnaissance", "T1595")]),
    ("^web-3-1-", [("Discovery", "T1083")]),
    ("^web-3-2-", [("Execution", "T1059")]),
    ("^web-3-3-", [("Privilege Escalation", "T1068")]),
]

_COMPILED_RULES = [(re.compile(pattern), mappings) for pattern, mappings in _RULES]


def _entry(tactic, technique, detection=None):
    return {
        "tactic": tactic,
        "technique": technique,
        "technique_name": TECHNIQUE_NAMES.get(technique, ""),
        "detection": detection or DETECTIONS.get(
            technique, "Review relevant authentication, endpoint, and network logs."
        ),
    }


def mapping_for_lab(track, level, category, slug):
    """Return one or more ATT&CK mappings for a lab definition."""
    slug = (slug or "").lower()
    for pattern, mappings in _COMPILED_RULES:
        if pattern.match(slug):
            return [_entry(*mapping) for mapping in mappings]
    if (track or "").lower() == "ot":
        return [_entry("Discovery", "T0846")]
    if (track or "").lower() in ("forensics", "malware"):
        return [_entry("Defense Evasion", "T1027")]
    if (track or "").lower() == "osint":
        return [_entry("Reconnaissance", "T1593")]
    return [_entry("Discovery", "T1046")]


def validate_mapping(mapping):
    """Return a list of validation errors for one mitre_attack entry."""
    errors = []
    if not isinstance(mapping, dict):
        return ["mitre_attack entries must be mappings"]
    for key in ("tactic", "technique", "detection"):
        if not str(mapping.get(key) or "").strip():
            errors.append(f"mitre_attack.{key} is required")
    technique = str(mapping.get("technique") or "")
    if technique and not re.match(r"^T\d{4}(?:\.\d{3})?$", technique):
        errors.append(
            f"mitre_attack.technique must look like T1003 or T1071.004: {technique}"
        )
    return errors
