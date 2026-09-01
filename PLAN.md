# Love Live! All-Series Tierlist — Implementation Plan

> Sumber: Google Sheets (902 lagu) + iTunes/Apple Search API (art) + MusicBrainz (fallback metadata)

## Ringkasan Terverifikasi
- **902 lagu**, 239 grup/artist — sheet `Songs` baris 52–953 (col: Song Name, Artist, Date, Center, Duration)
- **iTunes Search API**: 9/10 cocok instan, art 1000×1000, tanpa rate-limit → **sumber utama**
- **MusicBrainz**: 503 + banyak match salah → **fallback** saja
- **GitHub Pages**: cukup. ~150–250 album → cover render WebP ~40–80KB → total ~30–60MB

## Keputusan
- Sumber: **Hybrid** (iTunes utama → MusicBrainz fallback → label 'missing' utk sisanya)
- Web: **Static murni** HTML/JS, deploy gh-pages
- Layout: **navigasi per seri** (µ's/Aqours/Niji/Liella/Lain), **tierlist global semua grup** (S/A/B/C/D/F, save localStorage)

## Tahap
### 🔴 P1 — Ekstraksi Data
- `songs.json`: 902 entri (id, judul, artist, tanggal, durasi, group/seri)
- Verifikasi: count=902, sampling 10 lagu

### 🟠 P2 — Enrich Metadata
- Query iTunes per lagu → `collectionName` (album) + `artworkUrl100→1000x1000`
- Dedupe per album (≈1× request per album)
- Gagal → MusicBrainz `recording?query=recording:"... " AND artist:"..."`
- Sisa nihil → `missing` + cover generik
- Output: `metadata.json`
- Verifikasi: % cover; daftar missing

### 🟡 P3 — Render Kartu Album
- Pillow: cover 1000×1000 + **banner teks nama album di ATAS foto**
- 1 kartu per album (bukan 902), file bernama slug, WebP ~40–80KB
- Render 3 contoh dulu utk dicek sebelum render semua
- Output: `covers/*.webp` + `covers.json`

### 🟢 P4 — Web Tierlist
- Grid kartu album, filter/tab per seri
- Tierlist global drag & drop S/A/B/C/D/F per lagu, localStorage
- Lazy-load/virtualisasi utk 902 kartu, responsif, dark mode
- Output: `index.html` + `app.js` + `songs.json` + `metadata.json` + `covers/`

### 🟢 P5 — Deploy GitHub Pages
- Repo + branch `gh-pages`, tambah `.nojekyll`
- Verifikasi URL live, hitung kartu, tes drag & drop