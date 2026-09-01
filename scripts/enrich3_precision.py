#!/usr/bin/env python3
"""P2c: precision filter — revert itunes-jp matches whose track name isn't confirmed.
Keeps only where a store result's romanized track == our title; reverts others to missing."""
import json, os, re, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA = os.path.join(ROOT, "metadata.json")

def norm(s): return re.sub(r"[^a-z0-9]+", "", (s or "").lower())

def get_json(url, timeout=22):
    try: return json.load(urllib.request.urlopen(url, timeout=timeout))
    except Exception: return None

def search(term, country):
    url = ("https://itunes.apple.com/search?term=" + urllib.parse.quote(term)
           + f"&entity=song&limit=10&media=music&country={country}")
    d = get_json(url); return (d or {}).get("results") or []

def confirmed(title, artist):
    """Return best result whose track title equals ours (romanized), else None."""
    want = norm(title)
    if not want: return None
    best = None
    for term, country in [(f"{title} {artist}", "JP"), (title, "JP"),
                          (f"{title} {artist}", "US"), (title, "US")]:
        for r in search(term, country):
            if not r.get("artworkUrl100"): continue
            tn = norm(r.get("trackName", ""))
            if tn == want:
                if best is None: best = r
            elif want in tn and len(want) >= 9 and best is None:
                best = r
        time.sleep(0.1)
        if best: break
    return best

def main():
    meta = json.load(open(METADATA))
    jp = [k for k, v in meta.items() if v.get("source") == "itunes-jp"]
    print(f"verifying {len(jp)} itunes-jp matches", flush=True)
    kept = reverted = 0
    for k in jp:
        v = meta[k]
        r = confirmed(v["song"], v["artist"])
        if r:
            v["album"] = r.get("collectionName")
            v["art"] = (r.get("artworkUrl100") or "").replace("100x100", "1000x1000")
            v["source"] = "itunes"  # promoted to confident
            kept += 1
        else:
            v["album"] = None; v["art"] = ""; v["source"] = None   # -> placeholder
            reverted += 1
        if (kept + reverted) % 20 == 0:
            print(f"  kept {kept} reverted {reverted}", flush=True)
    json.dump(meta, open(METADATA, "w"), ensure_ascii=False, indent=1)
    print(f"DONE: kept {kept}, reverted {reverted}")

if __name__ == "__main__":
    main()