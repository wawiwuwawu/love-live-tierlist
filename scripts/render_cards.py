#!/usr/bin/env python3
"""P3: render a card per album — title banner ABOVE the 1:1 cover, saved as WebP.
Deterministic filename: covers/{seriesTag}--{slug(album)}.webp  (matches app.js)."""
import json, os, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA = os.path.join(ROOT, "metadata.json")
SONGS = os.path.join(ROOT, "songs.json")
COV_DIR = os.path.join(ROOT, "site", "covers")
SRC_DIR = os.path.join(COV_DIR, "_src")
os.makedirs(SRC_DIR, exist_ok=True)

HDR = {"User-Agent": "LoveLiveTierlist/0.3 (personal; contact)"}
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
SIZE = 1000   # final square cover length
BANNER_H = 150

def slug(s):
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)[:60].strip("-")
    return s or "n-a"

def seriestag(s): return ("mus" if s == "µs" else ("lain" if s in ("Musical", "Ikizurai-Bu") else (s or "lain"))).lower()

def series_of(artist):
    a = (artist or "").lower()
    if not a: return "Lain"
    for s, keys in {
        "µs": ["µ","printemps","bibi","lily white","\u00b5","muse","a-rise","stray","honoka","kotori","umi","hanayo","rin","maki","nico","eli","nozomi"],
        "Aqours": ["aqours","cyazalea","yyy","wai wai wai","cyaron","azalea","guilty","saint aqours","saint snow","chika","riko","kanan","dia","yoshiko","yohane","hanamaru","mari","ruby","you","gkss"],
        "Niji": ["nijigasaki","nijigaku","qu4rtz","diverdiva","azuna","a・zu","r3birth","yuuki","setsuna","ayumu","kasumi","shizuku","karin","ai","kanata","emma","rina","shioriko","shiroko","mia","lanzhu","yu"],
        "Liella": ["liella","catchu","kaleidoscope","kaleidoscore","5yncri5e","syncrise","sunny","kanon","keke","chisato","sumire","ren","kinako","mei","shiki","natsumi","wien","margarete","tomari"],
        "Hasunosora": ["hasu","hasunosora","nyaovenus","cerise","dollchestra","mira-cra","miracra","mira cra","edel","giiter","kaho","sayaka","kozue","tsuzuri","tsuziri","rurino","megumi","megu","kahomegu","gelato","ginko","kosuzu","hime","ceras"],
        "Musical": ["school idol musical","musical","tsubakisakuhana","takizakura","sim supports","rurika","yuzuha","yukino","hikaru","maya","anzu","misuzu","toa","rena","sayaka harukaze","madoka","kyoka"],
        "Ikizurai-Bu": ["ikizurai","ikizurai-bu","ikizuraibu","call me","kidokumachi","kobumi otome","chaki","plumina","mi×nori=tea","minori","sh1on","polka","mai","azabu","akira","hanabi","yukuri","aurora","midori","miracle","noriko","shion","chofu"]
    }.items():
        for k in keys:
            pattern = r'(?:^|[^a-z0-9])' + re.escape(k.lower()) + r'(?:$|[^a-z0-9])'
            if re.search(pattern, a):
                return s
    return "Lain"

def download(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers=HDR)
        return urllib.request.urlopen(req, timeout=timeout).read()
    except Exception:
        return None

def load_font(path, size):
    try: return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def fit_text(draw, text, font_big, font_small, max_w, start):
    f = font_big
    while f.size > start and draw.textlength(text, font=f) > max_w:
        f = load_font(FONT_BOLD, f.size - 4) if False else ImageFont.truetype(FONT_BOLD, f.size - 4)
    if draw.textlength(text, font=f) <= max_w: return f
    return ImageFont.truetype(FONT_BOLD, start)

def render_card(album, art_url, out_path):
    S = SIZE
    W, H = S, S + BANNER_H
    # background
    img = Image.new("RGB", (W, H), (30, 26, 44))
    d = ImageDraw.Draw(img)
    # banner gradient (accent pink -> purple)
    top, bot = (232, 98, 154), (142, 111, 224)
    for y in range(BANNER_H):
        t = y / BANNER_H
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=col)
    # cover
    try:
        if art_url:
            data = download(art_url)
            if data:
                cover = Image.open(BytesIO(data)).convert("RGB")
            else:
                cover = None
        else:
            cover = None
    except Exception:
        cover = None
    if cover is None:
        cover = Image.new("RGB", (S, S), (52, 48, 70))
        cd = ImageDraw.Draw(cover)
        for i in range(0, S, 80):
            cd.line([(i, 0), (0, i)], fill=(66, 60, 86))
            cd.line([(S - i, S), (S, S - i)], fill=(66, 60, 86))
    cover = cover.resize((S, S), Image.LANCZOS)
    img.paste(cover, (0, BANNER_H))

    # title text centered in banner
    title = album if album else "TANPA ALBUM"
    d2 = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, 54)
    while f.size > 22 and d2.textlength(title, font=f) > W - 64:
        f = ImageFont.truetype(FONT, f.size - 2)
    tw = d2.textlength(title, font=f)
    d2.text(((W - tw) / 2, (BANNER_H - f.size) / 2 - 2), title, font=f, fill=(255, 255, 255))

    img.save(out_path, "WEBP", quality=82, method=6)
    return img.size, os.path.getsize(out_path)

def build_albums():
    songs = json.load(open(SONGS))
    meta = json.load(open(METADATA))
    albums = {}   # key: tag--slug -> {title, series, art}
    for s in songs:
        m = meta.get(str(s["id"])) or {}
        album = m.get("album") or m.get("collectionName") or "TANPA ALBUM"
        series = series_of(s["artist"])
        key = f"{seriestag(series)}--{slug(album)}"
        e = albums.get(key)
        if not e:
            albums[key] = {"title": album, "series": series, "art": m.get("art") or ""}
        elif not albums[key]["art"] and m.get("art"):
            albums[key]["art"] = m["art"]
    return albums

def main(limit=None):
    albums = build_albums()
    items = list(albums.items())
    if limit: items = items[:limit]
    print(f"total albums: {len(albums)}; rendering {len(items)} now", flush=True)
    results = []
    for key, a in items:
        out = os.path.join(COV_DIR, key + ".webp")
        try:
            size, kb = render_card(a["title"], a["art"], out)
            results.append((key, kb))
            print(f"  {key:45} {kb/1024:5.1f} KB", flush=True)
        except Exception as ex:
            print(f"  {key:45} ERR {ex}", flush=True)
    results.sort(key=lambda x: -x[1])
    total = sum(kb for _, kb in results)
    print(f"DONE: {len(results)} cards, total {total/1024:.1f} MB")
    json.dump([{"key": k, "kb": round(kb/1024, 1)} for k, kb in results],
              open(os.path.join(COV_DIR, "covers_manifest.json"), "w"))

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)