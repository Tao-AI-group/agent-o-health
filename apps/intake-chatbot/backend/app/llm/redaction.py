from __future__ import annotations

import re


SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+"),
    re.compile(r"(?i)((?:client_secret|access_token|api_key)\s*[:=]\s*)[^\s,;]+"),
)


def redact(value: str) -> str:
    result = value
    for pattern in SECRET_PATTERNS:
        result = pattern.sub(r"\1[REDACTED]", result)
    return result


def safe_error(exc: Exception) -> str:
    text = redact(str(exc))
    return text[:500] if text else exc.__class__.__name__
