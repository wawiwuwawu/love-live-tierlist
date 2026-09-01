#!/usr/bin/env python3
"""P2b: second pass using iTunes JP store (expanded recall) for songs that missed pass 1."""
import json, os, re, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA = os.path.join(ROOT, "metadata.json")
MK = os.path.join(ROOT, "enrich2_progress.json")

def norm(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())

def get_json(url, timeout=22):
    try:
        return json.load(urllib.request.urlopen(url, timeout=timeout))
    except Exception:
        return None

def ll_hint(s):
    return any(k in norm(s) for k in
        ["lovelive","love-live","sharethelovelive","schoolidol","livelove",
         "aqours","nijigasaki","liella","idolclub","nijigaku","hasunosora","snowhalat"])

def search(term, country):
    url = (f"https://itunes.apple.com/search?term=" + urllib.parse.quote(term)
           + f"&entity=song&limit=10&media=music&country={country}")
    d = get_json(url)
    return (d or {}).get("results") or []

def best_candidate(title, artist):
    want = norm(title)
    cands = []
    # 1) JP title+artist  2) JP title  3) US title
    for term, country in [(f"{title} {artist}", "JP"), (title, "JP"), (title, "US")]:
        for r in search(term, country):
            cands.append(r)
        time.sleep(0.12)
    best, best_score = None, -1
    for r in cands:
        if not r.get("artworkUrl100"):  # need cover
            continue
        tn = norm(r.get("trackName", "")); cn = norm(r.get("collectionName", "") or "")
        an = norm(r.get("artistName", "") or "")
        sc = 0
        if want and tn == want: sc += 12
        elif want and (want in tn or tn in want): sc += 6
        if ll_hint(an + " " + cn + " " + tn + " " + want): sc += 5
        if "live" in tn or "remix" in tn or "tvsize" in tn or "tv edit" in tn: sc -= 4
        if sc > best_score:
            best, best_score = r, sc
    return best

def main():
    songs = json.load(open(os.path.join(ROOT, "songs.json")))
    meta = json.load(open(METADATA))
    prog = json.load(open(MK)) if os.path.exists(MK) else {"done": {}}
    todo = [s for s in songs if (not meta.get(str(s["id"])).get("art")) if meta.get(str(s["id"]))]
    todo = [s for s in songs if str(s["id"]) not in prog["done"] and
            not (meta.get(str(s["id"]) or {}).get("art"))]
    print(f"targets for pass2: {len(todo)}", flush=True)
    fixed = 0
    for s in todo:
        key = str(s["id"])
        prog["done"][key] = "no"
        r = best_candidate(s["title"], s["artist"])
        art = (r.get("artworkUrl100") or "").replace("100x100", "1000x1000") if r else ""
        if art:
            meta[key] = {"song": s["title"], "artist": s["artist"],
                         "album": r.get("collectionName"), "art": art, "source": "itunes-jp",
                         "albumId": r.get("collectionId")}
            prog["done"][key] = "yes"
            fixed += 1
        if len(prog["done"]) % 25 == 0:
            json.dump(meta, open(METADATA, "w"), ensure_ascii=False, indent=1)
            json.dump(prog, open(MK, "w"))
            print(f"fixed so far: {fixed} / processed {len(prog['done'])}", flush=True)
        time.sleep(0.1)
    json.dump(meta, open(METADATA, "w"), ensure_ascii=False, indent=1)
    json.dump(prog, open(MK, "w"))
    still_stale = [s for s in songs if not meta.get(str(s["id"]), {}).get("art")]
    json.dump([{"id": s["id"], "title": s["title"], "artist": s["artist"]} for s in still_stale],
              open(os.path.join(ROOT, "missing2.json"), "w"), ensure_ascii=False, indent=1)
    print(f"DONE pass2: fixed {fixed}; still missing {len(still_stale)}")

if __name__ == "__main__":
    main()