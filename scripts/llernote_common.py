"""Shared helpers for the LLerNote data pipeline.

The functions in this module are deliberately dependency-free and
deterministic: the same locked upstream snapshot plus the same local
overrides must produce byte-identical project data.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DEFAULT_LOCK = ROOT / "scripts" / "llernote.lock.json"
DEFAULT_OVERRIDES = ROOT / "scripts" / "llernote_overrides.json"
DEFAULT_REPO = "https://github.com/hamproductions/llernote.git"
DEFAULT_REF = "main"

DATA_FILES = (
    "song-info.json",
    "artists-info.json",
    "units.json",
    "series-info.json",
    "series.json",
)

# series.json upstream currently omits series 7. Keep the project's
# existing English names as a stable fallback.
SERIES_ENGLISH_FALLBACK = {
    "1": "Love Live! School idol project",
    "2": "Love Live! Sunshine!!",
    "3": "Nijigasaki High School Idol Club",
    "4": "Love Live! Superstar!!",
    "5": "School Idol Musical",
    "6": "Hasunosora Girls' High School Idol Club",
    "7": "幻日のヨハネ -SUNSHINE in the MIRROR-",
    "8": "Ikizulive! Love Live! BLUEBIRD",
}

# The frontend derives cover filenames from the series tab, not from the
# metadata "series" label. This table mirrors docs/app.js.
SERIES_FILE_TAG = {
    "Love Live! School idol project": "mus",
    "Love Live! Sunshine!!": "aqours",
    "Nijigasaki High School Idol Club": "niji",
    "Love Live! Superstar!!": "liella",
    "Hasunosora Girls' High School Idol Club": "hasunosora",
    "School Idol Musical": "lain",
    "幻日のヨハネ -SUNSHINE in the MIRROR-": "aqours",
    "Ikizulive! Love Live! BLUEBIRD": "lain",
}

_MISSING = object()


class DataError(RuntimeError):
    """Raised when project or upstream data cannot be processed safely."""


@dataclass
class Snapshot:
    commit: str
    songs: list[dict[str, Any]]
    songs_by_id: dict[str, dict[str, Any]]
    artists: dict[str, str]
    artist_english: dict[str, str]
    units: dict[str, str]
    unit_english: dict[str, str]
    series_names: dict[str, str]
    files: dict[str, bytes] = field(repr=False)
    hashes: dict[str, str] = field(default_factory=dict)


@dataclass
class SyncPlan:
    songs: list[dict[str, Any]]
    metadata: dict[str, dict[str, Any]]
    changed_ids: list[str] = field(default_factory=list)
    new_ids: list[int] = field(default_factory=list)
    upstream_only: list[str] = field(default_factory=list)
    local_only: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    changes: list[str] = field(default_factory=list)


def json_text(data: Any) -> str:
    """Serialize exactly like the existing project JSON (LF, no final newline)."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json_text(data)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def load_project(root: Path = ROOT) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    songs_path = root / "songs.json"
    metadata_path = root / "metadata.json"
    songs = load_json(songs_path)
    metadata = load_json(metadata_path)
    if not isinstance(songs, list):
        raise DataError(f"{songs_path} must contain a JSON list")
    if not isinstance(metadata, dict):
        raise DataError(f"{metadata_path} must contain a JSON object")
    return songs, metadata


def write_project(
    songs: list[dict[str, Any]],
    metadata: dict[str, dict[str, Any]],
    root: Path = ROOT,
) -> None:
    """Write the canonical data to the root copies and the Pages copies."""
    write_json(root / "songs.json", songs)
    write_json(root / "metadata.json", metadata)
    write_json(root / "docs" / "songs.json", songs)
    write_json(root / "docs" / "metadata.json", metadata)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_github_repo(repo: str) -> tuple[str, str]:
    match = re.search(r"github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?$", repo.strip())
    if not match:
        raise DataError(f"Not a GitHub repository URL: {repo}")
    return match.group(1), match.group(2)


def raw_data_url(repo: str, commit: str, filename: str) -> str:
    owner, name = parse_github_repo(repo)
    return f"https://raw.githubusercontent.com/{owner}/{name}/{commit}/data/{filename}"


def resolve_ref(ref: str, repo: str = DEFAULT_REPO) -> str:
    """Resolve a branch/tag/SHA to a full commit SHA without the GitHub API."""
    if re.fullmatch(r"[0-9a-fA-F]{40}", ref):
        return ref.lower()

    result = subprocess.run(
        ["git", "ls-remote", repo, ref],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise DataError(
            "Could not resolve upstream ref with git ls-remote:\n"
            + (result.stderr or result.stdout).strip()
        )

    candidates: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        sha, name = line.split("\t", 1)
        candidates[name] = sha
    for expected in (
        f"refs/heads/{ref}",
        f"refs/tags/{ref}",
        f"refs/tags/{ref}^{{}}",
    ):
        if expected in candidates:
            return candidates[expected].lower()
    if len(candidates) == 1:
        return next(iter(candidates.values())).lower()
    raise DataError(f"Could not resolve upstream ref: {ref}")


def fetch_snapshot(repo: str = DEFAULT_REPO, commit: str = "") -> dict[str, bytes]:
    if not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise DataError("A full 40-character commit SHA is required to fetch a snapshot")
    files: dict[str, bytes] = {}
    for filename in DATA_FILES:
        url = raw_data_url(repo, commit, filename)
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "love-live-tierlist-sync/1.0"},
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read()
        except Exception as exc:  # urllib raises several exception types
            raise DataError(f"Could not download {url}: {exc}") from exc
        if not payload:
            raise DataError(f"Empty upstream file: {url}")
        files[filename] = payload
    return files


def load_snapshot_dir(path: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for filename in DATA_FILES:
        file_path = path / filename
        if not file_path.is_file():
            raise DataError(f"Missing snapshot file: {file_path}")
        files[filename] = file_path.read_bytes()
    return files


def _decode_json_file(files: dict[str, bytes], filename: str) -> Any:
    try:
        return json.loads(files[filename].decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DataError(f"Invalid upstream JSON: {filename}: {exc}") from exc


def make_snapshot(files: dict[str, bytes], commit: str) -> Snapshot:
    songs = _decode_json_file(files, "song-info.json")
    artists = _decode_json_file(files, "artists-info.json")
    units = _decode_json_file(files, "units.json")
    series_info = _decode_json_file(files, "series-info.json")
    series_json = _decode_json_file(files, "series.json")

    if not isinstance(songs, list) or not isinstance(artists, list):
        raise DataError("LLerNote song-info/artists-info must be lists")
    if not isinstance(units, list) or not isinstance(series_info, list):
        raise DataError("LLerNote units/series-info must be lists")
    if not isinstance(series_json, dict):
        raise DataError("LLerNote series.json must be an object")

    songs_by_id: dict[str, dict[str, Any]] = {}
    for song in songs:
        if not isinstance(song, dict) or "id" not in song:
            raise DataError("LLerNote song entry is missing an id")
        sid = str(song["id"])
        if sid in songs_by_id:
            raise DataError(f"Duplicate LLerNote song id: {sid}")
        songs_by_id[sid] = song

    artist_names: dict[str, str] = {}
    artist_english: dict[str, str] = {}
    for artist in artists:
        aid = str(artist.get("id", ""))
        if not aid:
            continue
        artist_names[aid] = str(artist.get("name", "")).strip()
        if artist.get("englishName"):
            artist_english[aid] = str(artist["englishName"]).strip()

    unit_names: dict[str, str] = {}
    unit_english: dict[str, str] = {}
    for unit in units:
        uid = str(unit.get("id", ""))
        if not uid:
            continue
        unit_names[uid] = str(unit.get("name", "")).strip()
        if unit.get("englishName"):
            unit_english[uid] = str(unit["englishName"]).strip()

    series_names: dict[str, str] = {}
    for item in series_info:
        sid = str(item.get("id", ""))
        if not sid:
            continue
        japanese = str(item.get("name", "")).strip()
        series_names[sid] = (
            str(series_json.get(japanese, "")).strip()
            or SERIES_ENGLISH_FALLBACK.get(sid)
            or japanese
        )

    hashes = {name: sha256_bytes(payload) for name, payload in files.items()}
    return Snapshot(
        commit=commit,
        songs=songs,
        songs_by_id=songs_by_id,
        artists=artist_names,
        artist_english=artist_english,
        units=unit_names,
        unit_english=unit_english,
        series_names=series_names,
        files=files,
        hashes=hashes,
    )


def load_snapshot(files: dict[str, bytes], commit: str) -> Snapshot:
    return make_snapshot(files, commit)


def load_overrides(path: Path = DEFAULT_OVERRIDES) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        return {}
    data = load_json(path)
    if not isinstance(data, dict):
        raise DataError(f"{path} must contain a JSON object")
    for key, value in data.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            raise DataError(f"Invalid override for {key!r} in {path}")
    return data


def load_lock(path: Path = DEFAULT_LOCK) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    data = load_json(path)
    if not isinstance(data, dict):
        raise DataError(f"{path} must contain a JSON object")
    if not data.get("repo") or not data.get("commit"):
        raise DataError(f"{path} must contain repo and commit")
    return data


def make_lock(repo: str, commit: str, hashes: dict[str, str]) -> dict[str, Any]:
    return {
        "repo": repo,
        "commit": commit,
        "files": {name: hashes[name] for name in DATA_FILES if name in hashes},
    }


def verify_lock(snapshot: Snapshot, lock: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if lock.get("commit") != snapshot.commit:
        errors.append(
            f"Lock commit is {lock.get('commit')}, but snapshot is {snapshot.commit}"
        )
    files = lock.get("files", {})
    if not isinstance(files, dict):
        return errors + ["Lock file has no valid files map"]
    for name in DATA_FILES:
        expected = files.get(name)
        if not expected:
            errors.append(f"Lock is missing a hash for {name}")
        elif expected != snapshot.hashes.get(name):
            errors.append(f"Hash mismatch for {name}")
    return errors


def artist_names_for(song: dict[str, Any], snapshot: Snapshot) -> list[str]:
    names: list[str] = []
    for ref in song.get("artists", []):
        aid = str(ref.get("id", ""))
        name = (
            snapshot.artists.get(aid)
            or snapshot.units.get(aid)
            or snapshot.artist_english.get(aid)
            or snapshot.unit_english.get(aid)
            or aid
        ).strip()
        if name and name not in names:
            names.append(name)
    return names


def series_for(song: dict[str, Any], snapshot: Snapshot) -> str:
    series_ids = song.get("seriesIds") or []
    if not series_ids:
        return ""
    sid = str(series_ids[0])
    return snapshot.series_names.get(sid, sid)


def display_artist_for(song: dict[str, Any], snapshot: Snapshot) -> str:
    refs = song.get("artists") or []
    if not refs:
        return ""
    ref = refs[0]
    aid = str(ref.get("id", ""))
    name = (
        snapshot.artist_english.get(aid)
        or snapshot.unit_english.get(aid)
        or snapshot.artists.get(aid)
        or snapshot.units.get(aid)
        or aid
    ).strip()
    variant = str(ref.get("variant") or "").strip()
    return f"{name} ({variant})" if variant else name


def youtube_url(song: dict[str, Any]) -> str:
    video = song.get("musicVideo") or {}
    video_id = str(video.get("videoId") or "").strip()
    return f"https://www.youtube.com/watch?v={video_id}" if video_id else ""


def _override_value(override: dict[str, Any], key: str, default: Any = _MISSING) -> Any:
    if key in override:
        return override[key]
    return default


def _merge_optional_text(
    target: dict[str, Any],
    key: str,
    value: Any,
    fallback_key: str | None = None,
) -> None:
    if value:
        target[key] = str(value)
    elif fallback_key and target.get(fallback_key):
        target[key] = target[fallback_key]
    elif key in target and not target[key]:
        target[key] = ""


def merge_song(
    song: dict[str, Any],
    metadata: dict[str, Any],
    upstream: dict[str, Any],
    snapshot: Snapshot,
    override: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Merge LLerNote-owned fields into one existing song.

    Policy: non-null LLerNote values win; local values are kept when upstream
    has no value; values in scripts/llernote_overrides.json are explicit local
    corrections and always win.
    """
    new_song = dict(song)
    new_meta = dict(metadata)

    new_meta["jp_title"] = str(upstream.get("name") or new_meta.get("jp_title", ""))
    new_meta["phonetic"] = str(
        upstream.get("phoneticName") or new_meta.get("phonetic", "")
    )
    new_meta["llernote_id"] = str(upstream["id"])

    series = series_for(upstream, snapshot)
    if series:
        new_meta["series"] = series

    names = artist_names_for(upstream, snapshot)
    if names:
        new_meta["llernote_artists"] = names

    title = str(new_song.get("title") or new_meta.get("song", ""))
    override_song = _override_value(override, "song")
    if override_song is not _MISSING:
        title = str(override_song)
    new_song["title"] = title
    new_meta["song"] = title

    artist = _override_value(
        override,
        "artist",
        new_meta.get("artist", ""),
    )
    new_meta["artist"] = str(artist or "")
    new_song["artist"] = new_meta["artist"]

    upstream_title_en = upstream.get("englishName")
    if "title_en" in override:
        new_meta["title_en"] = str(override["title_en"] or "")
    elif upstream_title_en:
        new_meta["title_en"] = str(upstream_title_en)

    yt = _override_value(override, "yt", youtube_url(upstream))
    if yt:
        new_meta["yt"] = str(yt)

    wiki_audio = str(upstream.get("wikiAudioUrl") or "").strip()
    if wiki_audio:
        new_meta["wiki_audio"] = wiki_audio

    date = (
        str(upstream.get("releasedOn") or "").strip()
        or str(new_song.get("date") or "").strip()
        or str(new_meta.get("released_on") or "").strip()
    )
    if date:
        new_song["date"] = date
        new_meta["released_on"] = date

    new_song.setdefault("center", "")
    new_song.setdefault("duration", "")
    return new_song, new_meta


def build_new_song(
    upstream: dict[str, Any],
    local_id: int,
    snapshot: Snapshot,
    override: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    title = str(
        _override_value(
            override,
            "song",
            upstream.get("englishName") or upstream.get("name") or "",
        )
        or ""
    )
    artist = str(
        _override_value(override, "artist", display_artist_for(upstream, snapshot))
        or ""
    )
    date = str(upstream.get("releasedOn") or "").strip()
    song = {
        "id": int(local_id),
        "title": title,
        "artist": artist,
        "date": date,
        "center": "",
        "duration": "",
    }

    metadata: dict[str, Any] = {
        "song": title,
        "artist": artist,
        "album": str(override.get("album") or ""),
        "art": str(override.get("art") or ""),
        "source": str(override.get("source") or "llernote"),
    }
    for key in (
        "albumId",
        "album_orig",
        "jp_title_itunes",
        "cover",
        "mbid",
        "mb_release",
    ):
        if key in override:
            metadata[key] = override[key]
    metadata["jp_title"] = str(upstream.get("name") or "")
    metadata["llernote_id"] = str(upstream["id"])
    metadata["title_en"] = str(
        _override_value(
            override,
            "title_en",
            upstream.get("englishName") or "",
        )
        or ""
    )
    metadata["phonetic"] = str(upstream.get("phoneticName") or "")
    metadata["yt"] = str(
        _override_value(override, "yt", youtube_url(upstream)) or ""
    )
    metadata["released_on"] = date
    metadata["series"] = series_for(upstream, snapshot)
    metadata["llernote_artists"] = artist_names_for(upstream, snapshot)
    wiki_audio = str(upstream.get("wikiAudioUrl") or "").strip()
    if wiki_audio:
        metadata["wiki_audio"] = wiki_audio
    return song, metadata


def _entry_diff(before: dict[str, Any], after: dict[str, Any], prefix: str) -> list[str]:
    lines: list[str] = []
    for key in sorted(set(before) | set(after)):
        old = before.get(key, _MISSING)
        new = after.get(key, _MISSING)
        if old == new:
            continue
        old_text = "<absent>" if old is _MISSING else repr(old)
        new_text = "<absent>" if new is _MISSING else repr(new)
        lines.append(f"  {prefix}.{key}: {old_text} -> {new_text}")
    return lines


def plan_project(
    songs: list[dict[str, Any]],
    metadata: dict[str, dict[str, Any]],
    snapshot: Snapshot,
    overrides: dict[str, dict[str, Any]] | None = None,
) -> SyncPlan:
    """Return the expected project data for a snapshot without writing files."""
    overrides = overrides or {}
    new_songs = [dict(song) for song in songs]
    new_metadata = {str(key): dict(value) for key, value in metadata.items()}

    songs_by_id: dict[int, dict[str, Any]] = {}
    for song in new_songs:
        try:
            song_id = int(song["id"])
        except (KeyError, TypeError, ValueError) as exc:
            raise DataError(f"Invalid local song entry: {song!r}") from exc
        if song_id in songs_by_id:
            raise DataError(f"Duplicate local song id: {song_id}")
        songs_by_id[song_id] = song

    local_by_lln: dict[str, str] = {}
    for local_id, value in new_metadata.items():
        lln = str(value.get("llernote_id") or "").strip()
        if not lln:
            raise DataError(f"Metadata {local_id} has no llernote_id")
        if lln in local_by_lln:
            raise DataError(
                f"Duplicate llernote_id {lln}: {local_by_lln[lln]} and {local_id}"
            )
        local_by_lln[lln] = local_id
        if not local_id.isdigit():
            raise DataError(f"Metadata key is not a local song id: {local_id}")
        if int(local_id) not in songs_by_id:
            raise DataError(f"Metadata {local_id} has no matching song entry")

    plan = SyncPlan(songs=new_songs, metadata=new_metadata)
    upstream_ids = set(snapshot.songs_by_id)
    changed: list[str] = []

    for local_id in sorted(new_metadata, key=lambda value: int(value)):
        before = new_metadata[local_id]
        lln = str(before["llernote_id"])
        if lln not in snapshot.songs_by_id:
            plan.local_only.append(lln)
            plan.warnings.append(
                f"LLerNote id {lln} (local {local_id}) is not in the upstream snapshot; "
                "keeping local data"
            )
            continue

        song = songs_by_id[int(local_id)]
        upstream = snapshot.songs_by_id[lln]
        override = overrides.get(lln, {})
        after_song, after_meta = merge_song(song, before, upstream, snapshot, override)
        diff = _entry_diff(before, after_meta, f"metadata[{local_id}]")
        diff.extend(_entry_diff(song, after_song, f"songs[{local_id}]"))
        if diff:
            changed.append(local_id)
            plan.changes.extend(diff)
        new_metadata[local_id] = after_meta
        songs_by_id[int(local_id)] = after_song

    # Update the list with the merged song copies.
    plan.songs = [songs_by_id[int(song["id"])] for song in new_songs]

    next_id = max(songs_by_id, default=0) + 1
    for lln in sorted(upstream_ids - set(local_by_lln), key=lambda value: int(value)):
        upstream = snapshot.songs_by_id[lln]
        override = overrides.get(lln, {})
        requested_id = override.get("local_id")
        if requested_id is not None:
            local_id = int(requested_id)
            if local_id in songs_by_id:
                raise DataError(
                    f"Override for LLerNote {lln} requests local id {local_id}, "
                    "but that id already exists"
                )
        else:
            while next_id in songs_by_id:
                next_id += 1
            local_id = next_id
            next_id += 1

        new_song, new_meta = build_new_song(upstream, local_id, snapshot, override)
        songs_by_id[local_id] = new_song
        new_metadata[str(local_id)] = new_meta
        plan.new_ids.append(local_id)
        plan.upstream_only.append(lln)
        plan.changes.append(f"  added local {local_id} <- LLerNote {lln}")

    plan.songs = [songs_by_id[int(song["id"])] for song in new_songs]
    # New song entries are appended after the existing list, sorted by id.
    plan.songs.extend(
        songs_by_id[local_id]
        for local_id in sorted(plan.new_ids)
    )
    plan.metadata = new_metadata
    plan.changed_ids = changed
    if plan.local_only:
        plan.warnings.append(
            "Upstream snapshot is missing local LLerNote ids: "
            + ", ".join(plan.local_only)
        )
    if plan.upstream_only:
        plan.warnings.append(
            "New upstream songs will be added: " + ", ".join(plan.upstream_only)
        )
    return plan


def project_matches_plan(
    songs: list[dict[str, Any]],
    metadata: dict[str, dict[str, Any]],
    plan: SyncPlan,
) -> bool:
    return songs == plan.songs and metadata == plan.metadata


def cover_file_for(metadata: dict[str, Any]) -> str | None:
    """Return a local cover path (relative to docs/) for legacy cover checks."""
    cover = str(metadata.get("cover") or "").strip()
    if cover:
        if cover.startswith(("http://", "https://")):
            return None
        if cover.startswith("covers/"):
            return cover
        return f"covers/{cover}"

    album = str(metadata.get("album") or "").strip()
    series = str(metadata.get("series") or "").strip()
    if not album:
        return None
    tag = SERIES_FILE_TAG.get(series, "lain")
    slug = re.sub(r"[^a-z0-9]+", "-", album.lower()).strip("-")[:120] or "n-a"
    return f"covers/{tag}--{slug}.webp"


def is_remote_url(value: str) -> bool:
    return value.startswith(("http://", "https://"))


def format_plan(plan: SyncPlan, limit: int = 80) -> str:
    lines: list[str] = []
    if plan.new_ids:
        lines.append(f"New local ids: {', '.join(map(str, plan.new_ids))}")
    if plan.changed_ids:
        lines.append(f"Changed local ids: {', '.join(plan.changed_ids)}")
    if not plan.changes:
        lines.append("No data changes.")
    else:
        lines.extend(plan.changes[:limit])
        if len(plan.changes) > limit:
            lines.append(f"... and {len(plan.changes) - limit} more change(s)")
    for warning in plan.warnings:
        lines.append(f"WARNING: {warning}")
    return "\n".join(lines)
