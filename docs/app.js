/* Love Live! All-Series Song Tierlist */
const STORE='ll_tiers_v1';
const LANG_KEY='ll_lang_v1';
const THEME_KEY='ll_theme_v1';
let songs=[], meta={}, albums={}, songMap={};
let currentSeries='All', currentView='songs', searchQuery='', hideTiered=true;
let currentLang='en', currentTheme='light';
let activeAlbum=null, activeSongId=null;

const I18N={
  en:{
    'meta.title': `Love Live! Song Tierlist ({count} songs)`,
    'header.subtitlePrefix': `µ's · Aqours · Nijigasaki · Liella! · Hasunosora · Musical · Yohane · BLUEBIRD —`,
    'header.subtitleSuffix': `songs, one tierlist`,
    'search.placeholder': `🔍 Search songs or albums...`,
    'view.albums': `📁 By Album`,
    'view.songs': `🎵 By Song (Direct Drag)`,
    'toolbar.hideTiered': `Hide tiered`,
    'actions.exportPng': `📷 Export PNG`,
    'actions.backup': `💾 Backup`,
    'actions.backupTitle': `Save data to a JSON file`,
    'actions.import': `📂 Import`,
    'actions.importTitle': `Load data from a JSON file`,
    'actions.reset': `Reset`,
    'theme.label': `Dark mode`,
    'lang.label': `Language`,
    'tierlist.title': `Global Tierlist`,
    'tierlist.tip': `💡 Drag song covers from the gallery below directly onto a tier row`,
    'tierlist.clear': `Clear All Tiers`,
    'grid.songs': `Pick & Drag Songs to Tierlist`,
    'grid.albums': `Album & Single List`,
    'export.heading': `📷 Tierlist PNG Export`,
    'export.download': `⬇️ Download Image (PNG)`,
    'nav.all': `All`,
    'series.other': `Other`,
    'stats': `{albums} albums · {songs} songs · {tiered} tiered`,
    'empty.albums': `No matching albums.`,
    'empty.songs': `🎉 All songs are already tiered! (Or no songs match your search.)`,
    'album.none': `(no album)`,
    'album.count': `{count} songs`,
    'album.moreSongs': `+{count} more songs…`,
    'album.setAll': `Set all songs to tier:`,
    'album.choose': `— Choose —`,
    'album.tierOption': `Tier {tier}`,
    'album.clearOption': `Reset (Clear)`,
    'album.cleared': `Cleared all songs in {album}`,
    'album.setAllToast': `✅ Set all songs to Tier {tier}`,
    'song.fallback': `Song #{id}`,
    'song.fallbackSimple': `Song`,
    'song.dragToTierlist': `Drag to tierlist`,
    'song.dragToTier': `Drag this song to a tier`,
    'song.removeFromTier': `Remove from tier`,
    'detail.copyJpTitle': `Copy Japanese title`,
    'detail.copyJp': `📋 Copy`,
    'detail.copyTitle': `📋 Copy Song Title`,
    'detail.copyFull': `🎵 Copy (Title - Artist)`,
    'detail.released': `📅 Released: {date}`,
    'detail.center': `⭐ Center: {center}`,
    'detail.currentTier': `Current tier:`,
    'detail.noTier': `— Not tiered —`,
    'detail.youtube': `Open on YouTube`,
    'detail.youtubeAlt': `YouTube thumbnail`,
    'toast.drag': `✅ "{title}" added to Tier {tier}`,
    'toast.copyTitle': `✅ Song title copied!`,
    'toast.copyFull': `✅ (Title - Artist) copied!`,
    'toast.copyJp': `✅ Japanese title copied!`,
    'toast.copyFail': `Failed to copy text.`,
    'toast.imported': `✅ Tierlist data imported!`,
    'toast.invalidJson': `❌ Invalid JSON file.`,
    'toast.exportLibrary': `The html2canvas library is not ready. Make sure you are connected to the internet.`,
    'toast.generating': `⏳ Generating...`,
    'toast.exportFailed': `Failed to export image: {error}`,
    'confirm.clear': `Remove all songs from the tierlist?`,
    'confirm.reset': `Reset all tierlist data?`,
    'tier.empty': `empty`,
    'grid.tierPlaceholder': `— Tier —`
  },
  id:{
    'meta.title': `Love Live! Song Tierlist ({count} lagu)`,
    'header.subtitlePrefix': `µ's · Aqours · Nijigasaki · Liella! · Hasunosora · Musical · Yohane · BLUEBIRD —`,
    'header.subtitleSuffix': `lagu, satu tierlist`,
    'search.placeholder': `🔍 Cari lagu atau album...`,
    'view.albums': `📁 Per Album`,
    'view.songs': `🎵 Per Lagu (Direct Drag)`,
    'toolbar.hideTiered': `Sembunyikan ter-tier`,
    'actions.exportPng': `📷 Export PNG`,
    'actions.backup': `💾 Backup`,
    'actions.backupTitle': `Simpan data ke file JSON`,
    'actions.import': `📂 Import`,
    'actions.importTitle': `Muat data dari file JSON`,
    'actions.reset': `Reset`,
    'theme.label': `Mode gelap`,
    'lang.label': `Bahasa`,
    'tierlist.title': `Tierlist Global`,
    'tierlist.tip': `💡 Tarik (drag) foto lagu dari galeri bawah langsung ke baris tier`,
    'tierlist.clear': `Kosongkan Semua Tier`,
    'grid.songs': `Pilih & Drag Lagu Ke Tierlist`,
    'grid.albums': `Daftar Album & Single`,
    'export.heading': `📷 Hasil Export Tierlist PNG`,
    'export.download': `⬇️ Unduh Gambar (PNG)`,
    'nav.all': `Semua`,
    'series.other': `Lain`,
    'stats': `{albums} album · {songs} lagu · {tiered} ter-tier`,
    'empty.albums': `Belum ada album yang cocok.`,
    'empty.songs': `🎉 Semua lagu telah masuk ke tierlist! (Atau tidak ada lagu yang cocok dengan pencarian).`,
    'album.none': `(tanpa album)`,
    'album.count': `{count} lagu`,
    'album.moreSongs': `+{count} lagu lagi…`,
    'album.setAll': `Set Semua Lagu ke Tier:`,
    'album.choose': `— Pilih —`,
    'album.tierOption': `Tier {tier}`,
    'album.clearOption': `Reset (Kosongkan)`,
    'album.cleared': `Semua lagu di {album} sudah dikosongkan`,
    'album.setAllToast': `✅ Semua lagu diset ke Tier {tier}`,
    'song.fallback': `Lagu #{id}`,
    'song.fallbackSimple': `Lagu`,
    'song.dragToTierlist': `Tarik ke tierlist`,
    'song.dragToTier': `Tarik lagu ini ke tier`,
    'song.removeFromTier': `Lepas dari tier`,
    'detail.copyJpTitle': `Salin judul kanji`,
    'detail.copyJp': `📋 Salin`,
    'detail.copyTitle': `📋 Salin Judul Lagu`,
    'detail.copyFull': `🎵 Salin (Judul - Artis)`,
    'detail.released': `📅 Rilis: {date}`,
    'detail.center': `⭐ Center: {center}`,
    'detail.currentTier': `Tier Saat Ini:`,
    'detail.noTier': `— Belum Ter-tier —`,
    'detail.youtube': `Buka di YouTube`,
    'detail.youtubeAlt': `Thumbnail YouTube`,
    'toast.drag': `✅ "{title}" masuk ke Tier {tier}`,
    'toast.copyTitle': `✅ Judul lagu berhasil disalin!`,
    'toast.copyFull': `✅ (Judul - Artis) berhasil disalin!`,
    'toast.copyJp': `✅ Judul kanji berhasil disalin!`,
    'toast.copyFail': `Gagal menyalin teks.`,
    'toast.imported': `✅ Data tierlist berhasil di-import!`,
    'toast.invalidJson': `❌ File JSON tidak valid.`,
    'toast.exportLibrary': `Library html2canvas belum siap. Pastikan koneksi internet terhubung.`,
    'toast.generating': `⏳ Membuat...`,
    'toast.exportFailed': `Gagal mengekspor gambar: {error}`,
    'confirm.clear': `Kosongkan semua lagu dari tierlist?`,
    'confirm.reset': `Reset semua data tierlist?`,
    'tier.empty': `kosong`,
    'grid.tierPlaceholder': `— Tier —`
  }
};

function t(key, vars={}){
  const table=I18N[currentLang]||I18N.en;
  const text=table[key] ?? I18N.en[key] ?? key;
  return String(text).replace(/\{(\w+)\}/g, (_, name) => vars[name] !== undefined ? String(vars[name]) : `{${name}}`);
}

function getStoredLang(){
  try { return localStorage.getItem(LANG_KEY)==='id' ? 'id' : 'en'; } catch { return 'en'; }
}
function getStoredTheme(){
  try { return localStorage.getItem(THEME_KEY)==='dark' ? 'dark' : 'light'; } catch { return 'light'; }
}
function applyStaticTranslations(){
  document.querySelectorAll('[data-i18n]').forEach(el=>{
    el.textContent=t(el.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>{
    el.placeholder=t(el.dataset.i18nPlaceholder);
  });
  document.querySelectorAll('[data-i18n-title]').forEach(el=>{
    el.title=t(el.dataset.i18nTitle);
  });
  document.querySelectorAll('[data-i18n-aria-label]').forEach(el=>{
    el.setAttribute('aria-label', t(el.dataset.i18nAriaLabel));
  });
}
function syncLangButtons(){
  document.querySelectorAll('[data-lang]').forEach(btn=>{
    const active=btn.dataset.lang===currentLang;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', String(active));
  });
}
function setLanguage(lang, persist=true){
  if(lang!=='en' && lang!=='id') return;
  currentLang=lang;
  if(persist){ try { localStorage.setItem(LANG_KEY, lang); } catch {} }
  document.documentElement.lang=lang;
  applyStaticTranslations();
  syncLangButtons();
  if(songs.length){
    renderSeriesNav();
    renderGrid();
    renderTierlist();
    document.title=t('meta.title', {count:songs.length});
  }
  refreshOpenModals();
}
function setTheme(dark, persist=true){
  currentTheme=dark ? 'dark' : 'light';
  document.documentElement.classList.toggle('dark', !!dark);
  if(persist){ try { localStorage.setItem(THEME_KEY, currentTheme); } catch {} }
  const input=document.getElementById('dark-toggle');
  if(input){
    input.checked=!!dark;
    input.setAttribute('aria-checked', String(!!dark));
  }
}
function initPreferences(){
  currentLang=getStoredLang();
  currentTheme=getStoredTheme();
  document.documentElement.lang=currentLang;
  document.documentElement.classList.toggle('dark', currentTheme==='dark');
  applyStaticTranslations();
  syncLangButtons();
  const input=document.getElementById('dark-toggle');
  if(input){
    input.checked=currentTheme==='dark';
    input.setAttribute('aria-checked', String(currentTheme==='dark'));
  }
}
function updateGridTitle(){
  const el=document.getElementById('grid-title');
  if(el) el.textContent=t(currentView==='albums' ? 'grid.albums' : 'grid.songs');
}
function displayAlbum(album){
  return album==='(tanpa album)' ? t('album.none') : album;
}
function seriesLabel(series){
  return series==='Lain' ? t('series.other') : series;
}
function refreshOpenModals(){
  const albumModal=document.getElementById('modal');
  if(albumModal && !albumModal.classList.contains('hidden') && activeAlbum){
    openModal(activeAlbum);
  }
  const detailModal=document.getElementById('song-detail-modal');
  if(detailModal && !detailModal.classList.contains('hidden') && activeSongId!=null){
    openSongDetailModal(activeSongId);
  }
}
const TIERS=['S','A','B','C','D','F'];
const TIER_COLOR={S:'var(--s)',A:'var(--a)',B:'var(--b)',C:'var(--c)',D:'var(--d)',F:'var(--f)'};
const SERIES_KEYWORDS={
 'µs':['µ','printemps','bibi','lily white','\u00b5','muse','a-rise','stray','honoka','kotori','umi','hanayo','rin','maki','nico','eli','nozomi'],
 'Aqours':['aqours','cyazalea','yyy','wai wai wai','cyaron','azalea','guilty','saint aqours','saint snow','chika','riko','kanan','dia','yoshiko','yohane','hanamaru','mari','ruby','you','gkss','aiscream'],
 'Niji':['nijigasaki','nijigaku','qu4rtz','diverdiva','azuna','a・zu','r3birth','yuuki','setsuna','ayumu','kasumi','shizuku','karin','ai','kanata','emma','rina','shioriko','shiroko','mia','lanzhu','yu','a.l.a.n'],
 'Liella':['liella','catchu','kaleidoscope','kaleidoscore','5yncri5e','syncrise','sunny','kanon','keke','chisato','sumire','ren','kinako','mei','shiki','natsumi','wien','margarete','tomari'],
 'Musical':['school idol musical','musical','tsubakisakuhana','takizakura','sim supports','rurika','yuzuha','yukino','hikaru','maya','anzu','misuzu','toa','rena','sayaka harukaze','madoka','kyoka'],
 'Hasunosora':['hasu','hasunosora','nyaovenus','cerise','dollchestra','mira-cra','miracra','mira cra','edel','giiter','kaho','sayaka murano','kozue','tsuzuri','tsuziri','rurino','megumi','megu','kahomegu','gelato','ginko','kosuzu','hime','ceras','ruri&to','prince'],
 'Ikizurai-Bu':['ikizurai','ikizurai-bu','ikizuraibu','call me','kidokumachi','kobumi otome','chaki','plumina','mi×nori=tea','minori','sh1on','polka','mai','azabu','akira','hanabi','yukuri','aurora','midori','miracle','noriko','shion','chofu']
};

const SERIES_PATTERNS = Object.entries(SERIES_KEYWORDS).map(([s, keys]) => ({
  series: s,
  regexes: keys.map(k => {
    const escKey = k.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return new RegExp(`(?:^|[^a-z0-9])${escKey}(?:$|[^a-z0-9])`, 'i');
  })
}));

function seriesOf(artist){
  if (!artist) return 'Lain';
  const a = artist.toLowerCase();
  // The 2026 AiScReam lineup is filed under Nijigasaki, while the
  // original unit belongs to Sunshine.
  if (a.includes('aiscream (2026)')) return 'Niji';
  for (const { series, regexes } of SERIES_PATTERNS) {
    if (regexes.some(r => r.test(a))) return series;
  }
  return 'Lain';
}
function slug(s){return (s||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').slice(0,120).replace(/^-+|-+$/g,'')||'n/a';}
function fileTag(s){return (s==='µs'?'mus':s==='Musical'?'lain':s==='Ikizurai-Bu'?'lain':s||'lain').toLowerCase();}
function coverPath(series,album){return `covers/${fileTag(series)}--${slug(album)}.webp`;}
function songCover(id,series,album){
  const m=meta[String(id)]||{};
  if(m.cover){
    if(m.cover.startsWith('http://')||m.cover.startsWith('https://')||m.cover.startsWith('covers/')){
      return m.cover;
    }
    return `covers/${m.cover}`;
  }
  return coverPath(series,album);
}

function ytVideoId(url){const m=/(?:v=|youtu\.be\/|\/embed\/)([A-Za-z0-9_-]{6,})/.exec(url||'');return m?m[1]:'';}

async function load(){
  initPreferences();
  [songs, meta] = await Promise.all([
    fetch('songs.json').then(r=>r.json()),
    fetch('metadata.json').then(r=>r.json())
  ]);
  buildAlbums();
  setupEvents();
  renderSeriesNav();
  renderGrid();
  renderTierlist();
  document.title = t('meta.title', {count:songs.length});
  const songCount = document.getElementById('song-count');
  if (songCount) songCount.textContent = songs.length;
}

function buildAlbums(){
  albums={};
  songMap={};
  for(const s of songs){
    songMap[s.id] = s;
    const m=meta[String(s.id)]||{};
    const album=m.album || m.collectionName || '(tanpa album)';
    const series=seriesOf(s.artist);
    const key=series+'||'+album;
    if(!albums[key]){
      albums[key]={series,album,art:m.art||'',cover:m.cover||'',songs:[],ids:[]};
    } else if(!albums[key].cover && m.cover){
      albums[key].cover=m.cover;
    }
    albums[key].songs.push({id:s.id,title:s.title,artist:s.artist,center:s.center,date:s.date});
    albums[key].ids.push(s.id);
  }
}

function setupEvents(){
  const searchInput = document.getElementById('search-input');
  if(searchInput){
    searchInput.addEventListener('input', e=>{
      searchQuery = e.target.value.trim().toLowerCase();
      renderGrid();
    });
  }

  const btnAlbums = document.getElementById('btn-view-albums');
  const btnSongs = document.getElementById('btn-view-songs');
  if(btnAlbums && btnSongs){
    btnAlbums.onclick=()=>{
      currentView='albums';
      btnAlbums.classList.add('active');
      btnSongs.classList.remove('active');
      updateGridTitle();
      renderGrid();
    };
    btnSongs.onclick=()=>{
      currentView='songs';
      btnSongs.classList.add('active');
      btnAlbums.classList.remove('active');
      updateGridTitle();
      renderGrid();
    };
  }

  const hideToggle = document.getElementById('hide-tiered-toggle');
  if(hideToggle){
    hideToggle.checked = hideTiered;
    hideToggle.onchange = e => {
      hideTiered = e.target.checked;
      renderGrid();
    };
  }

  // Backup & Restore JSON
  document.getElementById('btn-export-json').onclick = exportJSON;
  document.getElementById('btn-import-json').onclick = () => document.getElementById('json-file-input').click();
  document.getElementById('json-file-input').onchange = e => {
    if(e.target.files && e.target.files[0]) importJSON(e.target.files[0]);
  };

  // Clear & Reset
  document.getElementById('btn-clear-tiers').onclick = () => {
    if(confirm(t('confirm.clear'))){
      localStorage.removeItem(STORE);
      renderTierlist();
      renderGrid();
    }
  };
  document.getElementById('btn-reset').onclick = () => {
    if(confirm(t('confirm.reset'))){
      localStorage.removeItem(STORE);
      renderTierlist();
      renderGrid();
    }
  };

  // Export PNG (html2canvas)
  document.getElementById('btn-export-png').onclick = exportPNG;
  document.getElementById('export-close').onclick = () => document.getElementById('export-modal').classList.add('hidden');
  document.getElementById('export-modal').addEventListener('click', e => {
    if(e.target.id==='export-modal') e.target.classList.add('hidden');
  });

  document.querySelectorAll('[data-lang]').forEach(btn=>{
    btn.onclick=()=>setLanguage(btn.dataset.lang);
  });

  const darkToggle = document.getElementById('dark-toggle');
  if(darkToggle){
    darkToggle.onchange = e => setTheme(e.target.checked);
  }

  // Setup Pointer Events Drag & Drop with Mouse Wheel Scroll support
  setupPointerDrag();
}

/* --- Pointer Events Drag & Drop with Mouse Wheel Scroll Support --- */
let currentDrag = null; // { id, sourceEl, startX, startY, isDragging, ghostEl }
let lastClientX = 0;
let lastClientY = 0;
let autoScrollAnim = null;
let justFinishedDrag = false;
let activeDropTierRow = null;

function setupPointerDrag() {
  window.addEventListener('pointermove', onPointerMove, { passive: false });
  window.addEventListener('pointerup', onPointerUp, { passive: false });
  window.addEventListener('pointercancel', onPointerUp, { passive: false });

  // Update target when scrolling with mouse wheel or page scroll during drag
  window.addEventListener('wheel', () => {
    if (currentDrag && currentDrag.isDragging) {
      updateHoverTarget(lastClientX, lastClientY);
    }
  }, { passive: true });

  window.addEventListener('scroll', () => {
    if (currentDrag && currentDrag.isDragging) {
      updateHoverTarget(lastClientX, lastClientY);
    }
  }, { passive: true });

  // Prevent accidental click (e.g. opening detail modal) immediately after dropping a drag
  window.addEventListener('click', e => {
    if (justFinishedDrag) {
      e.stopPropagation();
      e.preventDefault();
    }
  }, true);
}

function attachPointerDrag(el, songId) {
  el.addEventListener('pointerdown', e => {
    // Only primary mouse button or touch
    if (e.button !== 0 && e.pointerType === 'mouse') return;

    // Ignore interactive controls
    if (e.target.closest('select, button, input, a, .tier-card-rm')) return;

    // For touch devices, only allow dragging from drag handle or tier card to preserve native page scroll
    if (e.pointerType === 'touch' && !e.target.closest('.song-card-drag, .drag-handle, .tier-card')) {
      return;
    }

    currentDrag = {
      id: Number(songId),
      sourceEl: el,
      startX: e.clientX,
      startY: e.clientY,
      isDragging: false,
      ghostEl: null
    };
    lastClientX = e.clientX;
    lastClientY = e.clientY;
  });
}

function createGhostElement(id) {
  const s = songMap[id] || { id, title: t('song.fallback', {id}), artist: '' };
  const m = meta[String(id)] || {};
  const albumName = m.album || m.collectionName || '(tanpa album)';
  const sSeries = seriesOf(s.artist);
  const artSrc = songCover(id, sSeries, albumName);

  const ghost = document.createElement('div');
  ghost.className = 'drag-ghost';
  ghost.innerHTML = `
    <img src="${artSrc}" alt="" onerror="this.classList.add('missing-img')">
    <div class="drag-ghost-info">
      <div class="drag-ghost-title">${esc(s.title)}</div>
      <div class="drag-ghost-sub">${esc(s.artist || sSeries)}</div>
    </div>
  `;
  document.body.appendChild(ghost);
  return ghost;
}

function onPointerMove(e) {
  if (!currentDrag) return;

  lastClientX = e.clientX;
  lastClientY = e.clientY;

  if (!currentDrag.isDragging) {
    const dist = Math.hypot(e.clientX - currentDrag.startX, e.clientY - currentDrag.startY);
    if (dist > 6) {
      currentDrag.isDragging = true;
      currentDrag.ghostEl = createGhostElement(currentDrag.id);
      currentDrag.sourceEl.classList.add('is-dragging');
      document.body.classList.add('dragging-active');

      if (!autoScrollAnim) {
        autoScrollAnim = requestAnimationFrame(pointerAutoScrollLoop);
      }
    }
  }

  if (currentDrag.isDragging) {
    e.preventDefault();
    if (currentDrag.ghostEl) {
      currentDrag.ghostEl.style.left = e.clientX + 'px';
      currentDrag.ghostEl.style.top = e.clientY + 'px';
    }
    updateHoverTarget(e.clientX, e.clientY);
  }
}

function updateHoverTarget(x, y) {
  if (x == null || y == null) return;
  const el = document.elementFromPoint(x, y);
  const trow = el ? el.closest('.trow') : null;

  if (trow !== activeDropTierRow) {
    if (activeDropTierRow) {
      activeDropTierRow.classList.remove('drop-active');
    }
    activeDropTierRow = trow;
    if (activeDropTierRow) {
      activeDropTierRow.classList.add('drop-active');
    }
  }
}

function onPointerUp(e) {
  if (!currentDrag) return;

  if (currentDrag.isDragging) {
    if (e) e.preventDefault();
    const dropTarget = activeDropTierRow || (document.elementFromPoint(lastClientX, lastClientY)?.closest('.trow'));

    if (dropTarget) {
      const tier = dropTarget.querySelector('.body')?.dataset.tier;
      if (tier && TIERS.includes(tier)) {
        const sid = currentDrag.id;
        setTier(sid, tier);
        renderTierlist();
        renderGrid();
        const s = songMap[sid];
        showToast(t('toast.drag', {title:s ? s.title : t('song.fallbackSimple'), tier}));

        const modal = document.getElementById('modal');
        if (modal && !modal.classList.contains('hidden')) {
          modal.classList.add('hidden');
          activeAlbum=null;
        }
      }
    }

    // Cleanup
    if (currentDrag.ghostEl && currentDrag.ghostEl.parentNode) {
      currentDrag.ghostEl.parentNode.removeChild(currentDrag.ghostEl);
    }
    if (currentDrag.sourceEl) {
      currentDrag.sourceEl.classList.remove('is-dragging');
    }
    document.body.classList.remove('dragging-active');

    if (activeDropTierRow) {
      activeDropTierRow.classList.remove('drop-active');
      activeDropTierRow = null;
    }

    if (autoScrollAnim) {
      cancelAnimationFrame(autoScrollAnim);
      autoScrollAnim = null;
    }

    justFinishedDrag = true;
    setTimeout(() => {
      justFinishedDrag = false;
    }, 120);
  }

  currentDrag = null;
}

function pointerAutoScrollLoop() {
  if (!currentDrag || !currentDrag.isDragging) {
    autoScrollAnim = null;
    return;
  }

  const threshold = 110;
  const maxSpeed = 22;
  const viewportH = window.innerHeight;

  if (lastClientY !== null) {
    if (lastClientY >= 0 && lastClientY < threshold) {
      const speed = Math.ceil((1 - Math.max(0, lastClientY) / threshold) * maxSpeed);
      window.scrollBy(0, -speed);
      updateHoverTarget(lastClientX, lastClientY);
    } else if (viewportH - lastClientY < threshold) {
      const dist = Math.max(0, viewportH - lastClientY);
      const speed = Math.ceil((1 - dist / threshold) * maxSpeed);
      window.scrollBy(0, speed);
      updateHoverTarget(lastClientX, lastClientY);
    }
  }

  autoScrollAnim = requestAnimationFrame(pointerAutoScrollLoop);
}

function renderSeriesNav(){
  const counts={};
  Object.values(albums).forEach(a=>{counts[a.series]=(counts[a.series]||0)+a.songs.length;});
  const order=['µs','Aqours','Niji','Liella','Hasunosora','Musical','Ikizurai-Bu','Lain'];
  const nav=document.getElementById('seriesnav');
  nav.innerHTML='';
  const entries=[
    {key:'All', label:t('nav.all'), count:songs.length},
    ...order.map(series=>({key:series, label:seriesLabel(series), count:counts[series]||0}))
  ];
  entries.forEach(({key,label,count})=>{
    const b=document.createElement('button');
    b.innerHTML=`${label} <span class="c">${count}</span>`;
    if(currentSeries===key) b.classList.add('active');
    b.onclick=()=>{
      nav.querySelectorAll('button').forEach(x=>x.classList.remove('active'));
      b.classList.add('active');
      currentSeries = key;
      renderGrid();
    };
    nav.appendChild(b);
  });
  updateStats();
}

function updateStats(){
  const totalTiered = countTotalTiered();
  const stats=document.getElementById('stats');
  stats.textContent=t('stats', {
    albums:Object.keys(albums).length,
    songs:songs.length,
    tiered:totalTiered
  });
}

function countTotalTiered(){
  let count = 0;
  for(const t of TIERS){
    count += Object.keys(getStorage(t)).length;
  }
  return count;
}

function renderGrid(){
  updateGridTitle();
  if(currentView === 'songs'){
    renderSongGrid();
  } else {
    renderAlbumGrid();
  }
  updateStats();
}

function renderAlbumGrid(){
  const g=document.getElementById('grid');
  g.className='grid album-grid';
  g.innerHTML='';
  let list=Object.values(albums);
  if(currentSeries!=='All') list=list.filter(a=>a.series===currentSeries);
  if(searchQuery){
    list=list.filter(a=>a.album.toLowerCase().includes(searchQuery) || a.songs.some(s=>s.title.toLowerCase().includes(searchQuery)));
  }
  if(!list.length){g.innerHTML=`<div class="empty">${esc(t('empty.albums'))}</div>`;return;}
  list.sort((a,b)=>(a.series+b.album).localeCompare(b.series+a.album));
  for(const a of list){
    const card=document.createElement('div');card.className='card';
    const slugName=coverPath(a.series,a.album);
    const albumLabel=displayAlbum(a.album);
    card.innerHTML=`<img loading="lazy" src="${slugName}" alt="${esc(albumLabel)}" draggable="false" onerror="this.classList.add('missing-img');"><div class="cap"><span title="${esc(albumLabel)}">${esc(short(albumLabel))}</span><span class="n">${a.songs.length}</span></div>`;
    card.onclick=()=>openModal(a);
    g.appendChild(card);
  }
}

function renderSongGrid(){
  const g=document.getElementById('grid');
  g.className='grid song-grid';
  g.innerHTML='';
  let list=songs;
  if(currentSeries!=='All') list=list.filter(s=>seriesOf(s.artist)===currentSeries);

  if(hideTiered){
    list = list.filter(s => !isTiered(s.id));
  }

  if(searchQuery){
    list=list.filter(s=>{
      const m=meta[String(s.id)]||{};
      const alb=(m.album||m.collectionName||'').toLowerCase();
      return s.title.toLowerCase().includes(searchQuery) || (s.artist||'').toLowerCase().includes(searchQuery) || alb.includes(searchQuery);
    });
  }

  if(!list.length){
    g.innerHTML=`<div class="empty">${esc(t('empty.songs'))}</div>`;
    return;
  }

  for(const s of list){
    const m=meta[String(s.id)]||{};
    const albumName=m.album || m.collectionName || '(tanpa album)';
    const sSeries=seriesOf(s.artist);
    const artSrc=songCover(s.id,sSeries,albumName);
    const curTier=getTier(s.id);

    const card=document.createElement('div');
    card.className='song-card'+(curTier?' tiered':'');
    card.dataset.id=s.id;
    card.innerHTML=`
      <div class="song-card-drag" title="${esc(t('song.dragToTierlist'))}">⋮⋮</div>
      <img src="${artSrc}" alt="" draggable="false" onerror="this.classList.add('missing-img')">
      <div class="song-card-info">
        <div class="song-card-title" title="${esc(s.title)}">${esc(s.title)}</div>
        <div class="song-card-sub" title="${esc(s.artist||'')}">${esc(s.artist||'')}</div>
      </div>
      <select data-id="${s.id}">
        <option value="">${esc(t('grid.tierPlaceholder'))}</option>
        ${TIERS.map(tier=>`<option value="${tier}" ${curTier===tier?'selected':''}>${tier}</option>`).join('')}
      </select>
    `;

    attachPointerDrag(card, s.id);

    card.querySelector('select').addEventListener('change',e=>{
      e.stopPropagation();
      setTier(s.id, e.target.value);
      renderTierlist();
      renderGrid();
    });
    card.onclick=e=>{
      if(e.target.tagName.toLowerCase()==='select') return;
      openSongDetailModal(s.id);
    };

    g.appendChild(card);
  }
}

function openModal(album){
  const body=document.getElementById('modal-body');
  let art=coverPath(album.series,album.album);
  let ls=album.songs.slice(0,60).map(s=>`
    <li data-id="${s.id}" class="${isTiered(s.id)?'is-tiered-item':''}">
      <span class="drag-handle" title="${esc(t('song.dragToTier'))}">⋮⋮</span>
      <span class="song-title" title="${esc(s.title)}">${esc(s.title)}</span>
      <span class="artist">· ${esc(s.artist||'')}</span>
      <select data-id="${s.id}"><option value="">${esc(t('grid.tierPlaceholder'))}</option>${TIERS.map(tier=>`<option value="${tier}" ${getTier(s.id)===tier?'selected':''}>${tier}</option>`).join('')}</select>
    </li>
  `).join('') + (album.songs.length>60?`<div class="empty">${esc(t('album.moreSongs', {count:album.songs.length-60}))}</div>`:'');

  body.innerHTML=`
    <div class="alb"><img src="${art}" draggable="false" onerror="this.classList.add('missing-img')"><div class="meta">
      <h3>${esc(displayAlbum(album.album))} <mark class="tag">${seriesLabel(album.series)}</mark></h3>
      <div class="album-meta-sub">${esc(t('album.count', {count:album.songs.length}))}</div>
      <div class="album-batch-rank">
        <span>${esc(t('album.setAll'))}</span>
        <select id="batch-album-select">
          <option value="">${esc(t('album.choose'))}</option>
          ${TIERS.map(tier=>`<option value="${tier}">${esc(t('album.tierOption', {tier}))}</option>`).join('')}
          <option value="CLEAR">${esc(t('album.clearOption'))}</option>
        </select>
      </div>
    </div></div>
    <ul class="songlist">${ls}</ul>`;
  activeAlbum=album;
  document.getElementById('modal').classList.remove('hidden');

  const batchSel = document.getElementById('batch-album-select');
  if(batchSel){
    batchSel.onchange = e => {
      const val = e.target.value;
      if(!val) return;
      const targetTier = val === 'CLEAR' ? '' : val;
      album.songs.forEach(s => setTier(s.id, targetTier));
      renderTierlist();
      renderGrid();
      openModal(album);
      showToast(val === 'CLEAR'
        ? t('album.cleared', {album:displayAlbum(album.album)})
        : t('album.setAllToast', {tier:val}));
    };
  }

  body.querySelectorAll('li[data-id]').forEach(li=>{
    const id=+li.dataset.id;
    attachPointerDrag(li, id);
    li.onclick=e=>{
      if(e.target.tagName.toLowerCase()==='select') return;
      openSongDetailModal(id);
    };
  });

  body.querySelectorAll('select[data-id]').forEach(sel=>sel.onchange=e=>{
    setTier(+sel.dataset.id, e.target.value);
    renderTierlist();
    renderGrid();
  });
}
document.getElementById('modal-close').onclick=()=>{activeAlbum=null;document.getElementById('modal').classList.add('hidden');};
document.getElementById('modal').addEventListener('click',e=>{if(e.target.id==='modal'){activeAlbum=null;e.target.classList.add('hidden');}});

/* --- Song Detail Modal & Toast --- */
function openSongDetailModal(id){
  const s = songMap[id];
  if(!s) return;
  const m = meta[String(id)] || {};
  const albumName = m.album || m.collectionName || '(tanpa album)';
  const sSeries = seriesOf(s.artist);
  const artSrc = songCover(id, sSeries, albumName);
  const curTier = getTier(id);

  const body = document.getElementById('song-detail-body');
  const ytV = ytVideoId(m.yt);
  body.innerHTML = `
    <div class="song-detail-header">
      <img src="${artSrc}" alt="" class="song-detail-img" onerror="this.classList.add('missing-img')">
      <div class="song-detail-meta">
        <h2>${esc(s.title)}</h2>
        ${m.jp_title ? `<p class="song-detail-jp">🇯🇵 <span class="jp-text">${esc(m.jp_title)}</span> <button class="ghost" id="btn-copy-jp" title="${esc(t('detail.copyJpTitle'))}">${esc(t('detail.copyJp'))}</button></p>` : ''}
        <p class="song-detail-artist">🎤 ${esc(s.artist || 'Love Live!')}</p>
        <p class="song-detail-album">💿 Album: <strong>${esc(displayAlbum(albumName))}</strong> <mark class="tag">${seriesLabel(sSeries)}</mark></p>
        ${s.date ? `<p class="song-detail-extra">${esc(t('detail.released', {date:s.date}))}</p>` : ''}
        ${s.center ? `<p class="song-detail-extra">${esc(t('detail.center', {center:s.center}))}</p>` : ''}
        
        <div class="song-detail-tier-select">
          <label>${esc(t('detail.currentTier'))}</label>
          <select id="detail-tier-select">
            <option value="">${esc(t('detail.noTier'))}</option>
            ${TIERS.map(tier => `<option value="${tier}" ${curTier === tier ? 'selected' : ''}>${esc(t('album.tierOption', {tier}))}</option>`).join('')}
          </select>
        </div>
      </div>
    </div>
    ${ytV ? `
    <a class="song-detail-yt" href="${esc(m.yt)}" target="_blank" rel="noopener" title="${esc(t('detail.youtube'))}">
      <img src="https://i.ytimg.com/vi/${ytV}/maxresdefault.jpg" alt="${esc(t('detail.youtubeAlt'))}" loading="lazy"
           onerror="if(!this.dataset.f){this.dataset.f=1;this.src='https://i.ytimg.com/vi/${ytV}/hqdefault.jpg'}else{this.classList.add('missing-img')}">
      <span class="song-detail-yt-play">▶</span>
      <span class="song-detail-yt-badge">YouTube</span>
    </a>` : ''}
    <div class="song-detail-actions">
      <button id="btn-copy-title" class="btn-primary-lg">${esc(t('detail.copyTitle'))}</button>
      <button id="btn-copy-full" class="ghost">${esc(t('detail.copyFull'))}</button>
    </div>
  `;

  activeSongId=id;
  document.getElementById('song-detail-modal').classList.remove('hidden');

  document.getElementById('detail-tier-select').onchange = e => {
    setTier(id, e.target.value);
    renderTierlist();
    renderGrid();
  };

  document.getElementById('btn-copy-title').onclick = () => {
    copyToClipboard(s.title, t('toast.copyTitle'));
  };

  document.getElementById('btn-copy-full').onclick = () => {
    copyToClipboard(`${s.title} - ${s.artist || ''}`, t('toast.copyFull'));
  };

  const jpBtn = document.getElementById('btn-copy-jp');
  if (jpBtn && m.jp_title) {
    jpBtn.onclick = () => copyToClipboard(m.jp_title, t('toast.copyJp'));
  }
}

document.getElementById('song-detail-close').onclick = () => {
  activeSongId=null;
  document.getElementById('song-detail-modal').classList.add('hidden');
};
document.getElementById('song-detail-modal').addEventListener('click', e => {
  if(e.target.id==='song-detail-modal'){
    activeSongId=null;
    e.target.classList.add('hidden');
  }
});

function copyToClipboard(text, successMsg){
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(() => {
      showToast(successMsg);
    }).catch(() => {
      fallbackCopy(text, successMsg);
    });
  } else {
    fallbackCopy(text, successMsg);
  }
}

function fallbackCopy(text, successMsg){
  const textArea = document.createElement("textarea");
  textArea.value = text;
  document.body.appendChild(textArea);
  textArea.select();
  try {
    document.execCommand('copy');
    showToast(successMsg);
  } catch (err) {
    alert(t('toast.copyFail'));
  }
  document.body.removeChild(textArea);
}

function showToast(msg){
  const t = document.getElementById('toast');
  if(!t) return;
  t.textContent = msg;
  t.classList.remove('hidden');
  t.classList.add('show');
  setTimeout(() => {
    t.classList.remove('show');
    t.classList.add('hidden');
  }, 2400);
}

/* --- tiers & storage --- */
function loadStore(){
  try {
    return JSON.parse(localStorage.getItem(STORE)) || {};
  } catch {
    return {};
  }
}

function getStorage(t){
  const data = loadStore()[t] || {};
  delete data['NaN'];
  delete data['undefined'];
  delete data['null'];
  return data;
}

function isTiered(id){
  return getTier(id) !== '';
}

function getTier(id){
  const store = loadStore();
  for(const t of TIERS){
    const tierObj = store[t];
    if(tierObj && (tierObj[id] || tierObj[String(id)])) return t;
  }
  return '';
}

function setTier(id, t){
  const numId = Number(id);
  if(!numId || isNaN(numId)) return;
  const store = loadStore();
  for(const tier of TIERS){
    if(!store[tier]) store[tier] = {};
    delete store[tier][numId];
    delete store[tier][String(numId)];
    delete store[tier]['NaN'];
    delete store[tier]['undefined'];
    delete store[tier]['null'];
  }
  if(t && TIERS.includes(t)){
    store[t][numId] = true;
  }
  localStorage.setItem(STORE, JSON.stringify(store));
}

function renderTierlist(){
  const box=document.getElementById('tiers');
  box.innerHTML='';
  const remmap={};for(const tier of TIERS){remmap[tier]={...getStorage(tier)};}
  for(const tier of TIERS){
    const ids=Object.keys(remmap[tier]).map(Number).filter(id=>!isNaN(id)&&id>0);
    const row=document.createElement('div');row.className='trow';
    row.innerHTML=`<div class="lab ${tier.toLowerCase()}">${tier}</div><div class="body" data-tier="${tier}"></div>`;
    const body=row.querySelector('.body');
    ids.forEach(id=>{
      const s=songMap[id]||{id, title:t('song.fallback', {id}), artist:''};
      const m=meta[String(id)]||{};
      const albumName=m.album || m.collectionName || '(tanpa album)';
      const sSeries=seriesOf(s.artist);
      const artSrc=songCover(id, sSeries, albumName);

      const c=document.createElement('div');c.className='tier-card';
      c.dataset.id=id;c.dataset.tier=tier;
      c.title=`${s.title} (${s.artist||''})`;
      c.innerHTML=`
        <img class="tier-card-img" src="${artSrc}" alt="${esc(s.title)}" draggable="false" onerror="this.classList.add('missing-img');">
        <div class="tier-card-label">${esc(s.title)}</div>
        <button class="tier-card-rm" title="${esc(t('song.removeFromTier'))}">&times;</button>
      `;
      attachPointerDrag(c, id);
      c.querySelector('.tier-card-rm').onclick=e=>{
        e.stopPropagation();
        setTier(id,'');
        renderTierlist();
        renderGrid();
      };
      c.onclick=e=>{
        if(e.target.classList.contains('tier-card-rm')) return;
        openSongDetailModal(id);
      };
      body.appendChild(c);
    });
    if(!ids.length)body.innerHTML=`<span class="empty" style="padding:0;font-size:11px">${esc(t('tier.empty'))}</span>`;
    box.appendChild(row);
  }
}

/* --- JSON Export / Import --- */
function exportJSON(){
  const data = localStorage.getItem(STORE) || '{}';
  const blob = new Blob([data], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `love_live_tierlist_${new Date().toISOString().slice(0,10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

function importJSON(file){
  const reader = new FileReader();
  reader.onload = e => {
    try {
      const parsed = JSON.parse(e.target.result);
      if(typeof parsed === 'object'){
        localStorage.setItem(STORE, JSON.stringify(parsed));
        renderTierlist();
        renderGrid();
        alert(t('toast.imported'));
      }
    } catch(err){
      alert(t('toast.invalidJson'));
    }
  };
  reader.readAsText(file);
}

/* --- PNG Export (html2canvas) --- */
function exportPNG(){
  if(typeof html2canvas === 'undefined'){
    alert(t('toast.exportLibrary'));
    return;
  }
  const tierSection = document.getElementById('tierlist');
  const btn = document.getElementById('btn-export-png');
  btn.textContent = t('toast.generating');
  btn.disabled = true;

  html2canvas(tierSection, {
    scale: 2,
    useCORS: true,
    backgroundColor: getComputedStyle(document.body).getPropertyValue('--bg') || '#f4f1f8'
  }).then(canvas => {
    btn.textContent = t('actions.exportPng');
    btn.disabled = false;
    const container = document.getElementById('export-preview-container');
    container.innerHTML = '';
    const img = document.createElement('img');
    img.src = canvas.toDataURL('image/png');
    container.appendChild(img);

    const downloadLink = document.getElementById('download-png-link');
    downloadLink.href = img.src;
    document.getElementById('export-modal').classList.remove('hidden');
  }).catch(err => {
    btn.textContent = t('actions.exportPng');
    btn.disabled = false;
    alert(t('toast.exportFailed', {error:err.message}));
  });
}

function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function short(s){return s.length>26?s.slice(0,25)+'…':s;}
load();