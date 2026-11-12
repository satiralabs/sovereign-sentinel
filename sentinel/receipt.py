"""
SovereignSentinel Receipt: Cryptographic attestation of OSINT claims and source hashes.
"""

import hashlib
import json
import time
from typing import Any, Dict


def sha256_hash(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def generate_provenance_receipt(
    claim_evaluation: Dict[str, Any],
    auditor_id: str = "sentinel-engine-01",
) -> Dict[str, Any]:
    """Generates a verifiable audit receipt proving evidentiary basis for a verdict."""
    timestamp = time.time()
    payload = {
        "auditor_id": auditor_id,
        "timestamp": timestamp,
        "claim_id": claim_evaluation.get("claim_id"),
        "statement": claim_evaluation.get("statement"),
        "verdict": claim_evaluation.get("verdict"),
        "confidence": claim_evaluation.get("confidence"),
        "evidence_count": claim_evaluation.get("evidence_count"),
        "citations_hash": sha256_hash(json.dumps(claim_evaluation.get("citations", []), sort_keys=True)),
    }

    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    receipt_hash = sha256_hash(serialized)
    payload["receipt_hash"] = receipt_hash
    return payload
