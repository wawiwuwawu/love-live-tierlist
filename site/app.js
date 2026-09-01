/* Love Live! All-Series Song Tierlist */
const STORE='ll_tiers_v1';
let songs=[], meta={}, albums={};
const TIERS=['S','A','B','C','D','F'];
const TIER_COLOR={S:'var(--s)',A:'var(--a)',B:'var(--b)',C:'var(--c)',D:'var(--d)',F:'var(--f)'};
const SERIES_KEYWORDS={
 'µs':['µ','printemps','bibi','lily white','\u00b5','muse','a-rise','stray'],
 'Aqours':['aqours','cyaron','azalea','guilty','saint aqours'],
 'Niji':['nijigasaki','qu4rtz','diverdiva','azuna','a・zu','r3birth','yuuki','setsuna','ayumu'],
 'Liella':['liella','catchu','kaleidoscope','5yncri5e','sunny','kanon','chisato'],
 'Hasunosora':['hasu','nyaovenus','cerise','dollchestra','edel','giiter']
};
function seriesOf(artist){
  const a=(artist||'').toLowerCase();
  if(!a) return 'Lain';
  for(const [s,keys] of Object.entries(SERIES_KEYWORDS)){
    if(keys.some(k=>a.includes(k.toLowerCase()))) return s;
  }
  return 'Lain';
}
function slug(s){return (s||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,60)||'n/a';}
function fileTag(s){return (s==='µs'?'mus':s||'lain').toLowerCase();}
function coverPath(series,album){return `covers/${fileTag(series)}--${slug(album)}.webp`;}

async function load(){
  [songs, meta] = await Promise.all([fetch('songs.json').then(r=>r.json()), fetch('metadata.json').then(r=>r.json())]);
  buildAlbums();
  renderSeriesNav();
  renderGrid('All');
  renderTierlist();
  document.title = `Love Live! Song Tierlist (${songs.length} lagu)`;
}
function buildAlbums(){
  albums={};
  for(const s of songs){
    const m=meta[String(s.id)]||{};
    const album=m.album || m.collectionName || '(tanpa album)';
    const series=seriesOf(s.artist);
    const key=series+'||'+album;
    if(!albums[key]) albums[key]={series,album,art:m.art||'',songs:[],ids:[]};
    albums[key].songs.push({id:s.id,title:s.title,artist:s.artist,center:s.center,date:s.date});
    albums[key].ids.push(s.id);
  }
}
function renderSeriesNav(){
  const counts={};
  Object.values(albums).forEach(a=>{counts[a.series]=(counts[a.series]||0)+a.songs.length;});
  const order=['µs','Aqours','Niji','Liella','Hasunosora','Lain'];
  const nav=document.getElementById('seriesnav');
  nav.innerHTML='';
  [['All',songs.length],...order.map(s=>[s,counts[s]||0])].forEach(([label,n],i)=>{
    const b=document.createElement('button');
    b.innerHTML=label==='All'?`Semua <span class="c">${n}</span>`:`${label} <span class="c">${n}</span>`;
    if(i===0) b.classList.add('active');
    b.onclick=()=>{nav.querySelectorAll('button').forEach(x=>x.classList.remove('active'));b.classList.add('active');renderGrid(label);};
    nav.appendChild(b);
  });
  const t=document.getElementById('stats');
  t.textContent=`${Object.keys(albums).length} album · ${songs.length} lagu · 6 seri · ${TIERS.length} tier`;
}
function renderGrid(series){
  const g=document.getElementById('grid');
  g.innerHTML='';
  let list=Object.values(albums);
  if(series!=='All') list=list.filter(a=>a.series===series);
  if(!list.length){g.innerHTML='<div class="empty">Belum ada album di seri ini.</div>';return;}
  list.sort((a,b)=>(a.series+b.album).localeCompare(b.series+a.album));
  for(const a of list){
    const card=document.createElement('div');card.className='card';
    const slugName=coverPath(a.series,a.album);
    card.innerHTML=`<img loading="lazy" src="${slugName}" alt="${esc(a.album)}" onerror="this.classList.add('missing-img');"><div class="cap"><span title="${esc(a.album)}">${esc(short(a.album))}</span><span class="n">${a.songs.length}</span></div>`;
    card.onclick=()=>openModal(a);
    g.appendChild(card);
  }
}
function openModal(album){
  const body=document.getElementById('modal-body');
  let art=coverPath(album.series,album.album);
  let ls=album.songs.slice(0,60).map(s=>`<li><span title="${esc(s.title)}">${esc(s.title)}</span><span class="artist">· ${esc(s.artist||'')}</span><select data-id="${s.id}">${TIERS.map(t=>`<option value="${t}" ${getTier(s.id)===t?'selected':''}>${t}</option>`).join('')}<option value="">—</option></select></li>`).join('')
    + (album.songs.length>60?`<div class="empty">+${album.songs.length-60} lagu lagi…</div>`:'');
  body.innerHTML=`
    <div class="alb"><img src="${art}" onerror="this.classList.add('missing-img')"><div class="meta">
      <h3>${esc(album.album)} <mark class="tag">${album.series}</mark></h3>
      ${album.songs.length} lagu</div></div>
    <ul class="songlist">${ls}</ul>`;
  document.getElementById('modal').classList.remove('hidden');
  body.querySelectorAll('select').forEach(sel=>sel.onchange=e=>{
    setTier(+sel.dataset.id, e.target.value); renderTierlist();
  });
}
document.getElementById('modal-close').onclick=()=>document.getElementById('modal').classList.add('hidden');
document.getElementById('modal').addEventListener('click',e=>{if(e.target.id==='modal')e.target.classList.add('hidden');});

/* --- tiers --- */
function getStorage(t){return JSON.parse(localStorage.getItem(STORE)||'{}')[t]||{};}
function getTier(id){for(const t of TIERS)if(getStorage(t)[id])return t;return '';}
function setTier(id,t){
  const st=JSON.parse(localStorage.getItem(STORE)||'{}');const s={};
  for(const x of TIERS){s[x]=getStorage(x);delete s[x][id];}
  if(t&&TIERS.includes(t))s[t][id]=true;
  localStorage.setItem(STORE,JSON.stringify(s));
}
function renderTierlist(){
  const box=document.getElementById('tiers');
  const titleMap={};songs.forEach(s=>titleMap[s.id]=s.title);
  box.innerHTML='';
  const remmap={};for(const t of TIERS){remmap[t]={...getStorage(t)};}
  for(const t of TIERS){
    const ids=Object.keys(remmap[t]).map(Number);
    const row=document.createElement('div');row.className='trow';
    row.innerHTML=`<div class="lab ${t.toLowerCase()}">${t}</div><div class="body" data-tier="${t}"></div>`;
    const body=row.querySelector('.body');
    ids.forEach(id=>{
      const c=document.createElement('span');c.className='chip';c.draggable=true;
      c.innerHTML=`${esc(titleMap[id]||id)}<span class="rm" title="lepas">&times;</span>`;
      c.dataset.id=id;c.dataset.tier=t;
      c.addEventListener('dragstart',e=>{e.dataTransfer.setData('text/plain',id);c.classList.add('dragging');});
      c.addEventListener('dragend',()=>c.classList.remove('dragging'));
      c.querySelector('.rm').onclick=()=>{setTier(id,'');renderTierlist();};
      body.appendChild(c);
    });
    if(!ids.length)body.innerHTML='<span class="empty" style="padding:0;font-size:11px">kosong</span>';
    row.addEventListener('dragover',e=>{e.preventDefault();row.classList.add('drop-active');});
    row.addEventListener('dragleave',()=>row.classList.remove('drop-active'));
    row.addEventListener('drop',e=>{
      e.preventDefault();row.classList.remove('drop-active');
      const id=e.dataTransfer.getData('text/plain');
      if(id)setTier(+id,t);
      renderTierlist();
    });
    box.appendChild(row);
  }
}
document.getElementById('btn-reset').onclick=()=>{if(confirm('Reset semua tier?')){localStorage.removeItem(STORE);renderTierlist();}};
document.getElementById('dark-toggle').onchange=e=>{document.body.classList.toggle('dark',e.target.checked)};

function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function short(s){return s.length>26?s.slice(0,25)+'…':s;}
load();