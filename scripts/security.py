"""Secret filtering before any model call, and before publishing."""

from __future__ import annotations

import re
from pathlib import PurePosixPath

SECRET_FILENAMES = {
    ".env",
    "credentials.json",
    "credentials.json.enc",
    "id_rsa",
    "id_ed25519",
}

SECRET_FILENAME_PATTERNS = (
    re.compile(r"^\.env\..+", re.IGNORECASE),
    re.compile(r".*\.pem$", re.IGNORECASE),
    re.compile(r".*\.key$", re.IGNORECASE),
    re.compile(r"^secrets?\..+", re.IGNORECASE),
    re.compile(r".*credential.*", re.IGNORECASE),
)

SECRET_LINE_PATTERNS = (
    re.compile(r"OPENAI_API_KEY\s*=", re.IGNORECASE),
    re.compile(r"ANTHROPIC_API_KEY\s*=", re.IGNORECASE),
    re.compile(r"GEMINI_API_KEY\s*=", re.IGNORECASE),
    re.compile(r"GITHUB_TOKEN\s*=", re.IGNORECASE),
    re.compile(r"GH_TOKEN\s*=", re.IGNORECASE),
    re.compile(r"AWS_ACCESS_KEY(_ID)?\s*=", re.IGNORECASE),
    re.compile(r"AWS_SECRET_ACCESS_KEY\s*=", re.IGNORECASE),
    re.compile(r"PRIVATE_KEY", re.IGNORECASE),
    re.compile(r"BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY"),
    re.compile(r"PASSWORD\s*=", re.IGNORECASE),
    re.compile(r"SECRET(_KEY)?\s*=", re.IGNORECASE),
    re.compile(r"TOKEN\s*=", re.IGNORECASE),
    re.compile(r"api[_-]?key\s*[:=]", re.IGNORECASE),
    re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{20,}"),
)

REDACTION = "[REDACTED BY ORPHEON]"


def is_secret_path(path: str) -> bool:
    name = PurePosixPath(path).name
    if name in SECRET_FILENAMES:
        return True
    return any(pattern.match(name) for pattern in SECRET_FILENAME_PATTERNS)


def sanitize_line(line: str) -> str | None:
    if any(pattern.search(line) for pattern in SECRET_LINE_PATTERNS):
        return None
    return line


def sanitize_text(text: str | None) -> str:
    if not text:
        return ""
    kept: list[str] = []
    for line in text.splitlines():
        clean = sanitize_line(line)
        if clean is None:
            kept.append(REDACTION)
        else:
            kept.append(clean)
    return "\n".join(kept)


def contains_secret(text: str | None) -> bool:
    if not text:
        return False
    return any(pattern.search(text) for pattern in SECRET_LINE_PATTERNS)


def looks_like_private_url(url: str) -> bool:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme == "file":
        return True
    host = (parsed.hostname or "").lower()
    if host in {"localhost", "127.0.0.1", "::1"}:
        return True
    if host.endswith(".internal") or host.endswith(".local") or host.endswith(".lan"):
        return True
    parts = host.split(".")
    if len(parts) == 4 and all(part.isdigit() for part in parts):
        a, b = int(parts[0]), int(parts[1])
        if a == 10 or a == 127 or (a == 192 and b == 168) or (a == 172 and 16 <= b <= 31):
            return True
    return False
