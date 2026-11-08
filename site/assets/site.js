/* Browser-only controls; every term also has a static, linkable reference page. */
const search = document.querySelector('#term-search');
if (search) {
  const rows = [...document.querySelectorAll('tbody tr[data-search]')];
  const moduleFilter = document.querySelector('#module-filter');
  const kindFilter = document.querySelector('#kind-filter');
  function filterTerms() {
    const query = search.value.trim().toLowerCase();
    let count = 0;
    for (const row of rows) {
      row.hidden = !row.dataset.search.includes(query) ||
        Boolean(moduleFilter?.value && row.dataset.module !== moduleFilter.value) ||
        Boolean(kindFilter?.value && row.dataset.kind !== kindFilter.value);
      if (!row.hidden) count++;
    }
    document.querySelector('#result-count').textContent = `${count} of ${rows.length} terms`;
  }
  search.addEventListener('input', filterTerms);
  moduleFilter?.addEventListener('change', filterTerms);
  kindFilter?.addEventListener('change', filterTerms);
  filterTerms();
}

if (document.querySelector('#graph')) initGraph().catch(() => {
  document.querySelector('#graph-status').textContent = 'The graph could not load. Use the term index instead.';
});

async function initGraph() {
  const response = await fetch('assets/graph.json');
  if (!response.ok) throw new Error('Graph data unavailable');
  const {nodes, edges} = await response.json();
  const classes = nodes.filter(n => n.kind === 'Class');
  const byId = new Map(nodes.map(n => [n.id, n]));
  const focusSelect = document.querySelector('#graph-focus');
  const moduleSelect = document.querySelector('#graph-module');
  const svg = document.querySelector('#graph');
  const params = new URLSearchParams(location.search);
  const colors = {core:'#2f6d9c',doc:'#75569b',eval:'#1b7b70',gov:'#9a6417',health:'#a24d65',report:'#4f5aa8'};
  const tints = {core:'#eaf1f7',doc:'#f1edf6',eval:'#e8f3f1',gov:'#f6efe5',health:'#f6ecef',report:'#eceef7'};
  let focus = classes.some(n => n.id === params.get('term')) ? params.get('term') : 'core:AgentSystem';
  let zoom = 1;
  let canvasHeight = 400;
  const W = 1120, BOX = 230, ROW = 44, LEFT = 20, RIGHT = W - 20 - BOX, MID = (W - BOX) / 2;
  const NS = 'http://www.w3.org/2000/svg';
  function el(name, attrs = {}, text = '') {
    const item = document.createElementNS(NS, name);
    for (const [key,value] of Object.entries(attrs)) item.setAttribute(key, value);
    if (text) item.textContent = text;
    return item;
  }
  function fillOptions(module, preferred) {
    const options = classes.filter(n => !module || n.module === module);
    focusSelect.replaceChildren(...options.map(n => new Option(n.id, n.id)));
    focus = options.some(n => n.id === preferred) ? preferred : options[0].id;
    focusSelect.value = focus;
  }
  function updateZoom() {
    svg.setAttribute('viewBox', `${W / 2 - W / 2 / zoom} 0 ${W / zoom} ${canvasHeight / zoom}`);
    document.querySelector('#zoom-reset').textContent = `${Math.round(zoom * 100)}%`;
  }
  function move(id) {
    moduleSelect.value = '';
    fillOptions('', id);
    zoom = 1;
    draw();
  }
  function box(id, x, y, isFocus) {
    const n = byId.get(id);
    const anchor = el('a', {href: n.url});
    if (!isFocus) anchor.addEventListener('click', event => { event.preventDefault(); move(id); });
    const h = isFocus ? 56 : 32;
    anchor.append(el('rect', {x, y: y - h / 2, width: BOX, height: h, rx: 6,
      fill: isFocus ? colors[n.module] : tints[n.module], stroke: colors[n.module], 'stroke-width': isFocus ? 0 : 1}));
    const [prefix, name] = id.split(':');
    const label = el('text', {x: x + BOX / 2, y: y + (isFocus ? 6 : 4), 'text-anchor': 'middle',
      'font-family': 'system-ui,Segoe UI,Arial,sans-serif', 'font-size': isFocus ? 15 : (name.length > 30 ? 11 : 12.5),
      'font-weight': isFocus ? 650 : 500, fill: isFocus ? '#fff' : '#1d2327'});
    label.append(el('tspan', {fill: isFocus ? '#ffffffb0' : colors[n.module], 'font-size': isFocus ? 12 : 11}, prefix + ':'), el('tspan', {}, name));
    anchor.append(label, el('title', {}, n.definition));
    svg.append(anchor);
  }
  function draw() {
    const current = byId.get(focus);
    const relations = edges.filter(e => e.source === focus || e.target === focus);
    const order = e => (e.kind === 'subclass' ? 0 : 1);
    const outgoing = relations.filter(e => e.source === focus).sort((a, b) => order(a) - order(b) || a.target.localeCompare(b.target));
    const incoming = relations.filter(e => e.source !== focus).sort((a, b) => order(a) - order(b) || a.source.localeCompare(b.source));
    const rows = Math.max(outgoing.length, incoming.length, 1);
    canvasHeight = Math.max(220, rows * ROW + 60);
    const centerY = canvasHeight / 2;
    svg.setAttribute('height', canvasHeight);
    svg.replaceChildren();
    const defs = el('defs');
    for (const kind of ['property', 'subclass']) {
      const marker = el('marker', {id: kind, viewBox: '0 0 12 12', refX: 11, refY: 6, markerWidth: 8, markerHeight: 8, orient: 'auto'});
      marker.append(el('path', {d: 'M 1 1 L 11 6 L 1 11 z', fill: kind === 'subclass' ? '#fff' : '#8a959b', stroke: '#8a959b'}));
      defs.append(marker);
    }
    svg.append(defs);
    const column = (list, side) => {
      const top = centerY - (list.length - 1) * ROW / 2;
      list.forEach((edge, i) => {
        const y = top + i * ROW;
        const out = side === 'right';
        const neighbor = out ? edge.target : edge.source;
        const d = out
          ? `M ${MID + BOX} ${centerY} C ${MID + BOX + 40} ${centerY} ${RIGHT - 200} ${y} ${RIGHT - 160} ${y} L ${RIGHT} ${y}`
          : `M ${LEFT + BOX} ${y} L ${LEFT + BOX + 160} ${y} C ${MID - 40} ${y} ${MID - 40} ${centerY} ${MID} ${centerY}`;
        svg.append(el('path', {d, stroke: '#b9c2c7', fill: 'none', 'stroke-width': 1.2,
          'stroke-dasharray': edge.kind === 'subclass' ? '5 4' : 'none', 'marker-end': `url(#${edge.kind})`}));
        const label = el('a', {href: edge.url});
        const text = edge.kind === 'subclass' ? 'subclass of' : edge.label.split(':')[1];
        label.append(el('text', {x: out ? RIGHT - 8 : LEFT + BOX + 8, y: y - 5, 'text-anchor': out ? 'end' : 'start',
          'font-size': 10.5, 'font-family': 'ui-monospace,Consolas,monospace', fill: '#5f6b72'}, text));
        svg.append(label);
        box(neighbor, out ? RIGHT : LEFT, y, false);
      });
    };
    column(incoming, 'left');
    column(outgoing, 'right');
    box(focus, MID, centerY, true);
    updateZoom();
    document.querySelector('#graph-status').textContent = `${incoming.length} incoming · ${outgoing.length} outgoing`;
    document.querySelector('#focus-title').textContent = focus;
    document.querySelector('#focus-definition').textContent = current.definition;
    document.querySelector('#focus-link').href = current.url;
    const list = document.createElement('ul');
    for (const edge of relations) {
      const item = document.createElement('li');
      for (const [label, url] of [[edge.source, byId.get(edge.source).url], [edge.label, edge.url], [edge.target, byId.get(edge.target).url]]) {
        const a = document.createElement('a'); a.textContent = label; a.href = url;
        item.append(a, document.createTextNode(' '));
      }
      list.append(item);
    }
    document.querySelector('#graph-relations').replaceChildren(list);
    const next = new URL(location.href); next.search = ''; next.searchParams.set('term', focus);
    history.replaceState(null, '', next);
  }
  moduleSelect.value = Object.hasOwn(colors, params.get('module')) ? params.get('module') : '';
  fillOptions(moduleSelect.value, focus);
  focusSelect.addEventListener('change', () => { focus = focusSelect.value; zoom = 1; draw(); });
  moduleSelect.addEventListener('change', () => { fillOptions(moduleSelect.value, focus); zoom = 1; draw(); });
  document.querySelector('#zoom-in').addEventListener('click', () => { zoom = Math.min(2, zoom + .2); updateZoom(); });
  document.querySelector('#zoom-out').addEventListener('click', () => { zoom = Math.max(.6, zoom - .2); updateZoom(); });
  document.querySelector('#zoom-reset').addEventListener('click', () => { zoom = 1; updateZoom(); });
  draw();
}
