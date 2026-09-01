#!/usr/bin/env python3
"""P2: enrich each song with album + cover art (iTunes primary, MusicBrainz fallback).
Re-runnable: skips songs already resolved (reads a done-markers json)."""
import json, os, re, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONGS = os.path.join(ROOT, "songs.json")
OUT = os.path.join(ROOT, "metadata.json")
MARK = os.path.join(ROOT, "enrich_progress.json")

HDR = {"User-Agent": "LoveLiveTierlist/0.3 (personal use; contact)"}
ITUNES = "https://itunes.apple.com/search"
MB = "https://musicbrainz.org/ws/2/recording/"

def norm(s):
    if not s: return ""
    return re.sub(r"[^a-z0-9]+", "", s.lower())

def get_json(url, timeout=25, n=3):
    for i in range(n):
        try:
            req = urllib.request.Request(url, headers=HDR)
            return json.load(urllib.request.urlopen(req, timeout=timeout))
        except Exception:
            if i == n - 1:
                return None
            time.sleep(1.6)

def itunes_lookup(title, artist):
    term = urllib.parse.quote(f"{title} {artist}".strip())
    d = get_json(f"{ITUNES}?term={term}&entity=song&limit=8&media=music")
    if not d: return None
    res = d.get("results") or []
    if not res: return None
    want = norm(title)
    best = None
    for r in res:
        sc = 0
        tn = norm(r.get("trackName", ""))
        cn = norm(r.get("collectionName", "") or "")
        ct = r.get("collectionName") or ""
        if want and tn == want: sc += 10
        elif want and want in tn: sc += 5
        # prefer the source single EP over compilation box-sets
        if cn == want or cn.startswith(want) or cn == want + "single":
            sc += 14                       # title-track single
        elif want and want in cn:
            sc += 5
        if re.search(r"(complete|box|best|collection|compilation|greatest)", cn):
            sc -= 8                         # compilation -> deprioritize
        if "live" in tn or "remix" in tn or "(tv" in tn or "(off vocal" in tn:
            sc -= 4
        if cn: sc += 1
        r["_score"] = sc
        if best is None or sc > best["_score"]:
            best = r
    return best

def mb_lookup(title, artist):
    q = urllib.parse.quote(f'recording:"{title}" AND artist:"{artist}"')
    d = get_json(f"{MB}?query={q}&fmt=json&limit=5")
    if not d: return None
    recs = d.get("recordings") or []
    if not recs: return None
    r = recs[0]
    albums = [rel.get("title") for rel in (r.get("releases") or []) if rel.get("title")]
    return {"collectionName": albums[0] if albums else None, "source": "musicbrainz"}

def main():
    songs = json.load(open(SONGS))
    prog = json.load(open(MARK)) if os.path.exists(MARK) else {"done": {}}
    done = prog["done"]
    meta = json.load(open(OUT)) if os.path.exists(OUT) else {}
    missing, n= [], 0
    for s in songs:
        key = str(s["id"])
        if key in done:
            continue
        n += 1
        r = itunes_lookup(s["title"], s["artist"])
        status = "no-match"
        if r and r.get("__error") is None:
            # verify it's a plausible LL track: require non-empty artwork
            art = (r.get("artworkUrl100") or "").replace("100x100", "1000x1000")
            if art:
                status = "itunes"
        if status != "itunes":
            mbr = mb_lookup(s["title"], s["artist"])
            if mbr and mbr.get("collectionName"):
                status = "mb-fallback"
                meta[key] = {"song": s["title"], "artist": s["artist"],
                             "album": mbr["collectionName"], "art": "", "source": "mb"}
            else:
                missing.append({"id": s["id"], "title": s["title"], "artist": s["artist"]})
                meta[key] = {"song": s["title"], "artist": s["artist"],
                             "album": None, "art": "", "source": None}
        else:
            meta[key] = {"song": s["title"], "artist": s["artist"],
                         "album": r.get("collectionName"),
                         "art": art, "source": "itunes",
                         "albumId": r.get("collectionId")}
        done[key] = status
        if n % 25 == 0:
            json.dump(meta, open(OUT, "w"), ensure_ascii=False, indent=1)
            json.dump({"done": done}, open(MARK, "w"))
            print(f"processed {len(done)}/{len(songs)}  missing={len(missing)}", flush=True)
        time.sleep(0.18)
    json.dump(meta, open(OUT, "w"), ensure_ascii=False, indent=1)
    json.dump({"done": done}, open(MARK, "w"))
    json.dump(missing, open(os.path.join(ROOT, "missing.json"), "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    c = Counter(done.values())
    print("DONE:", len(done), "resolved:", len(meta), dict(c))

if __name__ == "__main__":
    main()