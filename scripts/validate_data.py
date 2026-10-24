#!/usr/bin/env python3
"""Validate the repository's structured free-LLM API catalogue without network calls."""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

DATA_FILE = Path(__file__).resolve().parents[1] / "data.json"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Missing data file: {DATA_FILE}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")

    if not isinstance(data, dict):
        fail("Top-level JSON value must be an object.")

    updated = data.get("lastUpdated")
    if not isinstance(updated, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", updated):
        fail("lastUpdated must use YYYY-MM-DD format.")
    try:
        if date.fromisoformat(updated).isoformat() != updated:
            fail("lastUpdated must be a valid calendar date in YYYY-MM-DD format.")
    except ValueError:
        fail("lastUpdated must be a valid calendar date in YYYY-MM-DD format.")

    providers = data.get("providers")
    if not isinstance(providers, list) or not providers:
        fail("providers must be a non-empty array.")

    provider_names: set[str] = set()
    total_models = 0
    errors: list[str] = []

    for index, provider in enumerate(providers):
        label = f"providers[{index}]"
        if not isinstance(provider, dict):
            errors.append(f"{label} must be an object")
            continue

        name = provider.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{label}.name must be a non-empty string")
        elif name.casefold() in provider_names:
            errors.append(f"duplicate provider name: {name}")
        else:
            provider_names.add(name.casefold())

        for field in ("url", "baseUrl"):
            value = provider.get(field)
            if not isinstance(value, str):
                errors.append(f"{label}.{field} must be a URL string")
                continue
            parsed = urlparse(value)
            if parsed.scheme != "https" or not parsed.netloc:
                errors.append(f"{label}.{field} must be an absolute HTTPS URL")

        models = provider.get("models")
        if not isinstance(models, list) or not models:
            errors.append(f"{label}.models must be a non-empty array")
            continue

        model_ids: set[str] = set()
        for model_index, model in enumerate(models):
            model_label = f"{label}.models[{model_index}]"
            if not isinstance(model, dict):
                errors.append(f"{model_label} must be an object")
                continue
            model_id = model.get("id")
            model_name = model.get("name")
            if not isinstance(model_name, str) or not model_name.strip():
                errors.append(f"{model_label}.name must be a non-empty string")
            # Some providers intentionally summarize a long catalogue with entries
            # such as "+ 55 more models"; those aggregate rows have no concrete ID.
            is_summary_row = isinstance(model_name, str) and model_name.strip().startswith("+ ")
            if model_id is None and is_summary_row:
                pass
            elif not isinstance(model_id, str) or not model_id.strip():
                errors.append(f"{model_label}.id must be a non-empty string unless this is a summary row")
            elif model_id.casefold() in model_ids:
                errors.append(f"{label} has duplicate model id: {model_id}")
            else:
                model_ids.add(model_id.casefold())
            total_models += 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)

    print(f"Catalogue validation passed: {len(providers)} providers, {total_models} models.")


if __name__ == "__main__":
    main()
