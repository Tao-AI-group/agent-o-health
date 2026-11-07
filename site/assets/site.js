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
    document.querySelector('#result-count').textContent = `${count} of ${rows.length} terms shown`;
  }
  search.addEventListener('input', filterTerms);
  moduleFilter?.addEventListener('change', filterTerms);
  kindFilter?.addEventListener('change', filterTerms);
  filterTerms();
}

if (document.querySelector('#graph')) initGraph().catch(() => {
  document.querySelector('#graph-status').textContent = 'The graph could not load. Use the complete term index to browse definitions and relationships.';
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
  const colors = {core:'#2f6d9c',doc:'#75569b',eval:'#1b7b70',gov:'#926326',health:'#a24d65',report:'#5963a5'};
  let focus = classes.some(n => n.id === params.get('term')) ? params.get('term') : 'core:AgentSystem';
  let zoom = 1;
  let canvasHeight = 600;
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
    svg.setAttribute('viewBox', `${550 - 550 / zoom} 0 ${1100 / zoom} ${canvasHeight / zoom}`);
  }
  function move(id) {
    moduleSelect.value = '';
    fillOptions('', id);
    zoom = 1;
    draw();
  }
  function draw() {
    const current = byId.get(focus);
    const relations = edges.filter(e => e.source === focus || e.target === focus);
    canvasHeight = Math.max(360, relations.length * 77 + 70);
    svg.setAttribute('height', canvasHeight);
    svg.replaceChildren();
    const defs = el('defs');
    for (const kind of ['property','subclass']) {
      const marker = el('marker',{id:kind,viewBox:'0 0 12 12',refX:11,refY:6,markerWidth:9,markerHeight:9,orient:'auto'});
      marker.append(el('path',{d:'M 1 1 L 11 6 L 1 11 z',fill:kind === 'subclass' ? '#fff' : '#62776d',stroke:'#62776d'}));
      defs.append(marker);
    }
    svg.append(defs);
    const centerY = canvasHeight / 2;
    const position = (id,x,y,isFocus=false) => {
      const n = byId.get(id);
      const group = el('g');
      const anchor = el('a',{href:n.url});
      // Neighbor activation changes the neighborhood; the text list below links to the reference.
      if (!isFocus) anchor.addEventListener('click', event => { event.preventDefault(); move(id); });
      anchor.append(el('rect',{x,y:y-25,width:270,height:50,rx:5,fill:isFocus ? colors[n.module] : '#fff',stroke:colors[n.module],'stroke-width':1.5}));
      const label = el('text',{x:x+135,y:y+5,'text-anchor':'middle','font-family':'Arial,sans-serif','font-size':id.length > 33 ? 11 : 13,fill:isFocus ? 'white' : colors[n.module]},id);
      anchor.append(label,el('title',{},n.definition));
      group.append(anchor);
      svg.append(group);
    };
    relations.forEach((edge,i) => {
      const y = 55 + i * 77;
      const outgoing = edge.source === focus;
      const neighbor = outgoing ? edge.target : edge.source;
      const targetX = outgoing ? 800 : 30;
      const d = outgoing ? `M 685 ${centerY} C 735 ${centerY} 735 ${y} 800 ${y}` : `M 300 ${y} C 365 ${y} 365 ${centerY} 415 ${centerY}`;
      svg.append(el('path',{d,stroke:'#62776d',fill:'none','stroke-width':1.4,'stroke-dasharray':edge.kind === 'subclass' ? '5 4' : 'none','marker-end':`url(#${edge.kind})`}));
      const labelX = outgoing ? 785 : 315;
      const label = el('a',{href:edge.url});
      label.append(el('text',{x:labelX,y:y-33,'text-anchor':outgoing ? 'end' : 'start','font-size':11,'font-family':'Arial,sans-serif',fill:'#304f43'},edge.label));
      svg.append(label);
      position(neighbor,targetX,y);
    });
    position(focus,415,centerY,true);
    updateZoom();
    document.querySelector('#graph-status').textContent = `${focus} · ${relations.length} direct relationships shown. Select a neighbor to explore; select a relationship label to read its definition.`;
    document.querySelector('#focus-title').textContent = focus;
    document.querySelector('#focus-definition').textContent = current.definition;
    document.querySelector('#focus-link').href = current.url;
    const list = document.createElement('ul');
    for (const edge of relations) {
      const item = document.createElement('li');
      for (const [label,url] of [[edge.source,byId.get(edge.source).url],[edge.label,edge.url],[edge.target,byId.get(edge.target).url]]) {
        const a = document.createElement('a'); a.textContent = label; a.href = url;
        item.append(a, document.createTextNode(' '));
      }
      list.append(item);
    }
    document.querySelector('#graph-relations').replaceChildren(list);
    const next = new URL(location.href); next.search = ''; next.searchParams.set('term',focus);
    history.replaceState(null,'',next);
  }
  moduleSelect.value = Object.hasOwn(colors,params.get('module')) ? params.get('module') : '';
  fillOptions(moduleSelect.value,focus);
  focusSelect.addEventListener('change',() => { focus = focusSelect.value; zoom = 1; draw(); });
  moduleSelect.addEventListener('change',() => { fillOptions(moduleSelect.value,focus); zoom = 1; draw(); });
  document.querySelector('#zoom-in').addEventListener('click',() => { zoom = Math.min(2,zoom+.2); updateZoom(); });
  document.querySelector('#zoom-out').addEventListener('click',() => { zoom = Math.max(.6,zoom-.2); updateZoom(); });
  document.querySelector('#zoom-reset').addEventListener('click',() => { zoom = 1; updateZoom(); });
  draw();
}
