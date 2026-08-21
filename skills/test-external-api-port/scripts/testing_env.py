#!/usr/bin/env python3
"""Deterministic environment gate for the test-external-api-port workflow.

The executing agent must never choose environment values. This script owns
.external-api-testing.toml: `check` reports exactly which values are missing
(with the verbatim question to ask the user), `set` records confirmed answers,
and `preflight` refuses to clear a run until every value has config provenance,
every host answers over HTTP, and the packet has a legal status.

Only five values are ever asked: the three server URLs, the custom host
(which IS the tenant the scenarios run against), and its API key. Everything
else is fixed policy below — not configuration, not questions.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

CONFIG_NAME = ".external-api-testing.toml"
LEGAL_PACKET_STATUSES = {"DISCOVERY", "BLOCKED", "READY", "IMPLEMENTING", "IMPLEMENTED", "VERIFIED"}

# Fixed policy — never asked, never configured.
LEGACY_TOKEN_ENV = "TM_TEST_LEGACY_TOKEN"   # auth token for legacy apps/api oracle calls
CORE_TOKEN_ENV = "TM_TEST_CORE_TOKEN"       # auth token for core-api oracle calls
REQUEST_TIMEOUT_MS = 15000
DELAY_BETWEEN_REQUESTS_MS = 250
ARTIFACTS_DIR = ".scratch/external-api-ports"

# (section, key, kind, question-to-ask-the-user-verbatim, redact-in-output)
FIELDS = (
    ("hosts", "external_api", "url",
     "Where is the EXTERNAL API server running (the apps/core-api serve exposing /external)? "
     "Full base URL, e.g. http://localhost:7070 or https://staging-core.tagmango.com.", False),
    ("hosts", "legacy_api", "url",
     "Where is the LEGACY apps/api server running? Full base URL (local or deployed).", False),
    ("hosts", "core_api", "url",
     "Where is the CORE apps/core-api server running? Full base URL (local or deployed).", False),
    ("auth", "external_custom_host", "string",
     "Which custom host should testing run against? (The custom host is the tenant; "
     "all scenarios and seeded data live under it.)", False),
    ("auth", "external_api_key", "string",
     "What is the external API key issued for that custom host?", True),
)

TEMPLATE = """# .external-api-testing.toml — runtime-testing environment for test-external-api-port.
# Managed by scripts/testing_env.py; every value is recorded from the user's answers.
# GITIGNORED — the API key below is a secret and never appears in run artifacts.
# Timeouts, delays, artifact locations, and oracle token env-var names are fixed
# policy inside testing_env.py, not configuration.

[hosts]
# Full base URLs before any global prefix/version, exactly as the user gave them.
external_api = @hosts.external_api@   # external surface (apps/core-api serve)
legacy_api   = @hosts.legacy_api@   # apps/api server used as the legacy oracle
core_api     = @hosts.core_api@   # apps/core-api server

[auth]
external_custom_host = @auth.external_custom_host@   # the tenant all scenarios run against
external_api_key     = @auth.external_api_key@   # external API key bound to that custom host

[provenance]
# Written only by `testing_env.py set`. A value whose entry here is not "user"
# was never confirmed in a session and is treated as a question, not an answer.
external_api         = @prov.external_api@
legacy_api           = @prov.legacy_api@
core_api             = @prov.core_api@
external_custom_host = @prov.external_custom_host@
external_api_key     = @prov.external_api_key@
"""


def config_path(repo: str) -> Path:
    return Path(repo).expanduser().resolve() / CONFIG_NAME


def parse_config(text: str) -> dict:
    data: dict = {}
    section = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        header = re.match(r"^\[([a-z_]+)\]$", line)
        if header:
            section = header.group(1)
            data.setdefault(section, {})
            continue
        pair = re.match(r"^([a-z_]+)\s*=\s*(.+)$", line)
        if pair and section is not None:
            key, raw_value = pair.group(1), pair.group(2).strip()
            if raw_value.startswith('"'):
                closing = raw_value.find('"', 1)
                data[section][key] = raw_value[1:closing] if closing > 0 else ""
    return data


def render_config(data: dict) -> str:
    text = TEMPLATE
    provenance = data.get("provenance", {})
    for section, key, _kind, _question, _redact in FIELDS:
        value = str(data.get(section, {}).get(key, "") or "")
        text = text.replace(f"@{section}.{key}@", '"' + value.replace('"', "") + '"')
        stamp = "user" if value and provenance.get(key) == "user" else ""
        text = text.replace(f"@prov.{key}@", f'"{stamp}"')
    return text


def load(repo: str) -> tuple[Path, dict]:
    path = config_path(repo)
    if not path.parent.is_dir():
        print(f"ERROR: repo root not found: {path.parent}", file=sys.stderr)
        raise SystemExit(2)
    if not path.is_file():
        path.write_text(render_config({}), encoding="utf-8")
        ensure_gitignored(path)
        print(f"Created {path} from template.")
    return path, parse_config(path.read_text(encoding="utf-8"))


def ensure_gitignored(path: Path) -> None:
    gitignore = path.parent / ".gitignore"
    existing = gitignore.read_text(encoding="utf-8") if gitignore.is_file() else ""
    if CONFIG_NAME not in existing.split():
        with gitignore.open("a", encoding="utf-8") as handle:
            if existing and not existing.endswith("\n"):
                handle.write("\n")
            handle.write(CONFIG_NAME + "\n")
        print(f"Added {CONFIG_NAME} to {gitignore}.")


def valid_url(value: str) -> bool:
    return bool(re.match(r"^https?://[^\s/]+", value))


def host_kind(value: str) -> str:
    return "local" if re.match(r"^https?://(localhost|127\.|0\.0\.0\.0)", value) else "deployed"


def missing_fields(data: dict) -> list[tuple[str, str, str]]:
    missing = []
    provenance = data.get("provenance", {})
    for section, key, kind, question, redact in FIELDS:
        value = data.get(section, {}).get(key, "")
        if not isinstance(value, str) or not value.strip():
            missing.append((section, key, question))
        elif kind == "url" and not valid_url(value):
            missing.append((section, key,
                            f"The recorded value for {section}.{key} is not a valid http(s) URL. {question}"))
        elif provenance.get(key) != "user":
            shown = "<a recorded key>" if redact else repr(value.strip())
            missing.append((section, key,
                            f"The config records {shown} for {section}.{key}, but it was never confirmed by the "
                            f"user (leftover from an older file or session). {question} "
                            "Record the confirmed value with `set` even if it is identical."))
    return missing


def token_env_status() -> dict:
    return {name: bool(os.environ.get(name)) for name in (LEGACY_TOKEN_ENV, CORE_TOKEN_ENV)}


def masked(value: str) -> str:
    value = value.strip()
    if len(value) <= 10:
        return value
    return f"{value[:4]}…{value[-4:]}"


def cmd_check(args: argparse.Namespace) -> int:
    path, data = load(args.repo)
    missing = missing_fields(data)
    if missing:
        print(f"ENVIRONMENT NOT READY — {len(missing)} value(s) need the user.")
        print("Ask the user each question below VERBATIM, then record each answer with:")
        print(f"  python3 {sys.argv[0]} set <section.key> \"<answer>\" --repo {args.repo}")
        print("Do not substitute discovered, remembered, or assumed values for any of them.")
        for section, key, question in missing:
            print(f"\nMISSING {section}.{key}\n  ASK: {question}")
        return 1

    print(f"ENVIRONMENT READY ({path})")
    for section, key, _kind, _question, redact in FIELDS:
        value = data.get(section, {}).get(key, "")
        shown = masked(str(value)) if redact else value
        suffix = f"  [{host_kind(str(value))}]" if section == "hosts" else ""
        print(f"  {section}.{key} = {shown}{suffix}")
    print("Fixed policy (not configurable):")
    print(f"  request timeout {REQUEST_TIMEOUT_MS} ms; inter-request delay {DELAY_BETWEEN_REQUESTS_MS} ms; "
          f"artifacts under {ARTIFACTS_DIR}/")
    for name, present in token_env_status().items():
        state = "set" if present else "UNSET — export it before oracle calls that need auth"
        print(f"  oracle token ${name}: {state}")
    return 0


def cmd_set(args: argparse.Namespace) -> int:
    path, data = load(args.repo)
    known = {(s, k): kind for s, k, kind, _q, _r in FIELDS}
    match = re.fullmatch(r"([a-z_]+)\.([a-z_]+)", args.key)
    if not match or (match.group(1), match.group(2)) not in known:
        print(f"ERROR: unknown key {args.key!r}; valid keys: "
              + ", ".join(f"{s}.{k}" for s, k, *_ in FIELDS), file=sys.stderr)
        return 2
    section, key = match.group(1), match.group(2)
    value = args.value.strip()
    if known[(section, key)] == "url" and not valid_url(value):
        print(f"ERROR: {args.key} must be a full http(s):// base URL, got {value!r}", file=sys.stderr)
        return 2
    data.setdefault(section, {})[key] = value
    data.setdefault("provenance", {})[key] = "user"
    path.write_text(render_config(data), encoding="utf-8")
    shown = masked(value) if (section, key) == ("auth", "external_api_key") else value
    print(f"Recorded {section}.{key} = {shown}")
    return 0


def http_reachable(url: str, timeout: float) -> tuple[bool, str]:
    request = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": "test-external-api-port/preflight"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return True, f"HTTP {response.status}"
    except urllib.error.HTTPError as error:
        return True, f"HTTP {error.code}"  # server answered; any status proves reachability
    except (urllib.error.URLError, OSError) as error:
        return False, str(getattr(error, "reason", error))


def cmd_preflight(args: argparse.Namespace) -> int:
    _path, data = load(args.repo)
    if missing_fields(data):
        print("PREFLIGHT FAILED: environment is not READY. Run `check` and ask the user for the missing values.")
        return 1

    failures: list[str] = []
    packet = Path(args.packet).expanduser().resolve()
    packet_text = packet.read_text(encoding="utf-8") if packet.is_file() else ""
    if not packet_text:
        failures.append(f"packet not found: {packet}")
    status_match = re.search(r"^Status:\s*([A-Z_]+)\s*$", packet_text, re.MULTILINE)
    status = status_match.group(1) if status_match else "MISSING"
    if status not in LEGAL_PACKET_STATUSES:
        failures.append(f"packet status {status!r} is not a legal status "
                        f"({', '.join(sorted(LEGAL_PACKET_STATUSES))}); a previous run corrupted it — "
                        "report this, do not invent statuses")
    elif status != "IMPLEMENTED":
        failures.append(f"packet status is {status}; testing requires IMPLEMENTED")
    wire = re.search(r"\b(GET|POST|PUT|PATCH|DELETE)\s+(/\S+)", packet_text)
    if not wire:
        failures.append("packet has no METHOD /wire/path in its Contract Proposal")

    timeout = REQUEST_TIMEOUT_MS / 1000.0
    reachability = {}
    for key in ("external_api", "legacy_api", "core_api"):
        url = data["hosts"][key]
        ok, detail = http_reachable(url, timeout)
        reachability[key] = {"url": url, "kind": host_kind(url), "reachable": ok, "detail": detail}
        if not ok:
            failures.append(f"{key} at {url} is not reachable ({detail}); ask the user, do not guess another URL")

    if failures:
        print("PREFLIGHT FAILED:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    tokens = token_env_status()
    manifest = {
        "provenance": "all values below come from .external-api-testing.toml; none were inferred",
        "packet": str(packet),
        "packet_status": status,
        "wire_operation": f"{wire.group(1)} {wire.group(2)}",
        "hosts": reachability,
        "custom_host": data["auth"]["external_custom_host"],
        "oracle_tokens": {name: ("set" if present else "unset") for name, present in tokens.items()},
        "fixed_policy": {"request_timeout_ms": REQUEST_TIMEOUT_MS,
                         "delay_between_requests_ms": DELAY_BETWEEN_REQUESTS_MS,
                         "artifacts_dir": ARTIFACTS_DIR},
    }
    print(f"TARGET: tenant {data['auth']['external_custom_host']} via {data['hosts']['external_api']} — "
          "the user must have reviewed and approved the READY table before this point.")
    print("PREFLIGHT PASSED — manifest seed (save into the run's manifest.json):")
    print(json.dumps(manifest, indent=2))
    for name, present in tokens.items():
        if not present:
            print(f"NOTE: ${name} is unset; oracle calls that need auth will fail until it is exported.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo", default=".", help="target repository root holding the config")
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", parents=[common],
                          help="report READY or the exact questions to ask the user").set_defaults(handler=cmd_check)
    set_parser = subparsers.add_parser("set", parents=[common], help="record one user-confirmed value")
    set_parser.add_argument("key", help="section.key, e.g. hosts.legacy_api")
    set_parser.add_argument("value")
    set_parser.set_defaults(handler=cmd_set)
    preflight_parser = subparsers.add_parser("preflight", parents=[common],
                                             help="verify readiness, packet status, and host reachability")
    preflight_parser.add_argument("--packet", required=True)
    preflight_parser.set_defaults(handler=cmd_preflight)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
