#!/usr/bin/env python3
"""Dependency-free secret and workflow-risk audit for this repository."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRET_PATTERNS = [
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{30,})\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Private key PEM", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
]
PLACEHOLDER = re.compile(r"(?:YOUR[_ -]?KEY|REPLACE[_ -]?ME|EXAMPLE|PLACEHOLDER|\$\{\{\s*secrets\.)", re.I)
ACTION_USE = re.compile(r"(?m)^\s*-\s*uses:\s*([^\s#]+)")


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [ROOT / p.decode("utf-8") for p in result.stdout.split(b"\0") if p]


def main() -> None:
    findings: list[str] = []
    files = tracked_files()
    for path in files:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            for label, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{path.relative_to(ROOT)}:{number}: possible {label}")
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith(".github/workflows/") and path.suffix in {".yml", ".yaml"}:
            if re.search(r"(?m)^\s*permissions:\s*write-all\s*$", text):
                findings.append(f"{relative}: avoid permissions: write-all; grant only required permissions")
            if re.search(r"(?m)^\s*pull_request_target\s*:", text):
                findings.append(f"{relative}: review pull_request_target carefully for untrusted code execution")
            for match in ACTION_USE.finditer(text):
                action_ref = match.group(1)
                if action_ref.startswith("./"):
                    continue
                if "@" not in action_ref:
                    findings.append(f"{relative}: action reference has no version or SHA: {action_ref}")
                    continue
                revision = action_ref.rsplit("@", 1)[1]
                if not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
                    findings.append(
                        f"{relative}: third-party action is not pinned to a full 40-character commit SHA: {action_ref}"
                    )

    if findings:
        print("Security audit found items requiring review:")
        for finding in findings:
            print(f"- {finding}")
        raise SystemExit(1)
    print(
        f"Security audit passed: scanned {len(files)} tracked files; "
        "no known secret patterns or flagged workflow settings found, and external Actions are SHA-pinned."
    )


if __name__ == "__main__":
    main()
