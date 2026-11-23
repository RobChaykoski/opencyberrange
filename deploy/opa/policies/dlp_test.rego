package opencyberrange.dlp

import rego.v1

test_student_restricted_is_denied if {
  r := result with input as {
    "subject": {"role": "student"},
    "resource": {"classification": "restricted"},
    "action": "export",
  }
  r.decision == "deny"
}

test_public_is_allowed if {
  r := result with input as {
    "subject": {"role": "student"},
    "resource": {"classification": "public"},
    "action": "read",
  }
  r.decision == "allow"
}

test_training_pii_is_masked if {
  r := result with input as {
    "subject": {"role": "student"},
    "resource": {"classification": "internal", "training_data": true, "contains_pii": true},
    "action": "read",
  }
  r.decision == "mask"
}

test_secret_material_is_denied if {
  r := result with input as {
    "subject": {"role": "instructor"},
    "resource": {"classification": "restricted", "contains_secrets": true},
    "action": "export",
  }
  r.decision == "deny"
}

test_answer_key_publication_is_denied if {
  r := result with input as {
    "subject": {"role": "instructor"},
    "resource": {"classification": "restricted", "contains_assessment_answer_key": true},
    "action": "publish",
  }
  r.decision == "deny"
}

test_unsafe_publication_is_denied if {
  r := result with input as {
    "subject": {"role": "instructor"},
    "resource": {"classification": "internal", "publication_safe": false},
    "action": "publish",
  }
  r.decision == "deny"
}

test_infrastructure_metadata_export_requires_approval if {
  r := result with input as {
    "subject": {"role": "instructor"},
    "resource": {"classification": "confidential", "contains_infrastructure_metadata": true},
    "action": "export",
  }
  r.decision == "require_approval"
}

test_answer_key_export_requires_approval if {
  r := result with input as {
    "subject": {"role": "instructor"},
    "resource": {"classification": "restricted", "contains_assessment_answer_key": true},
    "action": "export",
  }
  r.decision == "require_approval"
}

test_clean_internal_publication_is_allowed if {
  r := result with input as {
    "subject": {"role": "instructor"},
    "resource": {"classification": "internal", "publication_safe": true},
    "action": "publish",
  }
  r.decision == "allow"
}

test_pipeda_export_requires_approval if {
  r := result with input as {
    "subject": {"role": "instructor"},
    "resource": {"classification": "confidential", "contains_pii": true, "jurisdiction": "canada"},
    "action": "export",
  }
  r.decision == "require_approval"
}

test_pipeda_external_share_requires_approval if {
  r := result with input as {
    "subject": {"role": "instructor"},
    "resource": {"classification": "confidential", "contains_pii": true, "jurisdiction": "canada"},
    "action": "external_share",
  }
  r.decision == "require_approval"
}

test_security_analyst_can_read_restricted if {
  r := result with input as {
    "subject": {"role": "security-analyst"},
    "resource": {"classification": "restricted"},
    "action": "read",
  }
  r.decision == "allow"
}

test_unknown_metadata_is_denied if {
  r := result with input as {
    "subject": {"role": "instructor"},
    "resource": {"classification": "unknown"},
    "action": "read",
  }
  r.decision == "deny"
}
