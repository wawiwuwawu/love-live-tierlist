#!/usr/bin/env python3
"""Happy-path: (1) drop speculative placeholder rows, (2) fetch JP (kanji) title
from iTunes JP store per song, merge into metadata + write clean songs.json."""
import json, re, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = "/home/dede/love-live-tierlist"
def load(p):
    return json.load(open(f"{ROOT}/{p}"))

def save(p, o):
    json.dump(o, open(f"{ROOT}/{p}", "w"), ensure_ascii=False, indent=1)

# 1) drop placeholders
songs = load("docs/songs.json")
bads = [s for s in songs if "niji movie 3" in (s.get("title") or "").lower()
        or (s.get("title") or "").lower().startswith(("group song", "another group song"))]
bad_ids = {s["id"] for s in bads}
print("placeholder rows to drop:", len(bads), [s["title"] for s in bads])
songs = [s for s in songs if s["id"] not in bad_ids]

# 2) JP title fetch
def jp_title(title, artist=""):
    term = urllib.parse.quote(title)
    url = f"https://itunes.apple.com/search?term={term}&entity=song&limit=3&media=music&country=JP"
    try:
        d = json.load(urllib.request.urlopen(url, timeout=15))
        for r in (d.get("results") or []):
            tn = r.get("trackName") or ""
            if tn and re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", tn):
                return tn, r.get("trackName")
        # fallback: any trackName
        if d.get("results"):
            return (d["results"][0].get("trackName") or ""), (d["results"][0].get("trackName") or "")
    except Exception:
        pass
    return "", ""

# build song list for jp title
todo = [s for s in songs if s['id'] not in bad_ids]
results = {}
def work(s):
    jp, _raw = jp_title(s["title"], s.get("artist", ""))
    return s["id"], jp
with ThreadPoolExecutor(max_workers=10) as ex:
    for sid, jp in ex.map(work, todo):
        results[sid] = jp

# 3) merge into metadata + write songs
for path in ["docs/metadata.json", "metadata.json"]:
    meta = load(path)
    # drop placeholders
    for _id in bad_ids:
        meta.pop(str(_id), None)
    added = 0
    for _id, jp in results.items():
        k = str(_id)
        if jp and k in meta:
            meta[k]["jp_title"] = jp
            added += 1
    save(path, meta)
    print(path, "-> songs kept:", len(meta), "| jp_title added:", added)

# write cleaned songs (drop placeholders)
for path in ["docs/songs.json", "songs.json"]:
    save(path, songs)
    print(path, "-> songs:", len(songs))
json.dump({}, open("/dev/null", "w"))