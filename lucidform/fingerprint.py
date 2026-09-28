import hashlib


def fingerprint(field_id: str, normalized_value: str, candidate_id: str) -> str:
    """Binds a receipt to one exact (field, value, candidate). Recomputed at commit, never trusted."""
    return hashlib.sha256("\x1f".join((field_id, normalized_value, candidate_id)).encode()).hexdigest()
