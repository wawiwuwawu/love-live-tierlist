# Changelog

All notable changes to this project are documented here.
This project works towards [Keep a Changelog](https://keepachangelog.com/) and
[Semantic Versioning](https://semver.org/). This is a static site — "releases"
are pushed changes to `main`, which auto-deploy to GitHub Pages.

## [Unreleased]

### Added
- Open-source repo setup: MIT license, code of conduct, security policy,
  issue/PR templates, Dependabot, community-focused README.
- LLerNote sync pipeline (`scripts/sync_llernote.py`, `scripts/verify_data.py`)
  with a pinned commit/hash lock, explicit local overrides, and a stdlib test
  suite.
- GitHub Actions: data verification on pushes/PRs and a weekly/manual LLerNote
  sync that opens a branch + pull request instead of pushing to `main`.
- Two new Hasunosora 105期 songs: **Soleil Smile** and **Hyaku Okunen Bun no
  Shiawase** (released 2026-10-14), bringing the catalogue to **917 songs**.
- README now credits [LLerNote](https://github.com/hamproductions/llernote) as
  the primary song-data source and documents the sync/verification workflow.

### Changed
- Synced song metadata with LLerNote commit
  `c1c62f512921b14f903d0373ac4bce7cb8f1ba6e`: added 13 wiki audio links,
  corrected YouTube links for songs 949–952, set the official Soleil Smile
  video override, filled missing release/English data, and normalized metadata
  titles.
- Replaced the legacy enrichment scripts with the LLerNote pipeline; removed
  obsolete one-off/broken scripts and the unused Python dependency list.
- The site header and document title now derive the song count from the loaded
  data, and the header is updated to 917 songs.
- The interface is now English by default with a persistent EN/ID language
  switch. The theme now defaults to light, with an accessible persistent dark
  switch and no flash on load.

### Fixed
- `scripts/verify_data.py` now prints Japanese series names correctly on
  Windows consoles using legacy code pages.

## [0.1.0] — 2026-09-01

### Added
- Custom frontend built on vanilla HTML/CSS/JS with two views:
  *By Album* (art grid) and *By Song* (direct drag).
- Global tierlist **S/A/B/C/D/F** with drag-and-drop, `localStorage`
  persistence, JSON **Export/Import** backup, and **Export PNG**.
- **Search** across song title, artist, and album.
- Per-song detail modal with romaji title, artist, album, release date,
  center, tier selector, and copy-to-clipboard buttons.
- Dark mode.
- Data pipeline:
  - `enrich.py` — album + cover art from Apple/iTunes Search API and
    MusicBrainz fallback.
  - `mb_enrich.py` — MusicBrainz ID (MBID) matching (rate-limited, resumable).
  - `jp_title.py` — kanji titles from the iTunes JP store.
  - `render_cards.py` — album-cover cards (title banner above art) as WebP.
- **898 songs** across µ's · Aqours · Nijigasaki · Liella! · Hasunosora · Lain.
- **493/898** songs mapped to a MusicBrainz ID; **114** have kanji titles.
- Deploy served from `main` / `docs` via GitHub Pages (no separate branch).

### Removed
- Speculative / unreleased "Niji movie 3" placeholder rows (were part of the
  source spreadsheet's 902 rows but are not real song titles).

[0.1.0]: https://github.com/wawiwuwawu/love-live-tierlist/releases