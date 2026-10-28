from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

from llernote_common import (  # noqa: E402
    DATA_FILES,
    DataError,
    json_text,
    make_lock,
    make_snapshot,
    plan_project,
    project_matches_plan,
    verify_lock,
    write_project,
)
from verify_data import check_local  # noqa: E402


def snapshot_files() -> dict[str, bytes]:
    songs = [
        {
            "id": "1",
            "name": "既存曲",
            "phoneticName": "きそんきょく",
            "englishName": None,
            "seriesIds": [1],
            "artists": [{"id": "1", "variant": None}],
            "releasedOn": "2020-01-01",
            "musicVideo": {"videoId": "existing-video", "videoOffset": 0},
            "discographyIds": [1],
            "wikiAudioUrl": "https://example.com/existing.ogg",
        },
        {
            "id": "2",
            "name": "新曲",
            "phoneticName": "しんきょく",
            "englishName": None,
            "seriesIds": [6],
            "artists": [{"id": "133", "variant": "105期"}],
            "releasedOn": "2026-10-14",
            "musicVideo": {"videoId": "new-video", "videoOffset": 12},
            "discographyIds": [2],
            "wikiAudioUrl": None,
        },
    ]
    artists = [
        {"id": "1", "name": "μ's", "englishName": "μ's", "seriesIds": [1]},
        {
            "id": "133",
            "name": "蓮ノ空女学院スクールアイドルクラブ",
            "englishName": "Hasunosora Girls' High School Idol Club",
            "seriesIds": [6],
        },
    ]
    units = [{"id": "133", "name": "蓮ノ空女学院スクールアイドルクラブ"}]
    series_info = [
        {"id": 1, "name": "ラブライブ！", "color": "#f200b5"},
        {"id": 6, "name": "蓮ノ空女学院スクールアイドルクラブ", "color": "#fb8a9b"},
    ]
    series = {
        "ラブライブ！": "Love Live! School idol project",
        "蓮ノ空女学院スクールアイドルクラブ": "Hasunosora Girls' High School Idol Club",
    }
    values = {
        "song-info.json": songs,
        "artists-info.json": artists,
        "units.json": units,
        "series-info.json": series_info,
        "series.json": series,
    }
    return {
        name: json.dumps(value, ensure_ascii=False).encode("utf-8")
        for name, value in values.items()
    }


def local_project() -> tuple[list[dict], dict[str, dict]]:
    songs = [
        {
            "id": 100,
            "title": "Local Existing",
            "artist": "μ's",
            "date": "2020-01-01",
            "center": "",
            "duration": "",
        }
    ]
    metadata = {
        "100": {
            "song": "Local Existing",
            "artist": "μ's",
            "album": "Local Album",
            "art": "https://example.com/art.jpg",
            "source": "itunes",
            "jp_title": "旧題",
            "llernote_id": "1",
            "title_en": "Manual English Title",
            "phonetic": "きゅうだい",
            "released_on": "2020-01-01",
            "series": "Love Live! School idol project",
            "llernote_artists": ["μ's"],
            "yt": "",
            "wiki_audio": "",
        }
    }
    return songs, metadata


class SnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.files = snapshot_files()
        self.snapshot = make_snapshot(self.files, "a" * 40)

    def test_snapshot_loads_and_hashes_all_files(self) -> None:
        self.assertEqual(set(self.snapshot.hashes), set(DATA_FILES))
        self.assertEqual(self.snapshot.series_names["6"], "Hasunosora Girls' High School Idol Club")
        self.assertEqual(self.snapshot.artists["1"], "μ's")

    def test_lock_detects_hash_mismatch(self) -> None:
        lock = make_lock("https://github.com/example/repo.git", "a" * 40, self.snapshot.hashes)
        self.assertEqual(verify_lock(self.snapshot, lock), [])
        lock["files"]["song-info.json"] = "0" * 64
        errors = verify_lock(self.snapshot, lock)
        self.assertTrue(any("Hash mismatch for song-info.json" in error for error in errors))

    def test_plan_preserves_manual_english_when_upstream_is_null(self) -> None:
        songs, metadata = local_project()
        plan = plan_project(songs, metadata, self.snapshot)
        self.assertEqual(plan.metadata["100"]["title_en"], "Manual English Title")
        self.assertEqual(plan.metadata["100"]["jp_title"], "既存曲")
        self.assertEqual(plan.metadata["100"]["yt"], "https://www.youtube.com/watch?v=existing-video")
        self.assertEqual(plan.metadata["100"]["wiki_audio"], "https://example.com/existing.ogg")

    def test_override_can_replace_youtube_link_for_existing_song(self) -> None:
        songs, metadata = local_project()
        overrides = {"1": {"yt": "https://youtu.be/custom-link"}}
        plan = plan_project(songs, metadata, self.snapshot, overrides)
        self.assertEqual(plan.metadata["100"]["yt"], "https://youtu.be/custom-link")

    def test_new_song_uses_override_and_stable_id(self) -> None:
        songs, metadata = local_project()
        overrides = {
            "2": {
                "local_id": 500,
                "song": "New Song",
                "artist": "Hasunosora Girls' High School Idol Club (105)",
                "album": "New Album",
                "art": "https://example.com/new.jpg",
                "cover": "new.webp",
                "source": "llernote",
                "yt": "https://youtu.be/new-video",
            }
        }
        plan = plan_project(songs, metadata, self.snapshot, overrides)
        self.assertEqual(plan.new_ids, [500])
        new_song = plan.songs[-1]
        new_meta = plan.metadata["500"]
        self.assertEqual(new_song["title"], "New Song")
        self.assertEqual(new_song["artist"], "Hasunosora Girls' High School Idol Club (105)")
        self.assertEqual(new_song["date"], "2026-10-14")
        self.assertEqual(new_meta["jp_title"], "新曲")
        self.assertEqual(new_meta["title_en"], "")
        self.assertEqual(new_meta["series"], "Hasunosora Girls' High School Idol Club")
        self.assertEqual(new_meta["llernote_artists"], ["蓮ノ空女学院スクールアイドルクラブ"])
        self.assertEqual(new_meta["cover"], "new.webp")
        self.assertEqual(new_meta["yt"], "https://youtu.be/new-video")

    def test_plan_is_idempotent(self) -> None:
        songs, metadata = local_project()
        first = plan_project(songs, metadata, self.snapshot)
        second = plan_project(first.songs, first.metadata, self.snapshot)
        self.assertTrue(project_matches_plan(first.songs, first.metadata, second))
        self.assertEqual(second.new_ids, [])
        self.assertEqual(second.changed_ids, [])

    def test_local_only_entry_is_reported_not_deleted(self) -> None:
        songs, metadata = local_project()
        metadata["999"] = {
            **metadata["100"],
            "llernote_id": "999",
        }
        songs.append(
            {
                "id": 999,
                "title": "Local Existing",
                "artist": "μ's",
                "date": "2020-01-01",
                "center": "",
                "duration": "",
            }
        )
        plan = plan_project(songs, metadata, self.snapshot)
        self.assertIn("999", plan.local_only)
        self.assertIn("999", plan.metadata)

    def test_json_text_has_no_trailing_newline(self) -> None:
        text = json_text({"a": 1})
        self.assertEqual(text, '{\n  "a": 1\n}')
        self.assertFalse(text.endswith("\n"))


class LocalValidationTests(unittest.TestCase):
    def test_check_local_catches_docs_copy_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "docs").mkdir()
            songs, metadata = local_project()
            write_project(songs, metadata, root)

            docs_songs = json.loads((root / "docs" / "songs.json").read_text(encoding="utf-8"))
            docs_songs[0]["title"] = "Different"
            (root / "docs" / "songs.json").write_text(
                json_text(docs_songs), encoding="utf-8", newline="\n"
            )

            errors, _warnings = check_local(root, songs, metadata)
            self.assertIn("songs.json differs from docs/songs.json", errors)

    def test_check_local_requires_metadata_for_every_song(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "docs").mkdir()
            songs, metadata = local_project()
            write_project(songs, metadata, root)
            metadata = {}
            errors, _warnings = check_local(root, songs, metadata)
            self.assertTrue(any("Song 100 has no metadata entry" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
