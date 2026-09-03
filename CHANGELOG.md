# Changelog

All notable changes to this project are documented here.
This project works towards [Keep a Changelog](https://keepachangelog.com/) and
[Semantic Versioning](https://semver.org/). This is a static site — "releases"
are pushed changes to `main`, which auto-deploy to GitHub Pages.

## [Unreleased]

### Added
- Open-source repo setup: MIT license, code of conduct, security policy,
  issue/PR templates, Dependabot, community-focused README.

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