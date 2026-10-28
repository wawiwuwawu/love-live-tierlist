<div align="center">

# 🎀 Love Live! Song Tierlist

**The complete interactive tierlist for every Love Live! song.**

A static, open-source web app to rank all **917 Love Live! songs** (µ's · Aqours · Nijigasaki · Liella! · Hasunosora · School Idol Musical · Yohane · BLUEBIRD) by tier — with drag-and-drop, per-song album art, MusicBrainz IDs and kanji titles.

![GitHub License](https://img.shields.io/github/license/wawiwuwawu/love-live-tierlist)
![GitHub Pages](https://img.shields.io/badge/deploy-GitHub%20Pages-blueviolet)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)
![Static](https://img.shields.io/badge/stack-Vanilla%20JS%20%2B%20CSS-lightgrey)

[**Live demo**](https://wawiwuwawu.github.io/love-live-tierlist/) · [Report a bug](../../issues/new?assignees=&labels=bug&template=bug_report.yml) · [Request a feature](../../issues/new?assignees=&labels=enhancement&template=feature_request.yml)

*Unofficial fan project*

</div>

---

## ✨ Features

- **917 songs**, grouped by series: µ's · Aqours · Nijigasaki · Liella! · Hasunosora · School Idol Musical · Yohane · BLUEBIRD
- **Global tierlist** (S/A/B/C/D/F) with **drag-and-drop** — ranks songs across *all* series at once
- Two views: **By Album** (grid of album art) and **By Song** (direct drag)
- **Per-song detail modal** with:
  - Romaji title (main)
  - **Kanji title** (subtitle) with a **one-click copy** button to help you search the song
  - Artist, album, release date, center, tier selector
- **Copy to clipboard**: song title, kanji, or `Title - Artist`
- **Search** by song title, artist, or album
- **localStorage persistence** — your rankings survive page reloads; **Export/Import** JSON as backup
- **Export PNG** — capture your tierlist as an image (via `html2canvas`)
- **Dark mode**
- Fully **static** → free hosting on GitHub Pages, no backend

## 🗂 Data

The catalogue is maintained from **[LLerNote](https://github.com/hamproductions/llernote)** — an
open-source, offline-first Love Live! song database. Its `data/song-info.json` is the
source of truth for:

- Japanese titles (`jp_title`), English/romaji titles (`title_en`), and phonetics (`phonetic`)
- Release dates, series membership, artist credits, YouTube links, and wiki audio
- New songs when LLerNote adds them to the catalogue

Additional data comes from:

- **Album / cover art:** Apple / iTunes Search API (highest availability for JP releases)
- **MusicBrainz:** release metadata and MBIDs where available (493 of 917 songs)
- **Manual corrections:** `scripts/llernote_overrides.json` for local display names,
  new-song album/art mappings, and cases where the project intentionally differs from
  upstream (for example, the English title of “Oide yo! Ishikawa Daikankou II”).

LLerNote data is pinned in [`scripts/llernote.lock.json`](scripts/llernote.lock.json)
(commit + SHA-256 hashes of the five upstream JSON files). This keeps builds and
verification reproducible even when the upstream `main` branch moves. The lock is
updated by the sync workflow; see below.

## 📁 Project structure

```
.
├── docs/                       # ← GitHub Pages root (the deployable static site)
│   ├── index.html              #   single-page app (per-song / per-album views)
│   ├── app.js                  #   all frontend logic
│   ├── style.css
│   ├── songs.json              #   the 917 songs
│   ├── metadata.json           #   per-song: album, cover, MBID, kanji title, source
│   └── covers/                 #   album-cover WebP files
├── scripts/                    # LLerNote pipeline (Python 3.11+, stdlib only)
│   ├── sync_llernote.py        #   sync upstream data + write the lock
│   ├── verify_data.py          #   structural and cross-file validation
│   ├── llernote_common.py      #   shared sync/verification helpers
│   ├── llernote_overrides.json #   explicit local corrections
│   ├── llernote.lock.json      #   pinned upstream commit + file hashes
│   └── tests/                  #   stdlib unittest suite
├── .github/workflows/          # CI verification + scheduled LLerNote PR
├── songs.json / metadata.json  # pipeline copies (same as docs/)
└── LICENSE · CONTRIBUTING.md · CHANGELOG.md …
```

## 🚀 Getting started

The site is **100% static** — no build step and no runtime dependencies. Run it locally:

```bash
# serve the deployed site
cd docs
python3 -m http.server 8899
# open http://localhost:8899
```

The Python scripts use only the standard library, so no virtualenv or
`pip install` is required.

### Sync and verify the data

```bash
# Check the local data against the pinned LLerNote snapshot
python scripts/sync_llernote.py --check

# Fetch the latest upstream main, update data, and refresh the lock
python scripts/sync_llernote.py --ref main --update-lock

# Structural checks: root/docs copies, ids, metadata, dates, covers
python scripts/verify_data.py

# Unit tests for the sync/merge rules
python -m unittest discover -s scripts/tests -v
```

`sync_llernote.py` never silently deletes local songs or hand-written values:
LLerNote values win when present, local values are kept when upstream is empty,
and `llernote_overrides.json` wins over both. New upstream songs are appended
with the next local id; if a new song has no album/cover, add an override and
a cover file, then rerun `verify_data.py`.

## 🤖 Automation

Two GitHub Actions workflows keep the data current:

- **`verify.yml`** runs on every push and pull request: unit tests, local data
  validation, and a drift check against the pinned LLerNote snapshot.
- **`llernote-sync.yml`** runs weekly and on manual dispatch: syncs upstream
  `main`, verifies the result, commits to a `chore/llernote-sync-*` branch, and
  opens a pull request against `main` instead of pushing directly.

The scheduled sync creates a normal PR for review; it does not auto-merge.

## 📦 Deployment

**GitHub Pages serves `main` / `docs` directly** — no separate branch needed.

1. Merge data/UI changes into `main` (the sync workflow opens a PR for LLerNote updates).
2. GitHub Pages rebuilds automatically from `docs/`.
3. Done: `<user>.github.io/love-live-tierlist/`

## 🤝 Contributing

Contributions are welcome — missing kanji titles, better cover mappings, UI
polish, or new Love Live! series. See [CONTRIBUTING.md](CONTRIBUTING.md).

When changing song data, prefer updating `scripts/llernote_overrides.json` or
the LLerNote upstream project instead of editing the generated JSON by hand.

## 📜 License

[MIT](LICENSE). All Love Live! series trademarks/characters/covers belong to
their owners; this project is a fan work. LLerNote is a separate community
project; see its repository for its own terms and credits.
