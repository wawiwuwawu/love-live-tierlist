#!/usr/bin/env python3
"""Validate the project's song data before/after a LLerNote sync.

Usage:
    python scripts/verify_data.py
    python scripts/verify_data.py --snapshot path/to/llernote-data --commit <sha>
    python scripts/verify_data.py --strict

The default checks are structural and do not need the network. Passing
--snapshot also checks that every LLerNote id and owned field matches the
snapshot. Warnings (for example legacy songs without album art) do not fail
the command unless --strict is used.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from llernote_common import (
    DATA_FILES,
    DEFAULT_LOCK,
    DEFAULT_OVERRIDES,
    DEFAULT_REPO,
    ROOT,
    SERIES_ENGLISH_FALLBACK,
    DataError,
    cover_file_for,
    format_plan,
    is_remote_url,
    load_lock,
    load_overrides,
    load_project,
    load_snapshot,
    load_snapshot_dir,
    plan_project,
    project_matches_plan,
)

REQUIRED_METADATA = (
    "song",
    "artist",
    "jp_title",
    "phonetic",
    "series",
    "llernote_id",
    "llernote_artists",
)
VALID_SERIES = set(SERIES_ENGLISH_FALLBACK.values())
SOURCE_VALUES = {"itunes", "llernote", "mb"}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Project root")
    parser.add_argument("--snapshot", type=Path, default=None, help="LLerNote data directory")
    parser.add_argument("--commit", default=None, help="Commit SHA for --snapshot")
    parser.add_argument(
        "--lock",
        type=Path,
        default=DEFAULT_LOCK,
        help=f"Lock file (default: {DEFAULT_LOCK})",
    )
    parser.add_argument(
        "--overrides",
        type=Path,
        default=DEFAULT_OVERRIDES,
        help=f"Override file (default: {DEFAULT_OVERRIDES})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    return parser.parse_args(argv)


def _parse_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _validate_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def check_local(
    root: Path,
    songs: list[dict],
    metadata: dict[str, dict],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    root_songs = root / "songs.json"
    docs_songs = root / "docs" / "songs.json"
    root_metadata = root / "metadata.json"
    docs_metadata = root / "docs" / "metadata.json"
    for path in (root_songs, docs_songs, root_metadata, docs_metadata):
        if not path.is_file():
            errors.append(f"Missing data file: {path}")

    if docs_songs.is_file():
        try:
            import json

            docs_data = json.loads(docs_songs.read_text(encoding="utf-8"))
            if docs_data != songs:
                errors.append("songs.json differs from docs/songs.json")
        except Exception as exc:
            errors.append(f"Could not compare docs/songs.json: {exc}")
    if docs_metadata.is_file():
        try:
            import json

            docs_data = json.loads(docs_metadata.read_text(encoding="utf-8"))
            if docs_data != metadata:
                errors.append("metadata.json differs from docs/metadata.json")
        except Exception as exc:
            errors.append(f"Could not compare docs/metadata.json: {exc}")

    seen_ids: set[int] = set()
    seen_titles: set[str] = set()
    seen_lln: set[str] = set()
    song_by_id: dict[int, dict] = {}
    for index, song in enumerate(songs):
        label = f"songs[{index}]"
        if not isinstance(song, dict):
            errors.append(f"{label} is not an object")
            continue
        raw_id = song.get("id")
        if not isinstance(raw_id, int) or isinstance(raw_id, bool) or raw_id <= 0:
            errors.append(f"{label}.id must be a positive integer")
            continue
        song_id = raw_id
        if song_id in seen_ids:
            errors.append(f"Duplicate song id: {song_id}")
            continue
        seen_ids.add(song_id)
        song_by_id[song_id] = song
        title = str(song.get("title") or "").strip()
        if not title:
            errors.append(f"{label} ({song_id}) has an empty title")
        elif title in seen_titles:
            warnings.append(f"Duplicate song title: {title!r} (id {song_id})")
        else:
            seen_titles.add(title)
        for field in ("artist", "date", "center", "duration"):
            if field not in song:
                errors.append(f"Song {song_id} is missing field {field!r}")
            elif not isinstance(song[field], str):
                errors.append(f"Song {song_id}.{field} must be a string")
        song_date = str(song.get("date") or "").strip()
        if song_date and not _parse_iso_date(song_date):
            errors.append(f"Song {song_id} has invalid date {song_date!r}")
        if not str(song.get("artist") or "").strip():
            warnings.append(f"Song {song_id} has an empty artist")

    metadata_by_id: dict[int, dict] = {}
    for key, value in metadata.items():
        label = f"metadata[{key!r}]"
        if not isinstance(key, str) or not key.isdigit():
            errors.append(f"{label} key is not a numeric local id")
            continue
        local_id = int(key)
        if local_id in metadata_by_id:
            errors.append(f"Duplicate metadata key: {local_id}")
            continue
        metadata_by_id[local_id] = value
        if not isinstance(value, dict):
            errors.append(f"{label} is not an object")
            continue
        for field in REQUIRED_METADATA:
            if field not in value:
                errors.append(f"Metadata {local_id} is missing {field!r}")
        if local_id not in song_by_id:
            errors.append(f"Metadata {local_id} has no matching song")
        lln = str(value.get("llernote_id") or "").strip()
        if not lln:
            errors.append(f"Metadata {local_id} has an empty llernote_id")
        elif lln in seen_lln:
            errors.append(f"Duplicate llernote_id: {lln} (local {local_id})")
        else:
            seen_lln.add(lln)
        series = str(value.get("series") or "").strip()
        if series not in VALID_SERIES:
            errors.append(f"Metadata {local_id} has unknown series {series!r}")
        artists = value.get("llernote_artists")
        if not isinstance(artists, list) or not artists:
            errors.append(f"Metadata {local_id}.llernote_artists must be a non-empty list")
        elif not all(isinstance(item, str) and item.strip() for item in artists):
            errors.append(f"Metadata {local_id}.llernote_artists contains invalid values")

        source = str(value.get("source") or "").strip()
        if source not in SOURCE_VALUES:
            warnings.append(f"Metadata {local_id} has unexpected source {source!r}")

        song = song_by_id.get(local_id)
        if song:
            if str(value.get("song") or "") != str(song.get("title") or ""):
                errors.append(f"Metadata {local_id}.song does not match songs.title")
            if str(value.get("artist") or "") != str(song.get("artist") or ""):
                errors.append(f"Metadata {local_id}.artist does not match songs.artist")
            song_date = str(song.get("date") or "").strip()
            meta_date = str(value.get("released_on") or "").strip()
            if song_date != meta_date:
                errors.append(
                    f"Metadata {local_id}.released_on {meta_date!r} "
                    f"does not match songs.date {song_date!r}"
                )

        yt = str(value.get("yt") or "").strip()
        if yt and not _validate_url(yt):
            errors.append(f"Metadata {local_id}.yt is not a valid URL")
        wiki = str(value.get("wiki_audio") or "").strip()
        if wiki and not _validate_url(wiki):
            errors.append(f"Metadata {local_id}.wiki_audio is not a valid URL")
        art = str(value.get("art") or "").strip()
        if art and not is_remote_url(art):
            warnings.append(f"Metadata {local_id}.art is not a remote URL: {art!r}")

        cover = cover_file_for(value)
        if cover:
            cover_path = (root / "docs" / cover).resolve()
            docs_root = (root / "docs").resolve()
            if docs_root not in cover_path.parents and cover_path != docs_root:
                errors.append(f"Metadata {local_id} cover escapes docs/: {cover}")
            elif not cover_path.is_file():
                warnings.append(f"Metadata {local_id} cover is missing: {cover}")
        elif not str(value.get("cover") or "").strip():
            warnings.append(f"Metadata {local_id} has no album/cover source")

    missing_meta = sorted(seen_ids - set(metadata_by_id))
    extra_meta = sorted(set(metadata_by_id) - seen_ids)
    for local_id in missing_meta:
        errors.append(f"Song {local_id} has no metadata entry")
    for local_id in extra_meta:
        errors.append(f"Metadata {local_id} has no song entry")

    if len(songs) != len(metadata):
        errors.append(f"Song count {len(songs)} != metadata count {len(metadata)}")

    return errors, warnings


def check_snapshot(
    songs: list[dict],
    metadata: dict[str, dict],
    snapshot_dir: Path,
    commit: str,
    overrides: dict[str, dict],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        files = load_snapshot_dir(snapshot_dir)
        snapshot = load_snapshot(files, commit)
        plan = plan_project(songs, metadata, snapshot, overrides)
    except DataError as exc:
        return [str(exc)], warnings

    if not project_matches_plan(songs, metadata, plan):
        errors.append(
            f"Data differs from LLerNote snapshot {commit[:12]}"
        )
        warnings.append(format_plan(plan, limit=40))
    missing_local = snapshot.songs_by_id.keys() - {
        str(value.get("llernote_id") or "") for value in metadata.values()
    }
    if missing_local:
        errors.append(
            "Snapshot songs not present locally: " + ", ".join(sorted(missing_local, key=int))
        )
    if plan.local_only:
        errors.append(
            "Local LLerNote ids absent from snapshot: " + ", ".join(plan.local_only)
        )
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    # Keep Japanese series names readable on Windows consoles using legacy
    # code pages instead of crashing during the summary output.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    args = parse_args(argv)
    root: Path = args.root.resolve()
    try:
        songs, metadata = load_project(root)
        errors, warnings = check_local(root, songs, metadata)

        if args.snapshot:
            lock = load_lock(args.lock)
            commit = args.commit or (lock or {}).get("commit")
            if not commit:
                errors.append("--snapshot requires --commit or a lock file")
            else:
                if not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
                    errors.append(f"Invalid commit SHA: {commit!r}")
                else:
                    snap_errors, snap_warnings = check_snapshot(
                        songs,
                        metadata,
                        args.snapshot.resolve(),
                        commit.lower(),
                        load_overrides(args.overrides),
                    )
                    errors.extend(snap_errors)
                    warnings.extend(snap_warnings)
        elif args.commit:
            errors.append("--commit is only valid together with --snapshot")

        counts = Counter(str(value.get("series") or "") for value in metadata.values())
        print(f"Songs: {len(songs)}")
        print(f"Metadata: {len(metadata)}")
        print(f"LLerNote ids: {len({value.get('llernote_id') for value in metadata.values()})}")
        print("Series:")
        for name in sorted(counts):
            print(f"  {counts[name]:3d}  {name}")

        if warnings:
            print(f"Warnings: {len(warnings)}")
            for warning in warnings:
                print(f"  WARNING: {warning}")
        if errors:
            print(f"Errors: {len(errors)}", file=sys.stderr)
            for error in errors:
                print(f"  ERROR: {error}", file=sys.stderr)
            return 1
        if warnings and args.strict:
            print("Strict mode: warnings are treated as errors", file=sys.stderr)
            return 1
        print("OK: data is valid.")
        return 0
    except DataError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
