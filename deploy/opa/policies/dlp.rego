package opencyberrange.dlp

import rego.v1

# Ordered policy for the Release 6 MVP. The first matching branch wins.
result := {
  "decision": "deny",
  "reason": "Secret material cannot leave the controlled environment.",
  "obligations": ["block:secrets"],
} if {
  input.resource.contains_secrets
  input.action in {"publish", "export", "external_share"}
} else := {
  "decision": "deny",
  "reason": "Assessment answer keys cannot be published or externally shared.",
  "obligations": ["block:assessment-answer-key"],
} if {
  input.resource.contains_assessment_answer_key
  input.action in {"publish", "external_share"}
} else := {
  "decision": "deny",
  "reason": "Resource is not approved for publication.",
  "obligations": ["block:publication"],
} if {
  input.resource.publication_safe == false
  input.action == "publish"
} else := {
  "decision": "require_approval",
  "reason": "Infrastructure metadata requires review and redaction before export.",
  "obligations": ["approval:infrastructure-metadata", "redact:infrastructure-metadata"],
} if {
  input.resource.contains_infrastructure_metadata
  input.action in {"export", "external_share"}
} else := {
  "decision": "require_approval",
  "reason": "Assessment answer keys require approval and redaction before export.",
  "obligations": ["approval:assessment-answer-key", "redact:assessment-answer-key"],
} if {
  input.resource.contains_assessment_answer_key
  input.action == "export"
} else := {
  "decision": "deny",
  "reason": "Students cannot export restricted resources.",
  "obligations": [],
} if {
  input.resource.classification == "restricted"
  input.subject.role == "student"
} else := {
  "decision": "require_approval",
  "reason": "PII shared outside the organisation requires approval under PIPEDA.",
  "obligations": ["approval:pipeda-pii"],
} if {
  input.action in {"export", "external_share"}
  input.resource.contains_pii
  input.resource.jurisdiction == "canada"
} else := {
  "decision": "mask",
  "reason": "Synthetic training PII is masked for students.",
  "obligations": ["mask:pii"],
} if {
  input.resource.training_data
  input.resource.contains_pii
  input.subject.role == "student"
} else := {
  "decision": "allow",
  "reason": "Public resource.",
  "obligations": [],
} if {
  input.resource.classification == "public"
} else := {
  "decision": "allow",
  "reason": "Role may read restricted resources.",
  "obligations": [],
} if {
  input.resource.classification == "restricted"
  input.subject.role in {"security-analyst", "admin"}
} else := {
  "decision": "allow",
  "reason": "No blocking policy matched.",
  "obligations": [],
} if {
  input.resource.classification in {"internal", "confidential"}
} else := {
  "decision": "deny",
  "reason": "No policy permits this action.",
  "obligations": [],
}
