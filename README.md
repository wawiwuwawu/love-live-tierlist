# Love Live! All-Series Song Tierlist 🎀

Tierlist interaktif untuk **semua 902 lagu** Love Live! (µ's · Aqours · Nijigasaki · Liella! · Hasunosora · +Lain). Navigasi per seri, tierlist global drag & drop (S/A/B/C/D/F), tersimpan di browser (localStorage).

**Live:** https://wawiwuwawu.github.io/love-live-tierlist/

## Sumber data
- **Daftar 902 lagu:** Google Sheet "The Love Live! Google Sheet by BS Anime" (`Songs` sheet)
- **Cover + album:** iTunes/Apple Search API (utama) + MusicBrainz (fallback); judul album diromajikan agar bebas kanji

## Struktur
```
site/            # situs statis (index.html, app.js, style.css, songs.json, metadata.json, covers/)
scripts/         # enrich.py (metadata), enrich2.py (+recall), enrich3_precision.py, render_cards.py
songs.json       # 902 lagu (judul, artist, tanggal, center, durasi)
metadata.json    # per lagu: album + URL cover + sumber
PLAN.md          # rencana implementasi
```

## Deploy (GitHub Pages)
- `main` = source. Konten `site/` di-extract ke branch `gh-pages` untuk di-serve Pages.

## Cara menjalankan lokal
```bash
cd site && python3 -m http.server 8899
# buka http://localhost:8899
```