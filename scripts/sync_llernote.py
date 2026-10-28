#!/usr/bin/env python3
"""Sync the tierlist data from the LLerNote upstream repository.

Usage:
    python scripts/sync_llernote.py --update-lock   # fetch main, update data + lock
    python scripts/sync_llernote.py                  # fetch the locked commit, update data
    python scripts/sync_llernote.py --check          # verify data, exit 1 on drift
    python scripts/sync_llernote.py --snapshot DIR --check

The command only changes data files when the lock/ref resolves to a newer
snapshot. Existing manual values are preserved when LLerNote has no value;
explicit corrections belong in scripts/llernote_overrides.json.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from llernote_common import (
    DEFAULT_LOCK,
    DEFAULT_OVERRIDES,
    DEFAULT_REF,
    DEFAULT_REPO,
    ROOT,
    DataError,
    fetch_snapshot,
    format_plan,
    load_lock,
    load_overrides,
    load_project,
    load_snapshot,
    load_snapshot_dir,
    make_lock,
    plan_project,
    project_matches_plan,
    resolve_ref,
    verify_lock,
    write_json,
    write_project,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Project root (defaults to the repository root)",
    )
    parser.add_argument(
        "--repo",
        default=DEFAULT_REPO,
        help=f"Upstream repository URL (default: {DEFAULT_REPO})",
    )
    parser.add_argument(
        "--ref",
        default=None,
        help=f"Branch, tag, or commit to fetch (default: locked commit, else {DEFAULT_REF})",
    )
    parser.add_argument(
        "--commit",
        default=None,
        help="Explicit 40-character commit SHA (mainly for --snapshot)",
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=None,
        help="Read the five LLerNote JSON files from this local directory",
    )
    parser.add_argument(
        "--lock",
        type=Path,
        default=DEFAULT_LOCK,
        help=f"Lock file path (default: {DEFAULT_LOCK})",
    )
    parser.add_argument(
        "--overrides",
        type=Path,
        default=DEFAULT_OVERRIDES,
        help=f"Local override file (default: {DEFAULT_OVERRIDES})",
    )
    parser.add_argument(
        "--update-lock",
        action="store_true",
        help="Resolve the requested ref, update data and write a new lock file",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write; exit 1 if the project differs from the snapshot",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print the final status line",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=80,
        help="Maximum detailed change lines to print (default: 80)",
    )
    return parser.parse_args(argv)


def choose_source(args: argparse.Namespace) -> tuple[dict[str, bytes], str]:
    lock = load_lock(args.lock)

    if args.snapshot:
        files = load_snapshot_dir(args.snapshot)
        commit = args.commit or (lock or {}).get("commit")
        if not commit:
            raise DataError("--snapshot requires --commit or an existing lock file")
        return files, commit

    if args.ref:
        commit = resolve_ref(args.ref, args.repo)
    elif args.commit:
        commit = args.commit.lower()
    elif lock:
        commit = str(lock["commit"])
    else:
        commit = resolve_ref(DEFAULT_REF, args.repo)

    return fetch_snapshot(args.repo, commit), commit


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root: Path = args.root.resolve()

    try:
        songs, metadata = load_project(root)
        files, commit = choose_source(args)
        snapshot = load_snapshot(files, commit)
        lock = load_lock(args.lock)

        if lock and not args.update_lock:
            lock_errors = verify_lock(snapshot, lock)
            if lock_errors:
                print("Lock verification failed:", file=sys.stderr)
                for error in lock_errors:
                    print(f"  - {error}", file=sys.stderr)
                print(
                    "Refusing to mix a stale lock with a different snapshot. "
                    "Use --update-lock to accept the new snapshot.",
                    file=sys.stderr,
                )
                return 2

        overrides = load_overrides(args.overrides)
        plan = plan_project(songs, metadata, snapshot, overrides)
        matches = project_matches_plan(songs, metadata, plan)

        if args.check:
            if matches:
                print(
                    f"OK: {len(songs)} songs match LLerNote {commit[:12]} "
                    f"({len(plan.upstream_only)} new, {len(plan.local_only)} local-only)"
                )
                return 0
            print(
                f"DRIFT: local data differs from LLerNote {commit[:12]}",
                file=sys.stderr,
            )
            print(format_plan(plan, limit=args.limit), file=sys.stderr)
            return 1

        if matches:
            print(f"Already up to date with LLerNote {commit[:12]}.")
        else:
            write_project(plan.songs, plan.metadata, root)
            if not args.quiet:
                print(format_plan(plan, limit=args.limit))
            print(
                f"Synced LLerNote {commit[:12]}: "
                f"{len(plan.new_ids)} new, {len(plan.changed_ids)} changed, "
                f"{len(plan.metadata)} total songs."
            )

        if args.update_lock:
            lock_path = args.lock if args.lock.is_absolute() else root / args.lock
            write_json(lock_path, make_lock(args.repo, commit, snapshot.hashes))
            print(f"Wrote {lock_path.relative_to(root) if lock_path.is_relative_to(root) else lock_path}")
        elif not lock:
            print(
                "WARNING: no lock file written. Run again with --update-lock to pin this snapshot.",
                file=sys.stderr,
            )
        return 0
    except DataError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
