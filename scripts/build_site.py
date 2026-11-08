#!/usr/bin/env python3
"""Generate the public ontology reference from the six authoritative modules."""
from collections import Counter, defaultdict
from hashlib import sha256
from html import escape as esc
import json
import math
from pathlib import Path
import re
import shutil

from rdflib import BNode, Graph, Literal, RDF, RDFS, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, SKOS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
REPO = 'https://github.com/Tao-AI-group/agent-o-health'
MODULES = {
    'core': ('System & runtime', 'Agents, models, components, workflows and execution.'),
    'doc': ('Documentation & provenance', 'Documents, versions, licenses and lineage.'),
    'eval': ('Evaluation', 'Studies, datasets, metrics, results and failures.'),
    'gov': ('Governance', 'Policies, risks, human review and controls.'),
    'health': ('Clinical context', 'Intended use, populations, health data and interoperability.'),
    'report': ('Reporting assessment', 'Publications, requirements, evidence and completeness.'),
}
NS = {m: f'https://w3id.org/agent-o/{"reporting" if m == "report" else m}#' for m in MODULES}
TYPES = {OWL.Class: 'Class', OWL.ObjectProperty: 'Object property',
         OWL.DatatypeProperty: 'Datatype property', OWL.AnnotationProperty: 'Annotation property',
         OWL.NamedIndividual: 'Individual'}
CHARACTERISTICS = {OWL.FunctionalProperty: 'Functional', OWL.InverseFunctionalProperty: 'Inverse functional',
                   OWL.TransitiveProperty: 'Transitive', OWL.SymmetricProperty: 'Symmetric',
                   OWL.AsymmetricProperty: 'Asymmetric', OWL.ReflexiveProperty: 'Reflexive',
                   OWL.IrreflexiveProperty: 'Irreflexive'}
G = Graph()
sources = {}
for module in MODULES:
    path = ROOT / f'ontology/modules/agento-{module}.ttl'
    G.parse(path, format='turtle')
    sources[str(path.relative_to(ROOT))] = sha256(path.read_bytes()).hexdigest()
for module, ns in NS.items():
    G.bind(module, ns, replace=True)


def compact(value):
    for m, ns in NS.items():
        if str(value).startswith(ns):
            return f'{m}:{str(value)[len(ns):]}'
    return G.namespace_manager.normalizeUri(value) if isinstance(value, URIRef) else str(value)


TERMS = {}
for subject, kind in G.subject_objects(RDF.type):
    if isinstance(subject, URIRef) and kind in TYPES and any(str(subject).startswith(n) for n in NS.values()):
        TERMS[subject] = TYPES[kind]


def module_of(term):
    return next(m for m, ns in NS.items() if str(term).startswith(ns))


def local(term):
    return compact(term).split(':', 1)[1]


def term_path(term):
    return 'terms/' + compact(term).replace(':', '-') + '.html'


def deprecated(term):
    return bool(G.value(term, OWL.deprecated))


def definition(term):
    return str(G.value(term, SKOS.definition) or G.value(term, RDFS.comment) or 'No definition is recorded in this module.')


def first_sentence(text):
    match = re.match(r'(.+?[.;])(\s|$)', text)
    return match.group(1).rstrip(';') + ('' if match.group(1).endswith('.') else '.') if match else text


def link(term, prefix='', short=False):
    if term in TERMS:
        text = local(term) if short else compact(term)
        extra = ' deprecated' if deprecated(term) else ''
        return (f'<a class="t {module_of(term)}{extra}" href="{prefix}{term_path(term)}" '
                f'title="{esc(first_sentence(definition(term)), quote=True)}">{esc(text)}</a>')
    return f'<a class="ext" href="{esc(str(term), quote=True)}">{esc(compact(term))}</a>'


def chip(m, prefix=''):
    return f'<a class="chip {m}" href="{prefix}modules/{m}.html">{m}</a>'


# ---------------------------------------------------------------- OWL expressions

def expression(term, prefix=''):
    """Generic expansion of any RDF node (used for the raw statement tables)."""
    if isinstance(term, URIRef):
        return link(term, prefix)
    if isinstance(term, Literal):
        suffix = f' @{term.language}' if term.language else (f' ({compact(term.datatype)})' if term.datatype else '')
        return esc(str(term) + suffix)
    readable = manchester(term, prefix)
    if readable is not None:
        return readable
    if G.value(term, RDF.first) is not None:
        return '(' + ', '.join(expression(v, prefix) for v in Collection(G, term)) + ')'
    return '[' + '; '.join(f'{expression(p, prefix)} {expression(v, prefix)}' for p, v in sorted(G.predicate_objects(term), key=lambda x: str(x))) + ']'


def kw(word):
    return f' <span class="kw">{word}</span> '


def manchester(term, prefix='', nested=False):
    """Render a class expression in Manchester-like syntax, as Protégé does. Returns None if unknown."""
    if isinstance(term, URIRef):
        return link(term, prefix)
    if isinstance(term, Literal):
        return esc(str(term))
    wrap = (lambda s: f'({s})') if nested else (lambda s: s)
    for predicate, word in [(OWL.unionOf, 'or'), (OWL.intersectionOf, 'and')]:
        head = G.value(term, predicate)
        if head is not None:
            return wrap(kw(word).join(manchester(v, prefix, True) or expression(v, prefix) for v in Collection(G, head)))
    head = G.value(term, OWL.oneOf)
    if head is not None:
        return '{' + ', '.join(expression(v, prefix) for v in Collection(G, head)) + '}'
    if G.value(term, OWL.complementOf) is not None:
        return kw('not').strip() + ' ' + manchester(G.value(term, OWL.complementOf), prefix, True)
    prop = G.value(term, OWL.onProperty)
    if prop is not None:
        p = expression(prop, prefix)
        for predicate, word in [(OWL.someValuesFrom, 'some'), (OWL.allValuesFrom, 'only'), (OWL.hasValue, 'value')]:
            value = G.value(term, predicate)
            if value is not None:
                return wrap(p + kw(word) + (manchester(value, prefix, True) or expression(value, prefix)))
        for word, plain, qualified in [('min', OWL.minCardinality, OWL.minQualifiedCardinality),
                                       ('max', OWL.maxCardinality, OWL.maxQualifiedCardinality),
                                       ('exactly', OWL.cardinality, OWL.qualifiedCardinality)]:
            value = G.value(term, qualified) or G.value(term, plain)
            if value is not None:
                filler = G.value(term, OWL.onClass) or G.value(term, OWL.onDataRange)
                return wrap(p + kw(word) + esc(str(value)) + (' ' + manchester(filler, prefix, True) if filler is not None else ''))
    return None


def members(expr):
    """Named classes covered by a domain/range expression (the class itself, or members of a union)."""
    if isinstance(expr, URIRef):
        return [expr]
    head = G.value(expr, OWL.unionOf)
    if head is not None:
        return [c for v in Collection(G, head) for c in members(v)]
    return []


def joined(values, prefix=''):
    values = sorted(values, key=str)
    if not values:
        return '<span class="none">—</span>'
    return kw('and').join(manchester(v, prefix) or expression(v, prefix) for v in values)


# ---------------------------------------------------------------- schema indexes

CLASSES = sorted((t for t, k in TERMS.items() if k == 'Class'), key=lambda t: compact(t).lower())
PROPERTIES = sorted((t for t, k in TERMS.items() if k in {'Object property', 'Datatype property'}), key=lambda t: compact(t).lower())
PARENTS = {c: sorted((o for o in G.objects(c, RDFS.subClassOf) if o in TERMS), key=str) for c in CLASSES}
CHILDREN = defaultdict(list)
for c, ps in PARENTS.items():
    for p in ps:
        CHILDREN[p].append(c)
BY_DOMAIN, BY_RANGE = defaultdict(list), defaultdict(list)
for p in PROPERTIES:
    for d in G.objects(p, RDFS.domain):
        for c in members(d):
            BY_DOMAIN[c].append(p)
    for r in G.objects(p, RDFS.range):
        for c in members(r):
            BY_RANGE[c].append(p)


def ancestors(c):
    seen, queue = [], list(PARENTS.get(c, []))
    while queue:
        a = queue.pop(0)
        if a not in seen and a != c:
            seen.append(a)
            queue.extend(PARENTS.get(a, []))
    return seen


def breadcrumb(c, prefix):
    chain, current = [], c
    while PARENTS.get(current) and len(chain) < 12:
        current = PARENTS[current][0]
        if current in chain:
            break
        chain.append(current)
    if not chain:
        return ''
    return '<nav class="crumbs" aria-label="Superclasses">' + ' <span>›</span> '.join(link(a, prefix) for a in reversed(chain)) + f' <span>›</span> <b>{esc(local(c))}</b></nav>'


def property_rows(props, prefix, column):
    rows = []
    for p in sorted(set(props), key=lambda t: compact(t).lower()):
        other = G.objects(p, RDFS.range if column == 'range' else RDFS.domain)
        rows.append(f'<tr><td>{link(p, prefix)}</td><td>{joined(other, prefix)}</td></tr>')
    return ''.join(rows)


def prop_table(head, body):
    return f'<table class="props"><thead><tr><th>{head[0]}</th><th>{head[1]}</th></tr></thead><tbody>{body}</tbody></table>'


def raw_statements(term, prefix):
    predicates = sorted(G.predicate_objects(term), key=lambda pv: (str(pv[0]), str(pv[1])))
    rows = ''.join(f'<tr><th>{expression(p, prefix)}</th><td>{expression(v, prefix)}</td></tr>' for p, v in predicates)
    incoming = sorted([(s, p) for s, p in G.subject_predicates(term) if s in TERMS], key=lambda sp: (str(sp[0]), str(sp[1])))
    refs = ''.join(f'<tr><th>{link(s, prefix)}</th><td>{expression(p, prefix)} this term</td></tr>' for s, p in incoming)
    body = f'<table class="raw"><tbody>{rows}</tbody></table>'
    if refs:
        body += f'<h4>Statements in other terms that mention it</h4><table class="raw"><tbody>{refs}</tbody></table>'
    return f'<details class="raw-block"><summary>All asserted statements</summary><p class="note">Direct assertions from the Turtle source. Nothing inferred.</p>{body}</details>'


# ---------------------------------------------------------------- page shell

def page(path, title, body, active=''):
    prefix = '../' * path.count('/')
    nav = [('index.html', 'Overview'), ('modules.html', 'Modules'), ('explore.html', 'Graph'),
           ('terms.html', 'Terms'), ('example.html', 'Example'), ('questions.html', 'Questions')]
    navigation = ''.join('<a ' + ('aria-current="page"' if name == active else '') + f' href="{prefix}{href}">{name}</a>' for href, name in nav)
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · AGENT-O</title><meta name="description" content="AGENT-O: an ontology for health AI agent systems. Classes, properties, hierarchy and examples.">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/style.css">
<script src="{prefix}assets/site.js" defer></script></head><body>
<a class="skip" href="#main">Skip to content</a><header><div class="bar"><a class="brand" href="{prefix}index.html">AGENT-O</a>
<nav aria-label="Main navigation">{navigation}<a class="gh" href="{REPO}">GitHub</a></nav></div></header>
<main id="main">{body}</main><footer><span>AGENT-O · Tao AI Group · Ontology CC BY 4.0 · Code MIT</span><span><a href="{prefix}downloads/source-manifest.json">Source manifest</a> · <a href="{REPO}/issues/new/choose">Suggest a change</a></span></footer></body></html>'''
    destination = OUT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding='utf-8')


def term_table(terms, prefix=''):
    rows = []
    for term in sorted(terms, key=lambda t: compact(t).lower()):
        badge = ' <span class="badge">deprecated</span>' if deprecated(term) else ''
        text = definition(term)
        rows.append(f'<tr data-search="{esc((compact(term) + " " + text).lower(), quote=True)}" data-module="{module_of(term)}" data-kind="{TERMS[term]}">'
                    f'<td>{link(term, prefix)}{badge}</td><td class="kind">{TERMS[term]}</td><td class="def" title="{esc(text, quote=True)}">{esc(first_sentence(text))}</td></tr>')
    return '<div class="table-wrap"><table class="index"><thead><tr><th>Term</th><th class="kind">Kind</th><th>Definition</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'


# ---------------------------------------------------------------- module map (home page)

def graph_edges():
    edges = []
    for s, o in G.subject_objects(RDFS.subClassOf):
        if s in TERMS and o in TERMS:
            edges.append({'source': compact(s), 'target': compact(o), 'label': 'is-a', 'kind': 'subclass', 'url': term_path(s)})
    # Preserve domain/range expressions as expressions; do not turn union members into asserted edges.
    for p in G.subjects(RDF.type, OWL.ObjectProperty):
        for domain in G.objects(p, RDFS.domain):
            for range_ in G.objects(p, RDFS.range):
                if domain in TERMS and range_ in TERMS:
                    edges.append({'source': compact(domain), 'target': compact(range_), 'label': compact(p), 'kind': 'property', 'url': term_path(p)})
    return edges


def module_map(active):
    """Six modules as nodes; lines count direct cross-module links (subclass + named domain/range)."""
    pairs = Counter()
    for e in graph_edges():
        a, b = e['source'].split(':')[0], e['target'].split(':')[0]
        if a != b:
            pairs[tuple(sorted((a, b)))] += 1
    width, height, cx, cy, radius = 880, 470, 440, 235, 185
    others = [m for m in MODULES if m != 'core']
    pos = {'core': (cx, cy)}
    for i, m in enumerate(others):
        angle = -math.pi / 2 + i * 2 * math.pi / len(others)
        pos[m] = (cx + radius * 1.75 * math.cos(angle), cy + radius * math.sin(angle))
    top = max(pairs.values()) if pairs else 1
    lines, labels = [], []
    for (a, b), n in sorted(pairs.items(), key=lambda x: x[1]):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        lines.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke-width="{1 + 7 * n / top:.1f}"/>')
        t = 0.5 if 'core' not in (a, b) else 0.58
        lx, ly = (x1 + (x2 - x1) * t, y1 + (y2 - y1) * t) if a == 'core' else (x2 + (x1 - x2) * t, y2 + (y1 - y2) * t)
        labels.append(f'<g class="count"><rect x="{lx - 15:.0f}" y="{ly - 10:.0f}" width="30" height="20" rx="10"/><text x="{lx:.0f}" y="{ly + 4:.0f}">{n}</text></g>')
    nodes = []
    for m, (x, y) in pos.items():
        classes = sum(1 for t in active if module_of(t) == m and TERMS[t] == 'Class')
        w = 196
        nodes.append(f'<a href="modules/{m}.html" class="{m}"><rect x="{x - w / 2:.0f}" y="{y - 38:.0f}" width="{w}" height="76" rx="10"/>'
                     f'<text class="p" x="{x:.0f}" y="{y - 10:.0f}">{m}:</text><text class="n" x="{x:.0f}" y="{y + 10:.0f}">{esc(MODULES[m][0])}</text>'
                     f'<text class="c" x="{x:.0f}" y="{y + 27:.0f}">{classes} classes</text></a>')
    return (f'<svg class="module-map" viewBox="0 0 {width} {height}" role="img" aria-label="The six AGENT-O modules and the number of direct links between them">'
            f'<g class="links">{"".join(lines)}</g>{"".join(labels)}{"".join(nodes)}</svg>')


def key_classes(m, active, n=5):
    degree = Counter()
    for e in graph_edges():
        degree[e['source']] += 1
        degree[e['target']] += 1
    ranked = sorted((t for t in active if module_of(t) == m and TERMS[t] == 'Class'), key=lambda t: (-degree[compact(t)], compact(t)))
    return ranked[:n]


# ---------------------------------------------------------------- pages

def build_home(active, counts):
    cards = []
    for m, (title, desc) in MODULES.items():
        n_cls = sum(1 for t in active if module_of(t) == m and TERMS[t] == 'Class')
        n_prop = sum(1 for t in active if module_of(t) == m and TERMS[t] != 'Class')
        keys = ' '.join(link(t, short=True) for t in key_classes(m, active))
        cards.append(f'<article class="mod {m}"><h3><a href="modules/{m}.html">{title}</a> <code>{m}:</code></h3><p>{desc}</p>'
                     f'<p class="keys">{keys}</p><p class="meta">{n_cls} classes · {n_prop} properties</p></article>')
    page('index.html', 'Ontology for health AI agent systems', f'''
<section class="intro"><h1>AGENT-O</h1>
<p class="lead">An OWL ontology for describing health AI agent systems: what they are made of, how they are evaluated and governed, and how they are reported.</p>
<p class="meta">{counts['Class']} classes · {counts['Object property']} object properties · {counts['Datatype property']} datatype properties · 6 modules</p>
<p class="actions"><a class="button" href="modules.html">Browse the modules</a><a class="button ghost" href="explore.html">Open the graph</a><a class="button ghost" href="{REPO}">Source on GitHub</a></p></section>
<section><h2>Six modules</h2><p class="note">Numbers on the lines count direct links between modules (subclass axioms and object properties with a named domain and range). Click a module to see its class tree.</p>
{module_map(active)}
<div class="mods">{''.join(cards)}</div></section>
<section><h2>Core relationships</h2><p class="note">A hand-picked view of 23 classes. Solid arrow: object property. Dashed arrow: subclass. <a href="assets/overview-notes.md">How to read it</a> · <a href="assets/agent-o_engineer_overview.pdf">PDF</a></p>
<a class="figure" href="assets/agent-o_engineer_overview.svg"><img src="assets/agent-o_engineer_overview.svg" alt="Selected AGENT-O class relationships grouped into system architecture, evaluation, governance, reporting assessment and intended clinical use." width="1600" height="1280" loading="lazy"></a></section>
<section class="next"><a href="example.html"><b>Worked example</b><span>A medication-safety agent described with AGENT-O.</span></a><a href="questions.html"><b>Competency questions</b><span>12 questions the ontology must answer, with SPARQL.</span></a><a href="terms.html"><b>All terms</b><span>Search every class and property.</span></a></section>''', 'Overview')


def build_modules(active):
    rows = []
    for m, (title, desc) in MODULES.items():
        c = Counter(TERMS[t] for t in active if module_of(t) == m)
        rows.append(f'<tr><td>{chip(m)}</td><td><a href="modules/{m}.html">{title}</a><div class="note">{desc}</div></td>'
                    f'<td class="num">{c["Class"]}</td><td class="num">{c["Object property"]}</td><td class="num">{c["Datatype property"]}</td></tr>')
    page('modules.html', 'Modules', '<h1>Modules</h1><p class="lead">Each module has its own namespace. Classes and properties link across modules freely.</p>'
         '<div class="table-wrap"><table class="modtable"><thead><tr><th>Prefix</th><th>Module</th><th class="num">Classes</th><th class="num">Object props</th><th class="num">Datatype props</th></tr></thead><tbody>'
         + ''.join(rows) + '</tbody></table></div>'
         f'<p class="note">Not counted here: <a href="{REPO}/tree/main/ontology/profiles">application profiles</a>, <a href="{REPO}/tree/main/ontology/alignments">external alignments</a> and <a href="{REPO}/tree/main/shapes">SHACL shapes</a>.</p>', 'Modules')
    for m, (title, desc) in MODULES.items():
        build_module_page(m, title, desc, active)


def tree_item(c, m, prefix, path=()):
    badge = ' <span class="badge">deprecated</span>' if deprecated(c) else ''
    outside = [p for p in PARENTS[c] if module_of(p) != m] if not path else []
    tag = ''.join(f' <span class="from">⊂ {link(p, prefix)}</span>' for p in outside)
    kids = sorted((k for k in CHILDREN[c] if module_of(k) == m and k not in path), key=lambda t: compact(t).lower())
    sub = '<ul>' + ''.join(tree_item(k, m, prefix, path + (c,)) for k in kids) + '</ul>' if kids else ''
    return f'<li>{link(c, prefix, short=True)}{badge}{tag}{sub}</li>'


def build_module_page(m, title, desc, active):
    prefix = '../'
    mine = [t for t in TERMS if module_of(t) == m]
    classes = [t for t in CLASSES if module_of(t) == m]
    roots = [c for c in classes if not any(module_of(p) == m for p in PARENTS[c])]
    # Roots with children first, so the real hierarchy is visible before flat lists.
    roots.sort(key=lambda c: (not CHILDREN[c], compact(c).lower()))
    tree = '<ul class="tree">' + ''.join(tree_item(c, m, prefix) for c in roots) + '</ul>'
    obj = [p for p in PROPERTIES if module_of(p) == m and TERMS[p] == 'Object property']
    dat = [p for p in PROPERTIES if module_of(p) == m and TERMS[p] == 'Datatype property']

    def ptable(props, last):
        rows = ''.join(f'<tr><td>{joined(G.objects(p, RDFS.domain), prefix)}</td><td>{link(p, prefix)}{" <span class=badge>deprecated</span>" if deprecated(p) else ""}</td><td>{joined(G.objects(p, RDFS.range), prefix)}</td></tr>' for p in props)
        return f'<div class="table-wrap"><table class="triples"><thead><tr><th>Domain</th><th>Property</th><th>{last}</th></tr></thead><tbody>{rows}</tbody></table></div>'

    other = [t for t in mine if TERMS[t] in {'Annotation property', 'Individual'}]
    extra = ('<section><h2>Other terms</h2><p class="inline-list">' + ' '.join(f'{link(t, prefix)} <span class="kind">{TERMS[t]}</span>' for t in sorted(other, key=str)) + '</p></section>') if other else ''
    counts = Counter(TERMS[t] for t in mine if t in active)
    body = (f'<p class="crumbs"><a href="../modules.html">Modules</a> <span>›</span> {m}</p>'
            f'<h1 class="mod-title {m}">{title} <code>{m}:</code></h1><p class="lead">{desc}</p>'
            f'<p class="meta">{counts["Class"]} classes · {counts["Object property"]} object properties · {counts["Datatype property"]} datatype properties · <code>{NS[m]}</code></p>'
            f'<p class="actions"><a class="button ghost" href="../explore.html?module={m}">Open in graph</a><a class="button ghost" href="../downloads/ontology/modules/agento-{m}.ttl" download>Download Turtle</a></p>'
            f'<section><h2>Class hierarchy</h2><p class="note">Indented classes are subclasses. <span class="from">⊂ X</span> marks a parent defined in another module. Hover a name for its definition.</p>{tree}</section>'
            f'<section><h2>Object properties</h2><p class="note">Read each row as a sentence: <em>Domain</em> → <em>property</em> → <em>Range</em>.</p>{ptable(obj, "Range")}</section>'
            + (f'<section><h2>Datatype properties</h2>{ptable(dat, "Value type")}</section>' if dat else '') + extra)
    page(f'modules/{m}.html', title, body, 'Modules')


def build_term(term, kind):
    prefix = '../'
    m = module_of(term)
    feedback = REPO + '/issues/new?template=ontology-feedback.yml&title=' + compact(term).replace(':', '%3A')
    badge = ' <span class="badge">deprecated</span>' if deprecated(term) else ''
    head = (f'<p class="crumbs"><a href="../modules/{m}.html">{MODULES[m][0]}</a> <span>·</span> {kind}{badge}</p>'
            f'<h1 class="term-title {m}">{esc(local(term))}</h1>')
    side = [f'<div class="iri"><span>IRI</span><a href="{term}">{term}</a></div>',
            '<ul class="links">',
            f'<li><a href="../explore.html?term={compact(term)}">View in graph</a></li>' if kind == 'Class' else '',
            f'<li><a href="{REPO}/blob/main/ontology/modules/agento-{m}.ttl">Turtle source</a></li>',
            f'<li><a href="{feedback}">Comment on this term</a></li></ul>']
    main = [breadcrumb(term, prefix) if kind == 'Class' else '', f'<p class="lead def">{esc(definition(term))}</p>']
    if kind == 'Class':
        own = BY_DOMAIN.get(term, [])
        groups = [f'<tr class="group"><th colspan="2">Defined on {esc(local(term))}</th></tr>' + property_rows(own, prefix, 'range')] if own else []
        shown = set(own)
        for a in ancestors(term):
            props = [p for p in BY_DOMAIN.get(a, []) if p not in shown]
            shown.update(props)
            if props:
                groups.append(f'<tr class="group"><th colspan="2">Inherited from {link(a, prefix)}</th></tr>' + property_rows(props, prefix, 'range'))
        if groups:
            main.append('<section><h2>Properties</h2>' + prop_table(('Property', 'Expected value'), ''.join(groups)) + '</section>')
        incoming = BY_RANGE.get(term, [])
        if incoming:
            main.append('<section><h2>Used as a value of</h2>' + prop_table(('Property', 'On class'), property_rows(incoming, prefix, 'domain')) + '</section>')
        axioms = []
        for sup in G.objects(term, RDFS.subClassOf):
            if isinstance(sup, BNode):
                axioms.append(('SubClassOf', manchester(sup, prefix) or expression(sup, prefix)))
        for eq in set(G.objects(term, OWL.equivalentClass)) | set(G.subjects(OWL.equivalentClass, term)):
            axioms.append(('EquivalentTo', manchester(eq, prefix) or expression(eq, prefix)))
        for d in sorted(set(G.objects(term, OWL.disjointWith)) | set(G.subjects(OWL.disjointWith, term)), key=str):
            axioms.append(('DisjointWith', expression(d, prefix)))
        if axioms:
            main.append('<section><h2>Logical axioms</h2><table class="axioms"><tbody>' + ''.join(f'<tr><th>{a}</th><td>{v}</td></tr>' for a, v in axioms) + '</tbody></table></section>')
        parents, kids = PARENTS[term], sorted(CHILDREN[term], key=lambda t: compact(t).lower())
        if len(parents) > 1:
            side.insert(0, '<div class="box"><h3>Subclass of</h3><ul>' + ''.join(f'<li>{link(p, prefix)}</li>' for p in parents) + '</ul></div>')
        side.insert(0, '<div class="box"><h3>Subclasses</h3>' + ('<ul>' + ''.join(f'<li>{link(k, prefix)}</li>' for k in kids) + '</ul>' if kids else '<p class="none">None</p>') + '</div>')
    elif kind in {'Object property', 'Datatype property'}:
        name = esc(local(term))
        main.append(f'<div class="signature"><div class="end">{joined(G.objects(term, RDFS.domain), prefix)}<span>domain</span></div>'
                    f'<div class="arrow">{name}</div><div class="end">{joined(G.objects(term, RDFS.range), prefix)}<span>range</span></div></div>')
        facts = []
        sup = list(G.objects(term, RDFS.subPropertyOf))
        if sup:
            facts.append(('Subproperty of', ', '.join(expression(s, prefix) for s in sup)))
        sub = sorted((s for s in G.subjects(RDFS.subPropertyOf, term) if s in TERMS), key=str)
        if sub:
            facts.append(('Subproperties', ', '.join(link(s, prefix) for s in sub)))
        inv = set(G.objects(term, OWL.inverseOf)) | set(G.subjects(OWL.inverseOf, term))
        if inv:
            facts.append(('Inverse of', ', '.join(expression(i, prefix) for i in inv)))
        eq = set(G.objects(term, OWL.equivalentProperty)) | set(G.subjects(OWL.equivalentProperty, term))
        if eq:
            facts.append(('Equivalent to', ', '.join(expression(e, prefix) for e in eq)))
        chars = [CHARACTERISTICS[t] for t in G.objects(term, RDF.type) if t in CHARACTERISTICS]
        if chars:
            facts.append(('Characteristics', ', '.join(chars)))
        if facts:
            main.append('<table class="axioms"><tbody>' + ''.join(f'<tr><th>{a}</th><td>{v}</td></tr>' for a, v in facts) + '</tbody></table>')
    see = list(G.objects(term, RDFS.seeAlso))
    if see:
        main.append('<p class="note">See also: ' + ', '.join(expression(s, prefix) for s in see) + '</p>')
    main.append(raw_statements(term, prefix))
    body = head + f'<div class="term-grid"><div>{"".join(main)}</div><aside>{"".join(side)}</aside></div>'
    page(term_path(term), compact(term), body, 'Terms')


def main():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / 'site/assets', OUT / 'assets', dirs_exist_ok=True)
    (OUT / '.nojekyll').touch()
    for folder in ['ontology', 'shapes', 'queries/competency', 'data/examples']:
        for path in sorted((ROOT / folder).rglob('*')):
            if path.suffix in {'.ttl', '.rq'}:
                target = OUT / 'downloads' / path.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
    (OUT / 'downloads/source-manifest.json').write_text(json.dumps({'authoritative_modules_sha256': sources}, indent=2) + '\n')
    active = [t for t in TERMS if not deprecated(t)]
    counts = Counter(TERMS[t] for t in active)
    build_home(active, counts)
    build_modules(active)
    for term, kind in sorted(TERMS.items()):
        build_term(term, kind)
    filters = ('<div class="filters"><input id="term-search" type="search" aria-label="Search terms" placeholder="Search names and definitions…">'
               '<select id="module-filter" aria-label="Module"><option value="">All modules</option>' + ''.join(f'<option value="{m}">{m}: {MODULES[m][0]}</option>' for m in MODULES) + '</select>'
               '<select id="kind-filter" aria-label="Kind"><option value="">All kinds</option>' + ''.join(f'<option>{k}</option>' for k in TYPES.values()) + '</select></div>')
    page('terms.html', 'All terms', '<h1>All terms</h1>' + filters + '<p id="result-count" class="note" aria-live="polite"></p>' + term_table(TERMS), 'Terms')
    build_graph()
    build_questions()
    build_example()
    print(json.dumps({'module_triples': len(G), 'active_terms': dict(counts), 'term_pages': len(TERMS), 'html_pages': len(list(OUT.rglob('*.html')))}, indent=2))


def build_graph():
    nodes = [{'id': compact(t), 'module': module_of(t), 'kind': kind, 'definition': definition(t), 'url': term_path(t)} for t, kind in sorted(TERMS.items())]
    data = {'nodes': nodes, 'edges': graph_edges()}
    (OUT / 'assets/graph.json').write_text(json.dumps(data, indent=2))
    options = ''.join(f'<option value="{esc(n["id"])}">{esc(n["id"])}</option>' for n in nodes if n['kind'] == 'Class')
    legend = ''.join(f'<span class="{m}"><i></i>{m}</span>' for m in MODULES)
    page('explore.html', 'Graph', '<h1>Graph</h1>'
         '<div class="graph-controls"><select id="graph-module" aria-label="Module"><option value="">All modules</option>' + ''.join(f'<option value="{m}">{m}: {MODULES[m][0]}</option>' for m in MODULES) + '</select>'
         '<select id="graph-focus" aria-label="Focus class">' + options + '</select>'
         '<span class="zoom"><button id="zoom-out" aria-label="Zoom out">−</button><button id="zoom-reset">100%</button><button id="zoom-in" aria-label="Zoom in">+</button></span></div>'
         '<div class="graph-layout"><div><div class="legend">' + legend + '<span class="line">── property</span><span class="line">- - ▷ subclass of</span></div>'
         '<p id="graph-status" class="note" aria-live="polite">Loading…</p><div class="graph-scroll"><svg id="graph" role="img" aria-label="Class neighborhood"></svg></div>'
         '<p class="note">Left: classes pointing to the focus. Right: classes the focus points to. Click a box to move there. Only direct subclass links and properties with a single named domain and range are drawn; unions and restrictions are on the term pages.</p></div>'
         '<aside class="box"><h3 id="focus-title">Focus</h3><p id="focus-definition"></p><p><a id="focus-link" href="terms.html">Open term page</a></p><details><summary>List view</summary><div id="graph-relations"></div></details></aside></div>'
         '<noscript><p>The graph needs JavaScript. All terms are listed in the <a href="terms.html">term index</a>.</p></noscript>', 'Graph')


def build_questions():
    rows = []
    text = (ROOT / 'queries/competency/README.md').read_text(encoding='utf-8')
    for number, filename, question in re.findall(r'\| (CQ\d+) \| `([^`]+)` \| (.*?) \|', text):
        query = (ROOT / 'queries/competency' / filename).read_text(encoding='utf-8')
        rows.append(f'<details class="cq"><summary><span class="cq-id">{number}</span>{esc(question)}</summary>'
                    f'<pre><code>{esc(query)}</code></pre><p class="note"><a href="downloads/queries/competency/{filename}" download>Download .rq</a> · '
                    f'<a href="{REPO}/issues/new?template=ontology-feedback.yml&title={number}%20feedback">Discuss</a></p></details>')
    page('questions.html', 'Competency questions', '<h1>Competency questions</h1>'
         '<p class="lead">Questions the ontology should be able to answer. Each has a SPARQL query that runs against the example data.</p>'
         '<p class="note">Run locally with <code>python scripts/run_sparql_cqs.py</code>. Reporting completeness describes what a publication covers, not clinical safety or performance. '
         f'Missing a question? <a href="{REPO}/issues/new/choose">Open an issue</a>.</p>'
         + ''.join(rows), 'Questions')


def build_example():
    graph = Graph().parse(ROOT / 'data/examples/governance_reporting_profile_example.ttl')
    ns = 'https://w3id.org/agent-o/examples/governance-reporting-profile#'
    focus = URIRef(ns + 'MedicationSafetyAgent')
    assert (focus, RDF.type, None) in graph

    def short(x):
        return esc(str(x).replace(ns, 'ex:'))

    def typed(x):
        types = [t for t in graph.objects(x, RDF.type) if t in TERMS]
        return ' '.join(link(t) for t in sorted(types, key=str))

    def entity(x):
        return f'<span class="ent"><a href="#{short(x)[3:]}">{short(x)[3:]}</a><span class="types">{typed(x)}</span></span>'

    groups = defaultdict(lambda: defaultdict(list))
    literals = []
    for p, o in sorted(graph.predicate_objects(focus), key=lambda x: (str(x[0]), str(x[1]))):
        if p == RDF.type:
            continue
        if isinstance(o, URIRef) and str(o).startswith(ns):
            groups[module_of(p) if p in TERMS else 'other'][p].append(o)
        else:
            literals.append((p, o))
    panels = []
    for m in MODULES:
        if m not in groups:
            continue
        rows = ''.join(f'<li><span class="pred">{link(p, short=True)}</span><span class="vals">{"".join(entity(o) for o in objs)}</span></li>' for p, objs in sorted(groups[m].items(), key=lambda x: str(x[0])))
        panels.append(f'<div class="panel {m}"><h3>{MODULES[m][0]}</h3><ul>{rows}</ul></div>')
    incoming = sorted((s, p) for s, p in graph.subject_predicates(focus) if isinstance(s, URIRef) and str(s).startswith(ns))
    inc = ''.join(f'<li>{entity(s)}<span class="pred">{link(p, short=True)} → this system</span></li>' for s, p in incoming)
    name = ''.join(f'<div class="lit">{link(p, short=True)}: “{esc(str(o))}”</div>' for p, o in literals)
    hub = (f'<div class="hub"><div class="center"><b>MedicationSafetyAgent</b><span class="types">{typed(focus)}</span>{name}</div>'
           f'<div class="panel incoming"><h3>Points to this system</h3><ul>{inc}</ul></div></div>')

    selected = {focus}
    selected.update(o for o in graph.objects(focus) if isinstance(o, URIRef) and str(o).startswith(ns))
    selected.update(s for s in graph.subjects(None, focus) if isinstance(s, URIRef) and str(s).startswith(ns))
    records = []
    for subject in sorted(selected):
        rows = []
        for p, o in sorted(graph.predicate_objects(subject), key=lambda x: str(x)):
            obj = link(o) if o in TERMS else (f'<a href="#{short(o)[3:]}">{short(o)}</a>' if isinstance(o, URIRef) and str(o).startswith(ns) and o in selected else short(o))
            rows.append(f'<tr><th>{expression(p)}</th><td>{obj}</td></tr>')
        records.append(f'<details class="record" id="{short(subject)[3:]}"><summary>{short(subject)} <span class="types">{typed(subject)}</span></summary><table class="raw"><tbody>{"".join(rows)}</tbody></table></details>')
    page('example.html', 'Worked example', '<h1>Worked example</h1>'
         '<p class="lead">One synthetic medication-safety agent, described with AGENT-O. Links are grouped by the module of the property used.</p>'
         '<p class="note">Synthetic data for illustration only; not a real or validated system. '
         '<a href="downloads/data/examples/governance_reporting_profile_example.ttl" download>Download the Turtle</a>.</p>'
         + hub + '<div class="panels">' + ''.join(panels) + '</div>'
         '<section><h2>The records</h2><p class="note">Every statement about the system and its direct neighbours. Click to expand.</p>' + ''.join(records) + '</section>', 'Example')


if __name__ == '__main__':
    main()
