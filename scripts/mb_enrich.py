#!/usr/bin/env python3
"""MusicBrainz enrichment for 902 Love Live songs.
For each song: MB recording search (lenient title), pick best candidate,
record MBID + release + is_ost. Resumable via checkpoint. Covers stay from iTunes.
Run in background; ~1 req/s (MB rate limit) with 503 retry."""
import json, os, re, time, urllib.request, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "docs", "songs.json")
OUT = os.path.join(ROOT, "mb_map.json")
CK = os.path.join(ROOT, "mb_checkpoint.json")
HDR = {"User-Agent": "LoveLiveTierlist/0.4 (personal use; contact)"}

# OST / instrumental / soundtrack markers -> keep "lagu only"
OST_MARK = re.compile(r"(soundtrack|original.?sountrack|ost|bgm|instrumental|background music|drama\b|piano|relaxing|remaster|audio drama|voice drama|karaoke|off.?vocal|rhythm game|select\.?\b|arrange album|compilation\b)", re.I)
# release titles that are clearly not the primary song album we want
SKIP_MARK = re.compile(r"(soundtrack|bgm|piano|relaxing|instrumental|drama|radio|dj mix|memorial|tribute)", re.I)

def mb_search(title, limit=5):
    q = urllib.parse.quote(f'recording:"{title}"')
    url = "https://musicbrainz.org/ws/2/recording/?" + urllib.parse.urlencode({
        "query": f'recording:"{title}"', "limit": limit, "fmt": "json"})
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HDR)
            d = json.load(urllib.request.urlopen(req, timeout=30))
            return d.get("recordings", [])
        except Exception:
            time.sleep(2.5 + attempt)
    return []

def top_release(rec):
    rels = rec.get("releases") or []
    if not rels: return None
    # prefer non-OST release
    rels = sorted(rels, key=lambda r: 0 if SKIP_MARK.search(r.get("title","") or "") else 1)
    return rels[0]

def classify(title, rel_title):
    t = (title or "") + " " + (rel_title or "")
    return bool(SKIP_MARK.search(t))

def main():
    songs = json.load(open(SONGS))
    meta = {}
    ck = json.load(open(CK)) if os.path.exists(CK) else {"done": {}}
    done = ck["done"]
    try:
        meta = json.load(open(OUT))
    except Exception:
        meta = {}
    print(f"total songs: {len(songs)}; already done: {len(done)}", flush=True)
    n = 0
    for s in songs:
        key = str(s["id"])
        if key in done: continue
        n += 1
        recs = mb_search(s["title"])
        res = {"mbid": None, "release": None, "is_ost": False, "match": "none"}
        # pick best: exact title preferrec, then first with a release
        want = re.sub(r"[^a-z0-9]+", "", s["title"].lower())
        best = None
        for r in recs:
            rt = re.sub(r"[^a-z0-9]+", "", (r.get("title") or "").lower())
            if rt == want: best = r; break
        if best is None and recs:
            best = recs[0]
        if best:
            rel = top_release(best)
            rel_title = ((rel or {}).get("title")) or ""
            res = {"mbid": best.get("id"), "release": rel_title,
                   "is_ost": classify(s["title"], rel_title),
                   "rec_title": best.get("title"),
                   "artist": ((best.get("artist-credit") or [{}])[0].get("name")) if best.get("artist-credit") else "",
                   "match": "exact" if best and re.sub(r"[^a-z0-9]+","",(best.get("title") or "").lower())==want else "fuzzy"}
        meta[key] = res
        done[key] = res["mbid"] is not None and not res["is_ost"]
        if n % 15 == 0:
            json.dump(meta, open(OUT, "w"), ensure_ascii=False, indent=1)
            json.dump({"done": done}, open(CK, "w"))
            print(f"processed {len(done)}/{len(songs)} ost={sum(1 for v in meta.values() if v['is_ost'])}", flush=True)
        time.sleep(1.15)
    json.dump(meta, open(OUT, "w"), ensure_ascii=False, indent=1)
    json.dump({"done": done}, open(CK, "w"))
    found = sum(1 for v in meta.values() if v["mbid"])
    ost = sum(1 for v in meta.values() if v["is_ost"])
    print(f"DONE MB enrich: {len(meta)}; with MBID={found}; OST flagged={ost}")

if __name__ == "__main__":
    main()