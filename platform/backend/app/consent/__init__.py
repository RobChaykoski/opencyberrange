"""Consent and revocation bounded context.

The package owns learner consent state, the immutable revocation event trail,
the durable purge/verify job queue, proof-only audit records, and the
suppression ledger that protects against backup restores. It never stores the
content of deleted records.
"""
