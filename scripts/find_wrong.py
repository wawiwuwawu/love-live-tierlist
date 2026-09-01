#!/usr/bin/env python3
"""Identify songs whose current album cover came from a non-LoveLive release
(based on the iTunes release artistName), as targets to re-confirm via MusicBrainz."""
import json, time, urllib.request
ROOT = "/home/dede/love-live-tierlist"
meta = json.load(open(f"{ROOT}/docs/metadata.json"))

LL = [
 "μ", "u's", "mus", "aqueous", "aqours", "nijigasaki", "liella", "hasunosora",
 "love live", "school idol", "idol club", "nijigaku", "sunshine", "printemps",
 "bibi", "guilty kiss", "azalea", "cyaron", "qu4rtz", "diverdiva", "azuna",
 "r3birth", "kaleidoscope", "5yncri5e", "catchu", "sunny passion", "mira-cra",
 "dollchestra", "cerise", "edel note", "nyaovenus", "ai scream", "ikizurai",
 "snow hal", "tokimeki", "lailaps", "miradob", "dobbe", "saint snow", "katamukyu",
 "aqua", "chika", "riko", "kanan", "dia", "you", "yoshiko", "hanamaru", "ruby",
 "aysha", "kanon", "chisato", "sumire", "ren", "kinako", "mei", "shiki", "keke",
 "marie", "natsumi",
]
def is_ll(t):
    t=(t or "").lower()
    if "(cv" in t: return True
    return any(k in t for k in LL)

def lookup(aid, cache):
    if aid in cache: return cache[aid]
    url=f"https://itunes.apple.com/lookup?id={aid}"
    an=None
    try:
        d=json.load(urllib.request.urlopen(url,timeout=15))
        for r in d.get("results",[]):
            if r.get("wrapperType")=="collection":
                an=r.get("artistName") or r.get("collectionArtistName") or ""; break
    except Exception: pass
    cache[aid]=an; time.sleep(0.06)
    return an

cache={}
fixes=[]
for k,v in meta.items():
    aid=str(v.get("albumId")) if v.get("albumId") else None
    if not (v.get("art") and aid): continue
    an=lookup(aid,cache)
    if an is None: continue
    if not is_ll(an):
        fixes.append({"id":k,"song":v["song"],"artist":v["artist"],"album":v.get("album"),
                      "releaseArtist":an,"aid":aid})
print(f"songs with non-LL release artist (fix candidates): {len(fixes)}")
for f in fixes:
    print(f"  {f['id']:>4} {str(f['song'])[:30]:32}| {str(f['album'])[:32]:34}| {str(f['releaseArtist'])[:22]}")
json.dump(fixes, open(f"{ROOT}/fixlist.json","w"), ensure_ascii=False, indent=1)
print("saved fixlist.json")