#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAX_SCAN_BYTES = 2_000_000

SENSITIVE_FILE = re.compile(
    r"(^|/)(\.env($|\.)|.*(?:credential|secret).*(?:\.json|\.jsonl)$|.*\.pem$)",
    re.IGNORECASE,
)
PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
SECRET_ASSIGNMENT = re.compile(
    r"(?:client_secret|access_token|api[_-]?key)\s*[=:]\s*[\"']([^\"']{12,})[\"']",
    re.IGNORECASE,
)
SAFE_MARKERS = (
    "[redacted]",
    "<redacted>",
    "placeholder",
    "synthetic",
    "test-access-token",
    "never-show-this-value",
    "random-token",
    "example",
)


def candidate_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )
    return [PROJECT_ROOT / item.decode() for item in result.stdout.split(b"\0") if item]


def scan_file(path: Path) -> list[tuple[int, str]]:
    if not path.is_file() or path.stat().st_size > MAX_SCAN_BYTES:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    findings: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if PRIVATE_KEY.search(line):
            findings.append((line_number, "private-key material"))
        for match in SECRET_ASSIGNMENT.finditer(line):
            candidate = match.group(1).lower()
            if not any(marker in candidate for marker in SAFE_MARKERS):
                findings.append((line_number, "literal secret assignment"))
    return findings


def main() -> int:
    findings: list[tuple[str, int | None, str]] = []
    files = candidate_files()
    for path in files:
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        if relative != ".env.example" and SENSITIVE_FILE.search(relative):
            findings.append((relative, None, "sensitive filename is not ignored"))
            continue
        findings.extend(
            (relative, line_number, reason)
            for line_number, reason in scan_file(path)
        )
    if findings:
        print("Potential secret material detected. Values are intentionally not displayed:")
        for filename, line_number, reason in findings:
            location = f"{filename}:{line_number}" if line_number else filename
            print(f"- {location}: {reason}")
        return 1
    print(f"Secret scan passed for {len(files)} candidate source files; no values displayed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
