#!/usr/bin/env python3
"""Consolidate a test run's per-case folders into one JSON file per case.

Old layout (one folder, 5-8 files per case):
    T-014-duplicate-slug-conflict/
      case.json request.json response.json legacy/request.json
      legacy/response.json db.json side-effects.json verdict.json

New layout (one file per case, same content as top-level blocks):
    T-014-duplicate-slug-conflict.json
      { "case": ..., "request": ..., "response": ...,
        "legacy": {"request": ..., "response": ...},
        "db": ..., "side_effects": ..., "verdict": ... }

Absent blocks mean "not applicable", exactly like absent files did.

Safety: each case is consolidated only after the written file is re-read and
deep-compared block-by-block against the source files; only then is the
folder removed. A folder containing an unrecognized file is left untouched
and reported — nothing unknown is ever deleted. Idempotent.

Usage:
    python3 consolidate_run.py <run-dir>
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

KNOWN = {
    "case.json": ("case",),
    "request.json": ("request",),
    "response.json": ("response",),
    "legacy/request.json": ("legacy", "request"),
    "legacy/response.json": ("legacy", "response"),
    "db.json": ("db",),
    "side-effects.json": ("side_effects",),
    "verdict.json": ("verdict",),
}


def consolidate_case(folder: Path):
    """Return (blocks, problem). blocks is None when the folder must be kept."""
    present = [
        p for p in folder.rglob("*") if p.is_file() and p.name != ".DS_Store"
    ]
    known_paths = {folder / rel for rel in KNOWN}
    unknown = [p for p in present if p not in known_paths]
    if unknown:
        return None, f"unrecognized files, folder kept: {[str(p.relative_to(folder)) for p in unknown]}"

    blocks: dict = {}
    for rel, keys in KNOWN.items():
        path = folder / rel
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            return None, f"{rel} failed to parse ({exc}), folder kept"
        target = blocks
        for key in keys[:-1]:
            target = target.setdefault(key, {})
        target[keys[-1]] = data
    if not blocks:
        return None, "no artifact files found, folder kept"
    return blocks, None


def verify(out_file: Path, blocks: dict) -> bool:
    try:
        return json.loads(out_file.read_text(encoding="utf-8")) == blocks
    except Exception:
        return False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", help="path to <...>/test-runs/<run-id>/")
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir).resolve()
    if not run_dir.is_dir():
        print(f"ERROR: not a directory: {run_dir}", file=sys.stderr)
        return 2

    folders = sorted(
        p for p in run_dir.iterdir() if p.is_dir() and re.match(r"^T-\d{3}", p.name)
    )
    done = kept = 0
    for folder in folders:
        blocks, problem = consolidate_case(folder)
        if problem:
            print(f"KEPT   {folder.name}: {problem}")
            kept += 1
            continue
        out_file = run_dir / f"{folder.name}.json"
        out_file.write_text(
            json.dumps(blocks, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        if not verify(out_file, blocks):
            out_file.unlink(missing_ok=True)
            print(f"KEPT   {folder.name}: verification failed, folder kept")
            kept += 1
            continue
        shutil.rmtree(folder)
        done += 1
    already = len(list(run_dir.glob("T-*.json"))) - done
    print(
        f"consolidated {done} case folder(s), kept {kept}, "
        f"{max(already, 0)} already file-form, run: {run_dir.name}"
    )
    return 0 if kept == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
