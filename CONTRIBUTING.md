# Contributing to Love Live! Song Tierlist

Thanks for helping out! 🎵 This is an unofficial **fan project** — contributions
big or small are welcome.

## Ground rules

- Be respectful. Love Live! is a fan-series: we treat every series and every
  song fairly (no "µ's > all" flame wars in issues 😉).
- Only edit what's needed. No drive-by reformatting or unrelated renames.

## What you can work on

- **Better data**: missing album art, cover mappings, or MusicBrainz IDs.
- **New series**: when a new Love Live! series (or unit) is added, extend the
  series mapping in `docs/app.js` and the metadata in `scripts/`.
- **Frontend**: UI polish, accessibility, performance for 917 cards.
  - UI copy lives in the `en` and `id` tables in `docs/app.js`; add both
    translations when changing labels. English is the default language.
- **Docs**: clearer README, better pipeline comments.

## Working with the data

The canonical data lives in two files, with identical copies under `docs/`:

- `songs.json` — the 917 songs (`id`, `title`, `artist`, `date`, `center`, `duration`)
- `metadata.json` — per-song enrichment (`album`, `art`, `cover`, MBID, kanji title, source)

Most song identity fields are generated from
**[LLerNote](https://github.com/hamproductions/llernote)**. Do not edit
generated fields by hand unless you are fixing a deliberate local exception:

1. Add the correction to `scripts/llernote_overrides.json`.
2. Run the sync/verification commands below.
3. Commit the override file and the regenerated JSON together.

For a new LLerNote song, the sync script chooses the next local `id` and appends
it to both data files. If the song needs an album, art, or cover, add those to
the override entry. Local covers live in `docs/covers/` and should be WebP files
named `{series-tag}--{album-slug}.webp`.

```bash
# check against the pinned snapshot (no writes)
python scripts/sync_llernote.py --check

# pull a newer upstream snapshot; writes data + lock
python scripts/sync_llernote.py --ref main --update-lock

# validate root/docs copies, ids, metadata, dates, and cover references
python scripts/verify_data.py

# unit tests for the merge/sync rules
python -m unittest discover -s scripts/tests -v
```

The sync script is intentionally conservative: LLerNote values replace local
values when present, local values are kept when upstream is empty, and explicit
overrides win over both. It refuses to mix a stale lock with a different
snapshot unless you pass `--update-lock`.

## Before submitting

1. Your branch is up to date with `main`.
2. `python scripts/sync_llernote.py --check` passes.
3. `python scripts/verify_data.py` passes (warnings about pre-existing missing
   art are okay unless your change introduces them).
4. `node --check docs/app.js` passes if you touched any JS.
5. Run `python3 -m http.server 8899` from `docs/` and visually confirm your
   change.
6. Write a clear PR description linking any related issue (`fixes #N`).

## Commit convention

Use conventional commits:

```
feat: add kanji title for <song>
fix: correct cover for <album>
data: refresh LLerNote snapshot
docs: expand contributing guide
```

## Opening a PR

- Describe **what** changed and **why**.
- If it changes data, note the source (for example, the LLerNote commit or an
  override entry).
- Squash messy history if it helps reviewers.

Thanks again — *ganbatte!* 🎤🎶
