/* Love Live! All-Series Song Tierlist */
const STORE='ll_tiers_v1';
let songs=[], meta={}, albums={}, songMap={};
let currentSeries='All', currentView='songs', searchQuery='', hideTiered=true;
const TIERS=['S','A','B','C','D','F'];
const TIER_COLOR={S:'var(--s)',A:'var(--a)',B:'var(--b)',C:'var(--c)',D:'var(--d)',F:'var(--f)'};
const SERIES_KEYWORDS={
 'µs':['µ','printemps','bibi','lily white','\u00b5','muse','a-rise','stray','honoka','kotori','umi','hanayo','rin','maki','nico','eli','nozomi'],
 'Aqours':['aqours','cyazalea','yyy','wai wai wai','cyaron','azalea','guilty','saint aqours','saint snow','chika','riko','kanan','dia','yoshiko','yohane','hanamaru','mari','ruby','you','gkss'],
 'Niji':['nijigasaki','nijigaku','qu4rtz','diverdiva','azuna','a・zu','r3birth','yuuki','setsuna','ayumu','kasumi','shizuku','karin','ai','kanata','emma','rina','shioriko','shiroko','mia','lanzhu','yu'],
 'Liella':['liella','catchu','kaleidoscope','kaleidoscore','5yncri5e','syncrise','sunny','kanon','keke','chisato','sumire','ren','kinako','mei','shiki','natsumi','wien','margarete','tomari'],
 'Hasunosora':['hasu','hasunosora','nyaovenus','cerise','dollchestra','mira-cra','miracra','mira cra','edel','giiter','kaho','sayaka','kozue','tsuzuri','tsuziri','rurino','megumi','megu','kahomegu','gelato','ginko','kosuzu','hime','ceras'],
 'Musical':['school idol musical','musical','tsubakisakuhana','takizakura','sim supports','rurika','yuzuha','yukino','hikaru','maya','anzu','misuzu','toa','rena','sayaka harukaze','madoka','kyoka'],
 'Ikizurai-Bu':['ikizurai','ikizurai-bu','ikizuraibu','call me','kidokumachi','kobumi otome','chaki','plumina','mi×nori=tea','minori','sh1on','polka','mai','azabu','akira','hanabi','yukuri','aurora','midori','miracle','noriko','shion','chofu']
};

function seriesOf(artist){
  const a=(artist||'').toLowerCase();
  if(!a) return 'Lain';
  for(const [s,keys] of Object.entries(SERIES_KEYWORDS)){
    if(keys.some(k=>{
      const esc=k.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
      return new RegExp(`(?:^|[^a-z0-9])${esc}(?:$|[^a-z0-9])`,'i').test(a);
    })) return s;
  }
  return 'Lain';
}
function slug(s){return (s||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').slice(0,60).replace(/^-+|-+$/g,'')||'n/a';}
function fileTag(s){return (s==='µs'?'mus':s==='Musical'?'lain':s==='Ikizurai-Bu'?'lain':s||'lain').toLowerCase();}
function coverPath(series,album){return `covers/${fileTag(series)}--${slug(album)}.webp`;}

async function load(){
  [songs, meta] = await Promise.all([
    fetch('songs.json').then(r=>r.json()),
    fetch('metadata.json').then(r=>r.json())
  ]);
  buildAlbums();
  setupEvents();
  renderSeriesNav();
  renderGrid();
  renderTierlist();
  document.title = `Love Live! Song Tierlist (${songs.length} lagu)`;
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
    if(!albums[key]) albums[key]={series,album,art:m.art||'',songs:[],ids:[]};
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
      document.getElementById('grid-title').textContent = 'Daftar Album & Single';
      renderGrid();
    };
    btnSongs.onclick=()=>{
      currentView='songs';
      btnSongs.classList.add('active');
      btnAlbums.classList.remove('active');
      document.getElementById('grid-title').textContent = 'Pilih & Drag Lagu Ke Tierlist';
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
    if(confirm('Kosongkan semua lagu dari tierlist?')){
      localStorage.removeItem(STORE);
      renderTierlist();
      renderGrid();
    }
  };
  document.getElementById('btn-reset').onclick = () => {
    if(confirm('Reset semua data tierlist?')){
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

  document.getElementById('dark-toggle').onchange = e => {
    document.body.classList.toggle('dark', e.target.checked);
  };
}

function renderSeriesNav(){
  const counts={};
  Object.values(albums).forEach(a=>{counts[a.series]=(counts[a.series]||0)+a.songs.length;});
  const order=['µs','Aqours','Niji','Liella','Hasunosora','Musical','Ikizurai-Bu','Lain'];
  const nav=document.getElementById('seriesnav');
  nav.innerHTML='';
  [['All',songs.length],...order.map(s=>[s,counts[s]||0])].forEach(([label,n],i)=>{
    const b=document.createElement('button');
    b.innerHTML=label==='All'?`Semua <span class="c">${n}</span>`:`${label} <span class="c">${n}</span>`;
    if(i===0) b.classList.add('active');
    b.onclick=()=>{
      nav.querySelectorAll('button').forEach(x=>x.classList.remove('active'));
      b.classList.add('active');
      currentSeries = label;
      renderGrid();
    };
    nav.appendChild(b);
  });
  updateStats();
}

function updateStats(){
  const totalTiered = countTotalTiered();
  const t=document.getElementById('stats');
  t.textContent=`${Object.keys(albums).length} album · ${songs.length} lagu · ${totalTiered} ter-tier`;
}

function countTotalTiered(){
  let count = 0;
  for(const t of TIERS){
    count += Object.keys(getStorage(t)).length;
  }
  return count;
}

function renderGrid(){
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
  if(!list.length){g.innerHTML='<div class="empty">Belum ada album yang cocok.</div>';return;}
  list.sort((a,b)=>(a.series+b.album).localeCompare(b.series+a.album));
  for(const a of list){
    const card=document.createElement('div');card.className='card';
    const slugName=coverPath(a.series,a.album);
    card.innerHTML=`<img loading="lazy" src="${slugName}" alt="${esc(a.album)}" draggable="false" onerror="this.classList.add('missing-img');"><div class="cap"><span title="${esc(a.album)}">${esc(short(a.album))}</span><span class="n">${a.songs.length}</span></div>`;
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
    g.innerHTML='<div class="empty">🎉 Semua lagu telah masuk ke tierlist! (Atau tidak ada lagu yang cocok dengan pencarian).</div>';
    return;
  }

  for(const s of list){
    const m=meta[String(s.id)]||{};
    const albumName=m.album || m.collectionName || '(tanpa album)';
    const sSeries=seriesOf(s.artist);
    const artSrc=coverPath(sSeries,albumName);
    const curTier=getTier(s.id);

    const card=document.createElement('div');
    card.className='song-card'+(curTier?' tiered':'');
    card.draggable=true;
    card.dataset.id=s.id;
    card.innerHTML=`
      <div class="song-card-drag" title="Tarik ke tierlist">⋮⋮</div>
      <img src="${artSrc}" alt="" draggable="false" onerror="this.classList.add('missing-img')">
      <div class="song-card-info">
        <div class="song-card-title" title="${esc(s.title)}">${esc(s.title)}</div>
        <div class="song-card-sub" title="${esc(s.artist||'')}">${esc(s.artist||'')}</div>
      </div>
      <select data-id="${s.id}">
        <option value="">— Tier —</option>
        ${TIERS.map(t=>`<option value="${t}" ${curTier===t?'selected':''}>${t}</option>`).join('')}
      </select>
    `;

    card.addEventListener('dragstart',e=>{
      e.dataTransfer.setData('text/plain', String(s.id));
      card.classList.add('dragging');
    });
    card.addEventListener('dragend',()=>card.classList.remove('dragging'));
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
    <li draggable="true" data-id="${s.id}" class="${isTiered(s.id)?'is-tiered-item':''}">
      <span class="drag-handle" title="Tarik lagu ini ke tier">⋮⋮</span>
      <span class="song-title" title="${esc(s.title)}">${esc(s.title)}</span>
      <span class="artist">· ${esc(s.artist||'')}</span>
      <select data-id="${s.id}">${TIERS.map(t=>`<option value="${t}" ${getTier(s.id)===t?'selected':''}>${t}</option>`).join('')}<option value="">—</option></select>
    </li>
  `).join('') + (album.songs.length>60?`<div class="empty">+${album.songs.length-60} lagu lagi…</div>`:'');

  body.innerHTML=`
    <div class="alb"><img src="${art}" draggable="false" onerror="this.classList.add('missing-img')"><div class="meta">
      <h3>${esc(album.album)} <mark class="tag">${album.series}</mark></h3>
      <div class="album-meta-sub">${album.songs.length} lagu</div>
      <div class="album-batch-rank">
        <span>Set Semua Lagu ke Tier:</span>
        <select id="batch-album-select">
          <option value="">— Pilih —</option>
          ${TIERS.map(t=>`<option value="${t}">Tier ${t}</option>`).join('')}
          <option value="CLEAR">Riset (Kosongkan)</option>
        </select>
      </div>
    </div></div>
    <ul class="songlist">${ls}</ul>`;
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
      showToast(val === 'CLEAR' ? `Cleared all songs in ${album.album}` : `✅ Set semua lagu ke Tier ${val}`);
    };
  }

  body.querySelectorAll('li[draggable="true"]').forEach(li=>{
    const id=+li.dataset.id;
    li.addEventListener('dragstart',e=>{
      e.dataTransfer.setData('text/plain', String(id));
      li.classList.add('dragging');
    });
    li.addEventListener('dragend',()=>li.classList.remove('dragging'));
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
document.getElementById('modal-close').onclick=()=>document.getElementById('modal').classList.add('hidden');
document.getElementById('modal').addEventListener('click',e=>{if(e.target.id==='modal')e.target.classList.add('hidden');});

/* --- Song Detail Modal & Toast --- */
function openSongDetailModal(id){
  const s = songMap[id];
  if(!s) return;
  const m = meta[String(id)] || {};
  const albumName = m.album || m.collectionName || '(tanpa album)';
  const sSeries = seriesOf(s.artist);
  const artSrc = coverPath(sSeries, albumName);
  const curTier = getTier(id);

  const body = document.getElementById('song-detail-body');
  body.innerHTML = `
    <div class="song-detail-header">
      <img src="${artSrc}" alt="" class="song-detail-img" onerror="this.classList.add('missing-img')">
      <div class="song-detail-meta">
        <h2>${esc(s.title)}</h2>
        ${m.jp_title ? `<p class="song-detail-jp">🇯🇵 <span class="jp-text">${esc(m.jp_title)}</span> <button class="ghost" id="btn-copy-jp" title="Salin judul kanji">📋 Salin</button></p>` : ''}
        <p class="song-detail-artist">🎤 ${esc(s.artist || 'Love Live!')}</p>
        <p class="song-detail-album">💿 Album: <strong>${esc(albumName)}</strong> <mark class="tag">${sSeries}</mark></p>
        ${s.date ? `<p class="song-detail-extra">📅 Rilis: ${esc(s.date)}</p>` : ''}
        ${s.center ? `<p class="song-detail-extra">⭐ Center: ${esc(s.center)}</p>` : ''}
        
        <div class="song-detail-tier-select">
          <label>Tier Saat Ini:</label>
          <select id="detail-tier-select">
            <option value="">— Belum Ter-tier —</option>
            ${TIERS.map(t => `<option value="${t}" ${curTier === t ? 'selected' : ''}>Tier ${t}</option>`).join('')}
          </select>
        </div>
      </div>
    </div>
    <div class="song-detail-actions">
      <button id="btn-copy-title" class="btn-primary-lg">📋 Salin Judul Lagu</button>
      <button id="btn-copy-full" class="ghost">🎵 Salin (Judul - Artis)</button>
    </div>
  `;

  document.getElementById('song-detail-modal').classList.remove('hidden');

  document.getElementById('detail-tier-select').onchange = e => {
    setTier(id, e.target.value);
    renderTierlist();
    renderGrid();
  };

  document.getElementById('btn-copy-title').onclick = () => {
    copyToClipboard(s.title, '✅ Judul lagu berhasil disalin!');
  };

  document.getElementById('btn-copy-full').onclick = () => {
    copyToClipboard(`${s.title} - ${s.artist || ''}`, '✅ (Judul - Artis) berhasil disalin!');
  };

  const jpBtn = document.getElementById('btn-copy-jp');
  if (jpBtn && m.jp_title) {
    jpBtn.onclick = () => copyToClipboard(m.jp_title, '✅ Judul kanji berhasil disalin!');
  }
}

document.getElementById('song-detail-close').onclick = () => document.getElementById('song-detail-modal').classList.add('hidden');
document.getElementById('song-detail-modal').addEventListener('click', e => {
  if(e.target.id==='song-detail-modal') e.target.classList.add('hidden');
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
    alert('Gagal menyalin teks.');
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
function getStorage(t){
  const data = JSON.parse(localStorage.getItem(STORE)||'{}')[t]||{};
  delete data['NaN'];
  delete data[NaN];
  delete data['undefined'];
  delete data['null'];
  return data;
}

function isTiered(id){
  return getTier(id) !== '';
}

function getTier(id){
  for(const t of TIERS) if(getStorage(t)[id]) return t;
  return '';
}

function setTier(id,t){
  const numId = Number(id);
  if(isNaN(numId) || !numId) return;
  const st=JSON.parse(localStorage.getItem(STORE)||'{}');const s={};
  for(const x of TIERS){
    s[x]=getStorage(x);
    delete s[x][numId];
    delete s[x][String(numId)];
    delete s[x]['NaN'];
    delete s[x][NaN];
  }
  if(t&&TIERS.includes(t)) s[t][numId]=true;
  localStorage.setItem(STORE,JSON.stringify(s));
}

function renderTierlist(){
  const box=document.getElementById('tiers');
  box.innerHTML='';
  const remmap={};for(const t of TIERS){remmap[t]={...getStorage(t)};}
  for(const t of TIERS){
    const ids=Object.keys(remmap[t]).map(Number).filter(id=>!isNaN(id)&&id>0);
    const row=document.createElement('div');row.className='trow';
    row.innerHTML=`<div class="lab ${t.toLowerCase()}">${t}</div><div class="body" data-tier="${t}"></div>`;
    const body=row.querySelector('.body');
    ids.forEach(id=>{
      const s=songMap[id]||{id, title:'Song #'+id, artist:''};
      const m=meta[String(id)]||{};
      const albumName=m.album || m.collectionName || '(tanpa album)';
      const sSeries=seriesOf(s.artist);
      const artSrc=coverPath(sSeries, albumName);

      const c=document.createElement('div');c.className='tier-card';c.draggable=true;
      c.dataset.id=id;c.dataset.tier=t;
      c.title=`${s.title} (${s.artist||''})`;
      c.innerHTML=`
        <img class="tier-card-img" src="${artSrc}" alt="${esc(s.title)}" draggable="false" onerror="this.classList.add('missing-img');">
        <div class="tier-card-label">${esc(s.title)}</div>
        <button class="tier-card-rm" title="Lepas dari tier">&times;</button>
      `;
      c.addEventListener('dragstart',e=>{
        e.dataTransfer.setData('text/plain', String(id));
        c.classList.add('dragging');
      });
      c.addEventListener('dragend',()=>c.classList.remove('dragging'));
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
    if(!ids.length)body.innerHTML='<span class="empty" style="padding:0;font-size:11px">kosong</span>';

    row.addEventListener('dragover',e=>{e.preventDefault();row.classList.add('drop-active');});
    row.addEventListener('dragleave',()=>row.classList.remove('drop-active'));
    row.addEventListener('drop',e=>{
      e.preventDefault();row.classList.remove('drop-active');
      const rawId=e.dataTransfer.getData('text/plain');
      const idNum=parseInt(rawId, 10);
      if(!isNaN(idNum) && idNum > 0){
        setTier(idNum,t);
        renderTierlist();
        renderGrid();
      }
    });
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
        alert('✅ Data tierlist berhasil di-import!');
      }
    } catch(err){
      alert('❌ File JSON tidak valid.');
    }
  };
  reader.readAsText(file);
}

/* --- PNG Export (html2canvas) --- */
function exportPNG(){
  if(typeof html2canvas === 'undefined'){
    alert('Library html2canvas belum siap. Pastikan koneksi internet terhubung.');
    return;
  }
  const tierSection = document.getElementById('tierlist');
  const btn = document.getElementById('btn-export-png');
  btn.textContent = '⏳ Generating...';
  btn.disabled = true;

  html2canvas(tierSection, {
    scale: 2,
    useCORS: true,
    backgroundColor: getComputedStyle(document.body).getPropertyValue('--bg') || '#14121d'
  }).then(canvas => {
    btn.textContent = '📷 Export PNG';
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
    btn.textContent = '📷 Export PNG';
    btn.disabled = false;
    alert('Gagal mengekspor gambar: ' + err.message);
  });
}

function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function short(s){return s.length>26?s.slice(0,25)+'…':s;}

load();
document.getElementById('btn-reset').onclick=()=>{if(confirm('Reset semua tier?')){localStorage.removeItem(STORE);renderTierlist();}};
document.getElementById('dark-toggle').onchange=e=>{document.body.classList.toggle('dark',e.target.checked)};

function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function short(s){return s.length>26?s.slice(0,25)+'…':s;}
load();