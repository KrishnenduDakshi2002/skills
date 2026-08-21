#!/usr/bin/env python3
"""Create and validate durable external-API port packets."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_STATUSES = {
    "DISCOVERY",
    "BLOCKED",
    "READY",
    "IMPLEMENTING",
    "IMPLEMENTED",
    "VERIFIED",
}

REQUIRED_HEADINGS = (
    "Scope",
    "GitHub Issue Intake",
    "Source Authorities",
    "Consumer and Existing Conventions",
    "Repository Pattern Conformity",
    "Behavior Ledger",
    "Frontend Rule Classification",
    "Validation Matrix",
    "Contract Design Grill",
    "Contract Proposal",
    "Field Exposure Ledger",
    "Threat and Abuse Cases",
    "Mapping and Implementation Plan",
    "Shared Architecture Plan",
    "Core Migration Readiness",
    "Consumer Examples",
    "Decisions and Questions",
    "Implementation Traceability",
    "Implementation Checks",
    "Handoff",
)

REQUIRED_GRILL_IDS = {f"G-{index:03d}" for index in range(1, 9)}
REQUIRED_PATTERN_IDS = {f"P-{index:03d}" for index in range(1, 11)}
GITHUB_ISSUE_PATTERN = re.compile(
    r"https://github\.com/[^/\s]+/[^/\s]+/issues/[1-9]\d*(?:[/?#].*)?"
)

STAGE_STATUSES = {
    "design": {"READY", "IMPLEMENTING", "IMPLEMENTED"},
    "implementation": {"IMPLEMENTED"},
    "testing": {"VERIFIED"},
}

CORE_MIGRATION_STAGE_STATUSES = {
    "design": {"DESIGNED", "IMPLEMENTED"},
    "implementation": {"IMPLEMENTED"},
    "testing": {"IMPLEMENTED"},
}

PLACEHOLDER_PATTERNS = (
    re.compile(r"\{\{[^}]+\}\}"),
    re.compile(r"<!--\s*Replace", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
)


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def section(content: str, heading: str) -> str:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(content)
    return match.group(1) if match else ""


def table_ids(section_content: str, prefix: str) -> list[str]:
    return re.findall(rf"^\|\s*({re.escape(prefix)}-\d{{3}})\s*\|", section_content, re.MULTILINE)


def add_duplicate_errors(errors: list[str], identifiers: list[str], label: str) -> None:
    duplicates = sorted({identifier for identifier in identifiers if identifiers.count(identifier) > 1})
    if duplicates:
        errors.append(f"duplicate {label} IDs: {', '.join(duplicates)}")


def table_last_cell_statuses(section_content: str, prefix: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    identifier_pattern = re.compile(rf"{re.escape(prefix)}-\d{{3}}")
    for line in section_content.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and identifier_pattern.fullmatch(cells[0]):
            statuses[cells[0]] = cells[-1].upper()
    return statuses


def initialize_packet(args: argparse.Namespace) -> int:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.operation):
        print("ERROR: --operation must be a lowercase kebab-case slug", file=sys.stderr)
        return 1

    issue = args.issue.strip()
    if not GITHUB_ISSUE_PATTERN.fullmatch(issue):
        print("ERROR: --issue must be a full github.com issue URL", file=sys.stderr)
        return 1

    output = Path(args.output).expanduser().resolve()
    if output.exists():
        print(f"ERROR: refusing to overwrite existing packet: {output}", file=sys.stderr)
        return 1

    template = (skill_root() / "assets" / "port-packet.md").read_text(encoding="utf-8")
    rendered = (
        template.replace("{{OPERATION}}", args.operation)
        .replace("{{SOURCE_KIND}}", args.source)
        .replace("{{ISSUE_URL}}", issue)
        .replace("{{GENERATED_AT}}", datetime.now(timezone.utc).isoformat())
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"Created port packet: {output}")
    return 0


def validate_packet(args: argparse.Namespace) -> int:
    packet = Path(args.packet).expanduser().resolve()
    if not packet.is_file():
        print(f"ERROR: packet not found: {packet}", file=sys.stderr)
        return 1

    content = packet.read_text(encoding="utf-8")
    errors: list[str] = []

    missing_headings = [
        heading for heading in REQUIRED_HEADINGS if not re.search(rf"^## {re.escape(heading)}\s*$", content, re.MULTILINE)
    ]
    if missing_headings:
        errors.append(f"missing headings: {', '.join(missing_headings)}")

    status_match = re.search(r"^Status:\s*([A-Z]+)\s*$", content, re.MULTILINE)
    status = status_match.group(1) if status_match else None
    if status is None:
        errors.append("missing top-level Status field")
    elif status not in ALLOWED_STATUSES:
        errors.append(f"invalid status {status}; expected one of {', '.join(sorted(ALLOWED_STATUSES))}")
    elif status not in STAGE_STATUSES[args.stage]:
        errors.append(
            f"status {status} has not reached the {args.stage} gate; expected one of "
            f"{', '.join(sorted(STAGE_STATUSES[args.stage]))}"
        )

    for placeholder_pattern in PLACEHOLDER_PATTERNS:
        if placeholder_pattern.search(content):
            errors.append(f"unresolved template marker matching {placeholder_pattern.pattern!r}")

    issue_match = re.search(r"^GitHub issue:\s*(\S+)\s*$", content, re.MULTILINE)
    if issue_match is None or not GITHUB_ISSUE_PATTERN.fullmatch(issue_match.group(1)):
        errors.append("missing or invalid top-level GitHub issue URL")

    source_section = section(content, "Source Authorities")
    if not re.search(r"[A-Za-z0-9_.\-/]+@[0-9a-f]{7,40}:[^|\n]+:\d+", content):
        errors.append("no pinned evidence anchor found; use repository@commit:path:line")
    if not re.search(r"\|\s*[0-9a-f]{7,40}\s*\|", source_section):
        errors.append("Source Authorities must include at least one commit SHA in the Pin column")

    issue_ids = table_ids(section(content, "GitHub Issue Intake"), "I")
    behavior_ids = table_ids(section(content, "Behavior Ledger"), "B")
    validation_ids = table_ids(section(content, "Validation Matrix"), "V")
    grill_ids = table_ids(section(content, "Contract Design Grill"), "G")
    pattern_ids = table_ids(section(content, "Repository Pattern Conformity"), "P")
    exposure_ids = table_ids(section(content, "Field Exposure Ledger"), "X")
    threat_ids = table_ids(section(content, "Threat and Abuse Cases"), "S")
    migration_section = section(content, "Core Migration Readiness")
    migration_ids = table_ids(migration_section, "M")
    handoff_ids = table_ids(section(content, "Implementation Traceability"), "H")

    for identifiers, label in (
        (issue_ids, "issue requirement"),
        (behavior_ids, "behavior"),
        (validation_ids, "validation"),
        (grill_ids, "contract grill"),
        (pattern_ids, "pattern conformity"),
        (exposure_ids, "exposure"),
        (threat_ids, "threat"),
        (migration_ids, "core migration"),
        (handoff_ids, "implementation handoff"),
    ):
        if not identifiers:
            errors.append(f"no {label} IDs found")
        add_duplicate_errors(errors, identifiers, label)

    missing_grill_ids = sorted(REQUIRED_GRILL_IDS.difference(grill_ids))
    if missing_grill_ids:
        errors.append(f"missing required contract grill IDs: {', '.join(missing_grill_ids)}")

    missing_pattern_ids = sorted(REQUIRED_PATTERN_IDS.difference(pattern_ids))
    if missing_pattern_ids:
        errors.append(f"missing required pattern conformity IDs: {', '.join(missing_pattern_ids)}")

    pattern_statuses = table_last_cell_statuses(section(content, "Repository Pattern Conformity"), "P")
    for pattern_id in pattern_ids:
        pattern_status = pattern_statuses.get(pattern_id, "")
        if pattern_status != "ADOPTED" and not pattern_status.startswith("DEVIATION"):
            errors.append(
                f"{pattern_id} pattern decision {pattern_status or 'MISSING'} is unresolved; "
                "expected ADOPTED or DEVIATION (D-###)"
            )

    grill_section = section(content, "Contract Design Grill")
    if re.search(
        r"^\|\s*G-\d{3}\s*\|[^\n]*\b(OPEN|PENDING|UNRESOLVED)\b[^\n]*$",
        grill_section,
        re.MULTILINE | re.IGNORECASE,
    ):
        errors.append("contract grill decisions remain open")

    architecture_section = section(content, "Shared Architecture Plan")
    if "libs/services" not in architecture_section or "libs/repository" not in architecture_section:
        errors.append("Shared Architecture Plan must place logic in libs/services and libs/repository")
    if not re.search(r"\bcore\b", architecture_section, re.IGNORECASE) or not re.search(
        r"\bexternal\b", architecture_section, re.IGNORECASE
    ):
        errors.append("Shared Architecture Plan must identify both core and external consumers")

    migration_status_match = re.search(
        r"^Core migration readiness:\s*([A-Z_]+)\s*$",
        migration_section,
        re.MULTILINE,
    )
    migration_status = migration_status_match.group(1) if migration_status_match else None
    allowed_migration_statuses = CORE_MIGRATION_STAGE_STATUSES[args.stage]
    if migration_status is None:
        errors.append("Core Migration Readiness must declare Core migration readiness")
    elif migration_status not in allowed_migration_statuses:
        errors.append(
            f"core migration readiness {migration_status} has not reached the {args.stage} gate; expected one of "
            f"{', '.join(sorted(allowed_migration_statuses))}"
        )

    migration_row_statuses = table_last_cell_statuses(migration_section, "M")
    for migration_id in migration_ids:
        row_status = migration_row_statuses.get(migration_id)
        if row_status not in allowed_migration_statuses:
            errors.append(
                f"{migration_id} core migration status {row_status or 'MISSING'} has not reached the "
                f"{args.stage} gate; expected one of {', '.join(sorted(allowed_migration_statuses))}"
            )

    replacement_delta_match = re.search(
        r"^Core replacement implementation delta:\s*([A-Z_]+)\s*$",
        migration_section,
        re.MULTILINE,
    )
    replacement_delta = replacement_delta_match.group(1) if replacement_delta_match else None
    if replacement_delta != "TRANSPORT_ONLY":
        errors.append("Core replacement implementation delta must be TRANSPORT_ONLY")

    reimplementation_match = re.search(
        r"^Future core business/repository reimplementation required:\s*([A-Z]+)\s*$",
        migration_section,
        re.MULTILINE,
    )
    reimplementation_required = reimplementation_match.group(1) if reimplementation_match else None
    if reimplementation_required != "NO":
        errors.append("Future core business/repository reimplementation required must be NO")

    for required_term in ("legacy", "shared", "external", "core"):
        if not re.search(rf"\b{required_term}\b", migration_section, re.IGNORECASE):
            errors.append(f"Core Migration Readiness must explicitly map {required_term}")

    for rule_id in behavior_ids + validation_ids:
        if rule_id not in migration_section:
            errors.append(f"{rule_id} is not mapped in Core Migration Readiness")

    contract_section = section(content, "Contract Proposal")
    if not re.search(r"\b(GET|POST|PUT|PATCH|DELETE)\s+/\S+", contract_section):
        errors.append("Contract Proposal must contain the complete METHOD /wire/path")

    decision_section = section(content, "Decisions and Questions")
    if re.search(r"^\|\s*D-\d{3}\s*\|\s*(OPEN|PENDING|UNRESOLVED)\b", decision_section, re.MULTILINE | re.IGNORECASE):
        errors.append("material decisions remain open")

    handoff_section = section(content, "Implementation Traceability")
    for rule_id in behavior_ids + validation_ids + grill_ids + pattern_ids + migration_ids + threat_ids:
        if rule_id not in handoff_section:
            errors.append(f"{rule_id} is not mapped in Implementation Traceability")

    if args.stage == "implementation":
        checks_section = section(content, "Implementation Checks")
        if re.search(r"^\|[^\n]*\|\s*(FAIL|BLOCKED)\s*\|", checks_section, re.MULTILINE):
            errors.append("implementation checks still contain FAIL or BLOCKED outcomes")

        naming_check_match = re.search(
            r"^\|\s*New-file naming audit\s*\|[^|\n]*\|\s*([^|\n]+?)\s*\|",
            checks_section,
            re.MULTILINE | re.IGNORECASE,
        )
        if naming_check_match is None:
            errors.append("Implementation Checks must include New-file naming audit")
        elif naming_check_match.group(1).strip().upper() != "PASS":
            errors.append("New-file naming audit must have a PASS outcome")

        handoff_section = section(content, "Handoff")
        if not re.search(
            r"^Testing status:\s*DEFERRED TO SEPARATE WORKFLOW\s*$",
            handoff_section,
            re.MULTILINE,
        ):
            errors.append("Testing status must be DEFERRED TO SEPARATE WORKFLOW")
        if not re.search(
            r"^Test files added or modified by this port:\s*None\s*$",
            handoff_section,
            re.MULTILINE,
        ):
            errors.append("Test files added or modified by this port must be None")

    if args.stage == "testing":
        test_section = section(content, "Test Traceability")
        if not test_section:
            errors.append("missing Test Traceability section; the testing workflow appends it")
        test_ids = table_ids(test_section, "T")
        if not test_ids:
            errors.append("no test case IDs found in Test Traceability")
        add_duplicate_errors(errors, test_ids, "test case")

        error_ids = table_ids(contract_section, "E")
        for rule_id in behavior_ids + validation_ids + threat_ids + error_ids:
            if rule_id not in test_section:
                errors.append(f"{rule_id} is not covered in Test Traceability")

        test_statuses = table_last_cell_statuses(test_section, "T")
        for test_id in test_ids:
            row_status = test_statuses.get(test_id)
            if row_status not in {"PASS", "EXCLUDED"}:
                errors.append(
                    f"{test_id} verdict {row_status or 'MISSING'} blocks the testing gate; "
                    "expected PASS or EXCLUDED"
                )

        if not re.search(r"^Test run:\s*\S+", test_section, re.MULTILINE):
            errors.append("Test Traceability must pin the Test run artifact directory")

        if not re.search(
            r"^Testing status:\s*VERIFIED\s*$",
            section(content, "Handoff"),
            re.MULTILINE,
        ):
            errors.append("Testing status must be VERIFIED at the testing gate")

    if errors:
        print(f"Port packet FAILED {args.stage} validation: {packet}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Port packet PASSED {args.stage} validation: {packet}")
    print(
        f"status={status} issue_requirements={len(issue_ids)} behaviors={len(behavior_ids)} "
        f"validations={len(validation_ids)} grill_decisions={len(grill_ids)} patterns={len(pattern_ids)} "
        f"migrations={len(migration_ids)} exposures={len(exposure_ids)} "
        f"threats={len(threat_ids)} handoffs={len(handoff_ids)}"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create a port packet from the bundled template")
    init_parser.add_argument("--operation", required=True)
    init_parser.add_argument("--source", required=True, choices=("legacy", "core-api", "both"))
    init_parser.add_argument("--issue", required=True)
    init_parser.add_argument("--output", required=True)
    init_parser.set_defaults(handler=initialize_packet)

    check_parser = subparsers.add_parser("check", help="validate a completed port packet gate")
    check_parser.add_argument("packet")
    check_parser.add_argument("--stage", required=True, choices=("design", "implementation", "testing"))
    check_parser.set_defaults(handler=validate_packet)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
