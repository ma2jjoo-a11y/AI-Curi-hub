const FEED_URL = 'data/feed.json';

// 카테고리 → 이모지 / 색 (README Design Tokens)
const CATEGORIES = {
  '릴리즈':   { emoji: '🚀', color: '#1aa35a' },
  '도구':     { emoji: '🔧', color: '#c98a14' },
  'API·기술': { emoji: '📡', color: '#0e9aa7' },
  '연구':     { emoji: '📊', color: '#2f6fdb' },
  '비즈니스': { emoji: '💼', color: '#9a6b2f' },
  '한국':     { emoji: '🌏', color: '#d64545' },
  '화제':     { emoji: '🔥', color: '#e8590c' },
};
const FALLBACK = { emoji: '📰', color: '#888888' };
const CLAMP_THRESHOLD = 90; // 본문 길이 > 90자일 때만 클램프

let allItems = [];
let activeCat = 'all';       // 'all' | 카테고리명
let activeImportant = false; // 🔴 중요
let searchQuery = '';

// "🚀 릴리즈" → "릴리즈"
function catName(category) {
  if (!category) return '';
  const parts = String(category).trim().split(' ');
  return parts.length > 1 ? parts.slice(1).join(' ') : parts[0];
}
function catMeta(category) {
  return CATEGORIES[catName(category)] || FALLBACK;
}

// date(YYYY-MM-DD) → 상대 시간
function relTime(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr + 'T00:00:00');
  if (isNaN(d)) return dateStr;
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const diff = Math.round((today - d) / 86400000);
  if (diff <= 0) return '오늘';
  if (diff === 1) return '어제';
  if (diff < 7) return `${diff}일 전`;
  return dateStr.slice(5).replace('-', '/'); // MM/DD
}

function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function isImportant(item) {
  return item.important === true || item.importance === 'high';
}

const savedSet = new Set(JSON.parse(localStorage.getItem('aicuri:saved') || '[]'));

function filterItems() {
  let items = [...allItems];
  if (activeImportant) items = items.filter(isImportant);
  if (activeCat !== 'all') items = items.filter(i => catName(i.category) === activeCat);
  if (searchQuery) {
    const q = searchQuery.toLowerCase();
    items = items.filter(i =>
      [i.title_ko, i.summary_ko, i.source, ...(i.tags || [])]
        .filter(Boolean).join(' ').toLowerCase().includes(q)
    );
  }
  return items;
}

const ARROW = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="8 7 17 7 17 16"></polyline></svg>';
const BOOKMARK = '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4h12v16l-6-4-6 4z"></path></svg>';
const SHARE = '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.6" y1="13.5" x2="15.4" y2="17.5"></line><line x1="15.4" y1="6.5" x2="8.6" y2="10.5"></line></svg>';

function postHTML(item) {
  const meta = catMeta(item.category);
  const name = catName(item.category);
  const body = item.summary_ko || '';
  const original = item.original || '';            // 원문(영문) — 없으면 번역 토글 숨김
  const needsMore = body.length > CLAMP_THRESHOLD;
  const important = isImportant(item);
  const saved = savedSet.has(item.id);

  const avatarStyle =
    `background:color-mix(in srgb, ${meta.color} 18%, var(--bg));` +
    `box-shadow:inset 0 0 0 1.5px ${meta.color};`;

  const tags = (item.tags && item.tags.length)
    ? `<div class="post-tags">${item.tags.map(t => `<span class="tag">#${esc(t)}</span>`).join('')}</div>`
    : '';

  const translateBtn = original
    ? `<button class="btn-translate" data-orig="${esc(original)}" data-trans="${esc(body)}">번역 보기</button>`
    : '';

  return `
  <article class="post" data-id="${esc(item.id)}">
    <div class="avatar" style="${avatarStyle}" title="${esc(name)}">${meta.emoji}</div>
    <div class="post-content">
      <div class="post-header">
        <span class="acct">${esc(name)}</span>
        ${important ? '<span class="imp-dot" title="중요"></span>' : ''}
        <span class="meta">· ${esc(item.source)} · ${esc(relTime(item.date))}</span>
        <span class="more-menu" aria-hidden="true">···</span>
      </div>
      <h2 class="post-title">${esc(item.title_ko)}</h2>
      <p class="post-body ${needsMore ? 'clamp' : ''}">${esc(body)}</p>
      ${needsMore ? '<button class="toggle-more">더보기</button>' : ''}
      ${tags}
      <div class="post-actions">
        <a class="btn-read" href="${esc(item.url)}" target="_blank" rel="noopener">원본 읽기 ${ARROW}</a>
        ${translateBtn}
        <span class="spacer"></span>
        <button class="icon-btn bookmark ${saved ? 'on' : ''}" aria-label="북마크">${BOOKMARK}</button>
        <button class="icon-btn share" aria-label="공유">${SHARE}</button>
      </div>
    </div>
  </article>`;
}

function render() {
  const feed = document.getElementById('feed');
  const empty = document.getElementById('empty');
  const footer = document.getElementById('list-footer');
  const items = filterItems();

  if (items.length === 0) {
    feed.innerHTML = '';
    empty.classList.remove('hidden');
    empty.textContent = '해당 조건의 항목이 없어요.';
    footer.classList.add('hidden');
    return;
  }
  empty.classList.add('hidden');
  footer.classList.remove('hidden');
  feed.innerHTML = items.map(postHTML).join('');
}

// ── 피드 내 인터랙션 (이벤트 위임) ──
document.getElementById('feed').addEventListener('click', (e) => {
  const moreBtn = e.target.closest('.toggle-more');
  if (moreBtn) {
    const body = moreBtn.previousElementSibling;
    const clamped = body.classList.toggle('clamp');
    moreBtn.textContent = clamped ? '더보기' : '접기';
    return;
  }
  const transBtn = e.target.closest('.btn-translate');
  if (transBtn) {
    const body = transBtn.closest('.post-content').querySelector('.post-body');
    const showingTrans = transBtn.textContent === '번역 보기';
    body.textContent = showingTrans ? transBtn.dataset.orig : transBtn.dataset.trans;
    transBtn.textContent = showingTrans ? '원문 보기' : '번역 보기';
    return;
  }
  const bm = e.target.closest('.bookmark');
  if (bm) {
    const id = bm.closest('.post').dataset.id;
    if (savedSet.has(id)) { savedSet.delete(id); bm.classList.remove('on'); }
    else { savedSet.add(id); bm.classList.add('on'); }
    localStorage.setItem('aicuri:saved', JSON.stringify([...savedSet]));
    return;
  }
  const sh = e.target.closest('.share');
  if (sh) {
    const post = sh.closest('.post');
    const title = post.querySelector('.post-title').textContent;
    const url = post.querySelector('.btn-read').href;
    if (navigator.share) {
      navigator.share({ title, url }).catch(() => {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(() => {
        sh.classList.add('on');
        setTimeout(() => sh.classList.remove('on'), 900);
      });
    }
  }
});

// ── 필터칩 ──
document.getElementById('filters').addEventListener('click', (e) => {
  const chip = e.target.closest('.chip');
  if (!chip) return;
  document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
  chip.classList.add('active');
  if (chip.dataset.imp) {
    activeImportant = true;
    activeCat = 'all';
  } else {
    activeImportant = false;
    activeCat = chip.dataset.cat;
  }
  render();
});

// ── 검색 토글 ──
const searchBtn = document.getElementById('search-btn');
const searchRow = document.getElementById('search-row');
const searchInput = document.getElementById('search-input');
searchBtn.addEventListener('click', () => {
  const open = searchRow.classList.toggle('hidden') === false;
  searchBtn.setAttribute('aria-expanded', String(open));
  if (open) { searchInput.focus(); }
  else { searchInput.value = ''; searchQuery = ''; render(); }
});
searchInput.addEventListener('input', () => {
  searchQuery = searchInput.value.trim();
  render();
});

async function loadFeed() {
  try {
    const res = await fetch(FEED_URL);
    const data = await res.json();
    allItems = data.items || [];
    if (data.last_updated) {
      const d = new Date(data.last_updated);
      document.getElementById('last-updated').textContent =
        `마지막 업데이트: ${d.toLocaleDateString('ko-KR')} ${d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}`;
    }
    render();
  } catch (e) {
    const empty = document.getElementById('empty');
    empty.classList.remove('hidden');
    empty.textContent = '피드를 불러오는 중 오류가 발생했어요.';
    document.getElementById('list-footer').classList.add('hidden');
  }
}

loadFeed();
