// Builds the Trends tab from window.TRENDS (defined in trends.js).
// Load order in index.html: data.js -> trends.js -> trends-render.js -> main inline <script>.
(function () {
  const panel = document.getElementById('tab-trends');
  if (!panel) return;

  const T = window.TRENDS;
  if (!T || !Array.isArray(T.sections)) {
    // trends.js missing or has a syntax error: fail visibly instead of showing an empty tab
    panel.innerHTML = '<p class="no-results">Trends data failed to load — check trends.js.</p>';
    return;
  }

  // Escape everything that comes from data before it goes into innerHTML
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // Tile color name -> [rgb used for the tint, CSS var used for the label]
  const TILE = {
    cyan:   ['6,182,212',  'var(--accent)'],
    purple: ['139,92,246', 'var(--accent2)'],
    green:  ['63,185,80',  'var(--green)'],
    amber:  ['245,158,11', 'var(--accent3)'],
  };

  const tile = t => {
    const [rgb, color] = TILE[t.color] || TILE.cyan;
    return `<div style="background:linear-gradient(135deg,rgba(${rgb},0.08),var(--bg2));border:1px solid rgba(${rgb},0.25);border-radius:var(--radius);padding:16px;text-align:center;">
      <div style="font-size:24px;margin-bottom:6px;">${esc(t.icon)}</div>
      <div style="font-family:var(--font-mono);font-size:10px;color:${color};text-transform:uppercase;letter-spacing:.1em;">${esc(t.label)}</div>
      <div style="font-size:12px;color:var(--text2);margin-top:4px;">${esc(t.text)}</div>
    </div>`;
  };

  const link = (l, i) =>
    `<a href="${esc(l.url)}" target="_blank" rel="noopener" class="res-link"${i === 0 ? ' style="margin-left:auto;"' : ''}>${esc(l.text)}</a>`;

  const card = c => `<div class="trend-card ${esc(c.kind || '')}">
    <div class="trend-header"><div class="trend-icon">${esc(c.icon)}</div><div>
      <div class="trend-title">${esc(c.title)}</div>${c.sub ? `<div class="trend-sub">${esc(c.sub)}</div>` : ''}
    </div></div>
    <div class="trend-desc">${esc(c.desc)}</div>
    <div class="trend-footer">
      ${(c.stats || []).map(s => `<span class="trend-stat${s.hot ? ' hot' : ''}">${esc(s.text)}</span>`).join('')}
      ${(c.links || []).map(link).join('')}
    </div>
  </div>`;

  const linkItem = l => `<div class="link-list-item"><a href="${esc(l.url)}" target="_blank" rel="noopener"><span class="lli-icon">${esc(l.icon)}</span> ${esc(l.text)}</a><span class="lli-meta">${esc(l.meta)}</span></div>`;

  const section = (s, i) => `${i > 0 ? '<hr class="section-divider" />' : ''}
    <div class="section-head${s.color ? ' ' + esc(s.color) : ''}"><h2>${esc(s.title)}</h2>${s.tag ? `<span class="section-tag">${esc(s.tag)}</span>` : ''}</div>
    ${s.type === 'links'
      ? `<div class="link-list">${s.items.map(linkItem).join('')}</div>`
      : `<div class="card-grid">${s.items.map(card).join('')}</div>`}`;

  panel.innerHTML =
    `<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin-bottom:24px;">${(T.tiles || []).map(tile).join('')}</div>` +
    T.sections.map(section).join('');

  // "Trends refreshed" note on the What's New tab (element added by migrate_index.py)
  const note = document.getElementById('trends-updated');
  if (note && T.updatedLabel) note.textContent = '// Trends refreshed ' + T.updatedLabel;

  // Make trend cards searchable. SEARCH_DATA is a top-level const from data.js:
  // not on window, but visible by name to later classic scripts, and a const array can still be pushed to.
  if (typeof SEARCH_DATA !== 'undefined' && Array.isArray(SEARCH_DATA)) {
    T.sections.forEach(s => s.items.forEach(it => {
      const url = it.url || (it.links && it.links[0] && it.links[0].url);
      if (!url) return; // search results are links, so skip items with nowhere to go
      SEARCH_DATA.push({
        section: 'Trends',
        title: it.title || it.text,
        desc: it.sub || it.desc || it.meta || '',
        url,
        tags: ['trends', it.kind || 'link'],
      });
    }));
  }
})();
