# Contributing to Love Live! Song Tierlist

Thanks for helping out! 🎵 This is an unofficial **fan project** — contributions
big or small are welcome.

## Ground rules

- Be respectful. Love Live! is a fan-series: we treat every series and every
  song fairly (no "µ's > all" flame wars in issues 😉).
- Only edit what's needed. No drive-by reformatting or unrelated renames.

## What you can work on

- **Better data**: missing **kanji titles** (`jp_title`), correct album/cover
  mappings, more **MusicBrainz IDs**.
- **New series**: when a new Love Live! series (or unit) is added, extend the
  mapping in `scripts/` and the series tabs in `docs/app.js`.
- **Frontend**: UI polish, accessibility, performance for 898 cards.
- **Docs**: clearer README, better pipeline comments.

## Working with the data

Songs live in `docs/songs.json`; the per-song enrichment lives in
`docs/metadata.json`. Both are produced by the pipeline in `scripts/`.

If you fix a cover or add a kanji title, you can edit `metadata.json` directly
(or regenerate via the scripts) and submit a PR — the web app reads those JSON
files as-is.

```bash
# regenerate everything (MusicBrainz is rate-limited; be patient)
./.venv/bin/python scripts/enrich.py
./.venv/bin/python scripts/mb_enrich.py
./.venv/bin/python scripts/jp_title.py
./.venv/bin/python scripts/render_cards.py
```

## Before submitting

1. Your branch is up to date with `main`.
2. `node --check docs/app.js` passes if you touched any JS.
3. Run `python3 -m http.server 8899` from `docs/` and visually confirm your
   change.
4. Write a clear PR description linking any related issue (`fixes #N`).

## Commit convention

Use conventional commits:

```
feat: add kanji title for <song>
fix: correct cover for <album>
data: refresh metadata for Aqours singles
docs: expand contributing guide
```

## Opening a PR

- Describe **what** changed and **why**.
- If it changes data, note the source (e.g. "from Apple/iTunes JP store").
- Squash messy history if it helps reviewers.

Thanks again — *ganbatte!* 🎤🎶