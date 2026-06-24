const FEED_URL = 'data/feed.json';

let allItems = [];
let activeFilter = 'all';
let activeDays = 'all';
let activeImportance = null;

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
    document.getElementById('empty').classList.remove('hidden');
    document.getElementById('empty').textContent = '피드를 불러오는 중 오류가 발생했어요.';
  }
}

function filterItems() {
  let items = [...allItems];

  // 날짜 필터
  if (activeDays !== 'all') {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - parseInt(activeDays));
    items = items.filter(i => new Date(i.date) >= cutoff);
  }

  // 중요도 필터
  if (activeImportance) {
    items = items.filter(i => i.importance === activeImportance);
  }

  // 카테고리 필터
  if (activeFilter !== 'all') {
    items = items.filter(i => i.category === activeFilter);
  }

  return items;
}

function render() {
  const feed = document.getElementById('feed');
  const empty = document.getElementById('empty');
  const items = filterItems();

  if (items.length === 0) {
    feed.innerHTML = '';
    empty.classList.remove('hidden');
    empty.textContent = '해당 조건의 항목이 없어요.';
    return;
  }

  empty.classList.add('hidden');
  feed.innerHTML = items.map(item => `
    <a class="card" href="${item.url}" target="_blank" rel="noopener">
      <div class="card-top">
        <span class="card-category">${item.category}</span>
        <span class="importance-dot ${item.importance}" title="${item.importance}"></span>
      </div>
      <div class="card-title">${item.title_ko}</div>
      <div class="card-summary">${item.summary_ko}</div>
      ${item.tags?.length ? `<div class="card-tags">${item.tags.map(t => `<span class="tag">${t}</span>`).join('')}</div>` : ''}
      <div class="card-bottom">
        <span class="card-source">${item.source}</span>
        <span class="card-date">${item.date}</span>
      </div>
    </a>
  `).join('');
}

// 날짜·중요도 필터 버튼
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    if (btn.dataset.filter !== undefined) {
      document.querySelectorAll('.filter-btn[data-filter]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeDays = btn.dataset.filter;
      activeImportance = null;
      document.querySelectorAll('.filter-btn[data-importance]').forEach(b => b.classList.remove('active'));
    } else if (btn.dataset.importance !== undefined) {
      if (btn.classList.contains('active')) {
        btn.classList.remove('active');
        activeImportance = null;
      } else {
        document.querySelectorAll('.filter-btn[data-importance]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeImportance = btn.dataset.importance;
      }
    }
    render();
  });
});

// 카테고리 필터 버튼
document.querySelectorAll('.cat-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.dataset.cat;
    render();
  });
});

loadFeed();
