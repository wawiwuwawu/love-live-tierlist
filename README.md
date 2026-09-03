<div align="center">

# 🎀 Love Live! Song Tierlist

**The complete interactive tierlist for every Love Live! song.**

A static, open-source web app to rank all **898 Love Live! songs** (µ's · Aqours · Nijigasaki · Liella! · Hasunosora · others) by tier — with drag-and-drop, per-song album art, MusicBrainz IDs and kanji titles.

![GitHub License](https://img.shields.io/github/license/wawiwuwawu/love-live-tierlist)
![GitHub Pages](https://img.shields.io/badge/deploy-GitHub%20Pages-blueviolet)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)
![Static](https://img.shields.io/badge/stack-Vanilla%20JS%20%2B%20CSS-lightgrey)

[**Live demo**](https://wawiwuwawu.github.io/love-live-tierlist/) · [Report a bug](../../issues/new?assignees=&labels=bug&template=bug_report.yml) · [Request a feature](../../issues/new?assignees=&labels=enhancement&template=feature_request.yml)

*Unofficial fan project*

</div>

---

## ✨ Features

- **898 songs**, grouped by series: µ's · Aqours · Nijigasaki · Liella! · Hasunosora · Lain (other/units)
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

- **Song list:** `The Love Live! Google Sheet by BS Anime` (informal community reference of ~900 songs)
- **Album/song identity:** [MusicBrainz](https://musicbrainz.org) IDs (MBID) — the authoritative source for release mapping (~49% of songs have an MBID; the rest are newer unit / game-exclusive songs not yet in the database)
- **Cover art:** Apple / iTunes Search API (highest availability for JP releases)
- **Kanji titles:** iTunes JP store (`*.jp_title` in `metadata.json`)
- Speculative / unreleased placeholders (e.g. the "Niji movie 3" rows) are **excluded** by default.

## 📁 Project structure

```
.
├── docs/                  # ← GitHub Pages root (the deployable static site)
│   ├── index.html        #   single-page app (per-song / per-album views)
│   ├── app.js            #   all frontend logic
│   ├── style.css
│   ├── songs.json        #   the 898 songs
│   ├── metadata.json     #   per-song: album, cover, MBID, kanji title, source
│   └── covers/           #   rendered album-cover cards (WebP)
├── scripts/              # data pipeline (Python 3.11+, Python venv)
│   ├── enrich.py         #   iTunes + MusicBrainz metadata fetch
│   ├── mb_enrich.py      #   MusicBrainz ID matching (rate-limited, resumable)
│   ├── jp_title.py       #   kanji title fetch (iTunes JP)
│   └── render_cards.py   #   compose album-cover cards (Pillow → WebP)
├── songs.json / metadata.json   # pipeline copies (same as docs/)
└── LICENSE · CONTRIBUTING.md · CHANGELOG.md …
```

## 🚀 Getting started

The site is **100% static** — no build step. Run it locally:

```bash
# Python 3.11+, create a venv
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt   # or: openpyxl pillow requests pykakasi

# serve the deployed site
cd docs && python3 -m http.server 8899
# open http://localhost:8899
```

### Rebuild the data (optional)

```bash
./.venv/bin/python scripts/enrich.py        # album + cover metadata
./.venv/bin/python scripts/mb_enrich.py     # MusicBrainz IDs (resumable, ~1 req/s)
./.venv/bin/python scripts/jp_title.py      # kanji titles
./.venv/bin/python scripts/render_cards.py  # regenerate covers/*.webp
```

> MusicBrainz enforces ~1 request/second. `mb_enrich.py` saves checkpoints
> (`mb_checkpoint.json`) so interrupted runs resume where they left off.

## 📦 Deployment

**GitHub Pages serves `main` / `docs` directly** — no separate branch needed.

1. Make your edits under `docs/` (or run the scripts to regenerate data).
2. Push to `main` — GitHub Pages rebuilds automatically.
3. Done: `<user>.github.io/love-live-tierlist/`

## 🤝 Contributing

Contributions are welcome — missing kanji titles, better cover mappings, UI
polish, or new Love Live! series. See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📜 License

[MIT](LICENSE). All Love Live! series trademarks/characters/covers belong to
their owners; this project is a fan work.