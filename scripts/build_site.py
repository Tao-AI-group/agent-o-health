#!/usr/bin/env python3
"""Generate the public ontology reference from the six authoritative modules."""
from collections import Counter
from hashlib import sha256
from html import escape as esc
import json
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
    'core': ('System & runtime', 'Agents, model resources, components, workflows and execution.'),
    'doc': ('Documentation & provenance', 'Documents, versions, licenses, lineage and traceability.'),
    'eval': ('Evaluation', 'Studies, targets, datasets, metrics, results and failures.'),
    'gov': ('Governance', 'Policies, risks, human review and prospective controls.'),
    'health': ('Clinical context', 'Intended use, patient populations, health data and interoperability.'),
    'report': ('Reporting assessment', 'Publications, requirements, evidence and completeness assessments.'),
}
NS = {m: f'https://w3id.org/agent-o/{"reporting" if m == "report" else m}#' for m in MODULES}
TYPES = {OWL.Class: 'Class', OWL.ObjectProperty: 'Object property',
         OWL.DatatypeProperty: 'Datatype property', OWL.AnnotationProperty: 'Annotation property',
         OWL.NamedIndividual: 'Individual'}
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


def term_path(term):
    return 'terms/' + compact(term).replace(':', '-') + '.html'


def link(term, prefix=''):
    if term in TERMS:
        return f'<a class="term-link {module_of(term)}" href="{prefix}{term_path(term)}">{esc(compact(term))}</a>'
    return f'<a href="{esc(str(term), quote=True)}">{esc(compact(term))}</a>'


def expression(term, prefix=''):
    if isinstance(term, URIRef):
        return link(term, prefix)
    if isinstance(term, Literal):
        suffix = f' @{term.language}' if term.language else (f' ({compact(term.datatype)})' if term.datatype else '')
        return esc(str(term) + suffix)
    for predicate, word in [(OWL.unionOf, 'or'), (OWL.intersectionOf, 'and'), (OWL.oneOf, 'one of')]:
        head = G.value(term, predicate)
        if head is not None:
            return '(' + f' <strong>{word}</strong> '.join(expression(v, prefix) for v in Collection(G, head)) + ')'
    if G.value(term, OWL.onProperty) is not None:
        items = [f'{expression(p, prefix)} {expression(v, prefix)}' for p, v in sorted(G.predicate_objects(term), key=lambda x: str(x)) if p != RDF.type]
        return '<span class="expression">Restriction: ' + '; '.join(items) + '</span>'
    if G.value(term, RDF.first) is not None:
        return '(' + ', '.join(expression(v, prefix) for v in Collection(G, term)) + ')'
    return '[' + '; '.join(f'{expression(p, prefix)} {expression(v, prefix)}' for p, v in sorted(G.predicate_objects(term), key=lambda x: str(x))) + ']'


def definition(term):
    return str(G.value(term, SKOS.definition) or G.value(term, RDFS.comment) or 'No definition is recorded in this module.')


def page(path, title, body, active=''):
    prefix = '../' * path.count('/')
    nav = [('index.html', 'Overview'), ('modules.html', 'Modules'), ('explore.html', 'Explore'),
           ('terms.html', 'Term index'), ('questions.html', 'Review questions')]
    navigation = ''.join('<a ' + ('aria-current="page"' if name == active else '') + f' href="{prefix}{href}">{name}</a>' for href, name in nav)
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · AGENT-O</title><meta name="description" content="Explore the AGENT-O ontology for health-oriented AI agent systems: definitions, relationships and review questions.">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/style.css">
<script src="{prefix}assets/site.js" defer></script></head><body>
<a class="skip" href="#main">Skip to content</a><header><a class="brand" href="{prefix}index.html"><span class="brand-mark">A<span>O</span></span>AGENT-O<span class="brand-sub">Ontology explorer</span></a>
<nav aria-label="Main navigation">{navigation}<a href="{REPO}">GitHub ↗</a></nav></header>
<main id="main">{body}</main><footer><div><strong>AGENT-O</strong> · Tao AI Group</div><div>Ontology & documentation: CC BY 4.0 · Code: MIT</div><a href="{prefix}downloads/source-manifest.json">Source manifest</a><a href="{REPO}/issues/new/choose">Suggest a change ↗</a></footer></body></html>'''
    destination = OUT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding='utf-8')


def eyebrow(text):
    return f'<p class="eyebrow">{text}</p>'


def term_table(terms, prefix=''):
    rows = []
    for term in sorted(terms, key=lambda t: compact(t).lower()):
        deprecated = bool(G.value(term, OWL.deprecated))
        badge = ' <span class="badge">Deprecated</span>' if deprecated else ''
        rows.append(f'<tr data-search="{esc((compact(term) + " " + definition(term)).lower(), quote=True)}" data-module="{module_of(term)}" data-kind="{TERMS[term]}"><td>{link(term, prefix)}{badge}</td><td>{TERMS[term]}</td><td>{esc(definition(term))}</td></tr>')
    return '<div class="table-wrap"><table><thead><tr><th>Term</th><th>Kind</th><th>Definition</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'


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
    active = [t for t in TERMS if not G.value(t, OWL.deprecated)]
    counts = Counter(TERMS[t] for t in active)
    module_cards = ''.join(f'<a class="module-card {m}" href="modules/{m}.html"><span class="module-tag">{m}:</span><h3>{title}</h3><p>{desc}</p><span class="module-count">{sum(module_of(t) == m for t in active)} active terms <span aria-hidden="true">↗</span></span></a>' for m, (title, desc) in MODULES.items())
    page('index.html', 'An open map of health AI agents', f'''
<section class="hero"><div>{eyebrow('A SHARED LANGUAGE FOR HEALTH AI')}<h1>Understand the system.<br><em>Trace the decisions.</em></h1><p class="hero-copy">Explore how AGENT-O connects agent architecture, model resources, evaluation, governance and clinical context in one modular ontology.</p><div class="actions"><a class="button" href="explore.html">Explore the ontology <span>↗</span></a><a class="button secondary" href="questions.html">Review the design</a></div><p class="small">Built from the six authoritative ontology modules. Browse every declared term, follow its relationships, and share specific feedback.</p></div><div class="hero-map"><span class="map-caption">SIX CONNECTED PERSPECTIVES</span><div class="map-center">AGENT-O<span>Health AI agent systems</span></div><div class="map-grid">{''.join(f'<a class="{m}" href="modules/{m}.html"><i></i><b>{m}:</b><span>{v[0]}</span></a>' for m,v in MODULES.items())}</div><p>Explanatory module map · colors identify namespaces</p></div></section>
<div class="stats"><div><b>6</b><span>Semantic modules</span></div><div><b>{counts['Class']}</b><span>Active classes</span></div><div><b>{counts['Object property']}</b><span>Active object properties</span></div><div><b>{counts['Datatype property']}</b><span>Active datatype properties</span></div></div>
<section><div class="section-heading"><div>{eyebrow('01 / THE DESIGN')}<h2>One system. Six perspectives.</h2></div><p>Start with a module, then follow the definitions and cross-module links.</p></div><div class="module-grid">{module_cards}</div></section>
<section class="overview"><div class="section-heading"><div>{eyebrow('02 / THE STARTING POINT')}<h2>The relationships that matter first.</h2></div><a class="text-link" href="assets/agent-o_engineer_overview.pdf">Download vector PDF ↗</a></div><a class="figure-link" href="assets/agent-o_engineer_overview.svg"><img src="assets/agent-o_engineer_overview.svg" alt="Selected AGENT-O class relationships grouped into system architecture, evaluation, governance, reporting assessment and intended clinical use." width="1600" height="1280" loading="lazy"></a><p class="small">Selected schema view: 23 distinct classes out of {counts['Class']} active classes, with 20 checked relationships. Solid arrows summarize object-property links between instances; dashed hollow arrows denote subclasses. Panels are explanatory groups. <a href="assets/overview-notes.md">Full caption and interpretation</a>. The complete reference is in the <a href="terms.html">term index</a>.</p></section>
<section class="reading-path"><div>{eyebrow('03 / FROM SCHEMA TO EXAMPLE')}<h2>Follow a medication-safety system.</h2><p>A published synthetic example connects a configured system, its model components, clinical use, governance controls and reporting evidence. Inspect the actual RDF statements in context.</p><a class="button secondary" href="example.html">Walk through the example ↗</a></div><div class="callout"><h3>Bring your questions.</h3><p>Can the model describe a system you know? Which distinction is unclear? What concept is missing? Use the competency questions to guide a focused review.</p><a class="text-link" href="questions.html">Open review questions →</a></div></section>''', 'Overview')
    page('modules.html', 'Six semantic modules', eyebrow('THE DESIGN / MODULES') + '<h1>Six semantic modules.</h1><p class="lead">Each namespace covers a distinct part of the representation. Relationships connect terms across these boundaries.</p><div class="module-grid">' + module_cards + '</div><section><h2>Beyond the six modules</h2><p>Application profiles, external alignments and SHACL shapes complement the semantic modules. They are separate artifacts and are not included in the module term counts.</p><div class="actions"><a class="button secondary" href="' + REPO + '/tree/main/ontology/profiles">Profiles ↗</a><a class="button secondary" href="' + REPO + '/tree/main/ontology/alignments">External alignments ↗</a><a class="button secondary" href="' + REPO + '/tree/main/shapes">SHACL shapes ↗</a></div></section>', 'Modules')
    for m, (title, desc) in MODULES.items():
        selected = [t for t in TERMS if module_of(t) == m]
        page(f'modules/{m}.html', title, f'{eyebrow("MODULE / " + m.upper())}<h1>{title}</h1><p class="lead">{desc}</p><p><code>{NS[m]}</code></p><div class="actions"><a class="button secondary" href="../downloads/ontology/modules/agento-{m}.ttl" download>Download Turtle ↓</a><a class="button secondary" href="../explore.html?module={m}">Explore relationships ↗</a></div><section><h2>Declared terms</h2><label class="search-label">Filter this module<input id="term-search" type="search" placeholder="Search names and definitions…"></label><p id="result-count" aria-live="polite"></p>{term_table(selected, "../")}</section>', 'Modules')
    for term, kind in sorted(TERMS.items()):
        m = module_of(term)
        predicates = sorted(G.predicate_objects(term), key=lambda pv: (str(pv[0]), str(pv[1])))
        axioms = ''.join(f'<tr><th>{expression(p, "../")}</th><td>{expression(v, "../")}</td></tr>' for p,v in predicates)
        incoming = sorted([(s,p) for s,p in G.subject_predicates(term) if s in TERMS], key=lambda sp: (str(sp[0]), str(sp[1])))
        uses = ''.join(f'<tr><td>{link(s,"../")}</td><td>{expression(p,"../")}</td></tr>' for s,p in incoming)
        feedback = REPO + '/issues/new?template=ontology-feedback.yml&title=' + compact(term).replace(':', '%3A')
        heading = eyebrow(f'<a href="../modules/{m}.html">{m.upper()} MODULE</a> / {kind.upper()}')
        references = '<div class="table-wrap"><table><thead><tr><th>Term</th><th>Relationship to this term</th></tr></thead><tbody>' + uses + '</tbody></table></div>' if uses else '<p>No direct named-term references in these six modules. Anonymous expressions may also reference this term.</p>'
        page(term_path(term), compact(term), f'{heading}<h1 class="term-title">{esc(compact(term))}</h1><p class="lead">{esc(definition(term))}</p><p class="iri"><strong>IRI</strong> <a href="{term}">{term}</a></p><div class="actions"><a class="button secondary" href="../explore.html?term={compact(term)}">Explore neighborhood ↗</a><a class="button secondary" href="{feedback}">Comment on this term ↗</a><a class="text-link" href="{REPO}/blob/main/ontology/modules/agento-{m}.ttl">View source</a></div><section><h2>Declared annotations & axioms</h2><p>Direct assertions from the module. Anonymous OWL expressions are expanded below. No inferred axioms are added.</p><div class="table-wrap"><table class="axioms"><tbody>{axioms}</tbody></table></div></section><section><h2>Referenced by</h2>{references}</section>', 'Term index')
    filters = '<div class="filters"><label>Namespace<select id="module-filter"><option value="">All six modules</option>' + ''.join(f'<option value="{m}">{m}:</option>' for m in MODULES) + '</select></label><label>Term kind<select id="kind-filter"><option value="">All kinds</option>' + ''.join(f'<option>{k}</option>' for k in TYPES.values()) + '</select></label></div>'
    page('terms.html', 'Complete term index', eyebrow('THE REFERENCE / ALL TERMS') + '<h1>Every term, connected.</h1><p class="lead">Search the names and source definitions of all declared classes, properties and named individuals. Deprecated terms are labeled explicitly.</p><label class="search-label">Search the ontology<input id="term-search" type="search" placeholder="Try model, escalation, population…"></label>' + filters + '<p id="result-count" aria-live="polite"></p>' + term_table(TERMS), 'Term index')
    build_graph()
    build_questions()
    build_example()
    print(json.dumps({'module_triples': len(G), 'active_terms': dict(counts), 'term_pages': len(TERMS), 'html_pages': len(list(OUT.rglob('*.html')))}, indent=2))


def build_graph():
    nodes = [{'id': compact(t), 'module': module_of(t), 'kind': kind, 'definition': definition(t), 'url': term_path(t)} for t,kind in sorted(TERMS.items())]
    edges = []
    for s,o in G.subject_objects(RDFS.subClassOf):
        if s in TERMS and o in TERMS:
            edges.append({'source': compact(s), 'target': compact(o), 'label': 'is-a', 'kind': 'subclass', 'url': term_path(s)})
    # Preserve domain/range expressions as expressions; do not turn union members into asserted edges.
    for p in G.subjects(RDF.type, OWL.ObjectProperty):
        for domain in G.objects(p, RDFS.domain):
            for range_ in G.objects(p, RDFS.range):
                if domain in TERMS and range_ in TERMS:
                    edges.append({'source': compact(domain), 'target': compact(range_), 'label': compact(p), 'kind': 'property', 'url': term_path(p)})
    data = {'nodes': nodes, 'edges': edges}
    (OUT / 'assets/graph.json').write_text(json.dumps(data, indent=2))
    options = ''.join(f'<option value="{esc(n["id"])}">{esc(n["id"])}</option>' for n in nodes if n['kind'] == 'Class')
    page('explore.html', 'Explore relationships', eyebrow('THE EXPLORER / FOLLOW A CONNECTION') + '<h1>See how the concepts connect.</h1><p class="lead">Choose a class to explore its direct neighborhood across namespaces. Select a neighboring node to move through the ontology.</p><div class="graph-controls"><label>Module<select id="graph-module"><option value="">All modules</option>' + ''.join(f'<option value="{m}">{m}:</option>' for m in MODULES) + '</select></label><label>Focus class<select id="graph-focus">' + options + '</select></label><button id="zoom-out" aria-label="Zoom out">−</button><button id="zoom-in" aria-label="Zoom in">+</button><button id="zoom-reset">Reset zoom</button></div><p id="graph-status" aria-live="polite">Loading relationships…</p><div class="graph-scroll"><svg id="graph" role="img" aria-label="Interactive class neighborhood"></svg></div><div class="legend">' + ''.join(f'<span class="{m}"><i></i>{m}:</span>' for m in MODULES) + '<span>→ Object-property domain / range</span><span>⇢ Direct subclass → parent</span></div><p class="small">This browser shows direct named-class subclass axioms and object properties with named domain and range. Union domains/ranges, restrictions, inherited links and external alignments remain available on each term page. A property arrow summarizes a possible link between instances; it does not assert existence or cardinality.</p><section><h2 id="focus-title">Focus details</h2><p id="focus-definition"></p><a id="focus-link" class="text-link" href="terms.html">Open full term definition →</a><div id="graph-relations"></div></section><noscript><p>The interactive view needs JavaScript. All definitions and axioms are available in the <a href="terms.html">complete term index</a>.</p></noscript>', 'Explore')


def build_questions():
    rows = []
    text = (ROOT / 'queries/competency/README.md').read_text()
    for number, filename, question in re.findall(r'\| (CQ\d+) \| `([^`]+)` \| (.*?) \|', text):
        path = ROOT / 'queries/competency' / filename
        query = path.read_text()
        rows.append(f'<article class="cq"><span class="eyebrow">{number}</span><h3>{esc(question)}</h3><details><summary>Inspect the SPARQL query</summary><pre><code>{esc(query)}</code></pre></details><div class="actions"><a href="downloads/queries/competency/{filename}" download>Download query ↓</a><a href="{REPO}/issues/new?template=ontology-feedback.yml&title={number}%20feedback">Discuss this question ↗</a></div></article>')
    page('questions.html', 'Review with competency questions', eyebrow('CONTRIBUTE / REVIEW THE DESIGN') + '<h1>Start with a question.</h1><p class="lead">A useful ontology should answer useful questions. Review these existing competency questions against a system or clinical workflow you know.</p><div class="callout"><h2>Three prompts for reviewers</h2><ol><li>Is the question meaningful in your domain? What is missing?</li><li>Can the ontology express a concrete example and the answer you expect?</li><li>Which definition or relationship should change? Include the term IRI and an example.</li></ol><a class="button" href="' + REPO + '/issues/new/choose">Share structured feedback ↗</a><p>GitHub feedback requires a GitHub account. You can also give these questions and term links to the project team through your usual communication channel.</p></div><section><h2>The competency questions</h2><p>Queries can be run locally against the ontology and supplied synthetic examples using <code>python scripts/run_sparql_cqs.py</code>. The website is a static reference, not a live SPARQL endpoint.</p>' + ''.join(rows) + '</section><section><h2>Interpretation matters</h2><p>Reporting completeness concerns publication coverage. It does not establish clinical safety, performance, fairness, compliance or deployment readiness. SHACL conformance applies to the tested graph and declared shapes.</p></section>', 'Review questions')


def build_example():
    graph = Graph().parse(ROOT / 'data/examples/governance_reporting_profile_example.ttl')
    ns = 'https://w3id.org/agent-o/examples/governance-reporting-profile#'
    focus = URIRef(ns + 'MedicationSafetyAgent')
    assert (focus, RDF.type, None) in graph
    selected = {focus}
    selected.update(o for o in graph.objects(focus) if isinstance(o, URIRef) and str(o).startswith(ns))
    selected.update(s for s in graph.subjects(None, focus) if isinstance(s, URIRef) and str(s).startswith(ns))
    sections = []
    for subject in sorted(selected):
        rows = []
        for p,o in sorted(graph.predicate_objects(subject), key=lambda x: str(x)):
            obj = link(o) if o in TERMS else esc(str(o).replace(ns, 'example:'))
            rows.append(f'<tr><th>{expression(p)}</th><td>{obj}</td></tr>')
        sections.append(f'<article class="example-record"><h3>{esc(str(subject).replace(ns,"example:"))}</h3><div class="table-wrap"><table><tbody>{"".join(rows)}</tbody></table></div></article>')
    page('example.html', 'A medication-safety example', eyebrow('A WORKED EXAMPLE / ACTUAL RDF') + '<h1>From a system to its evidence.</h1><p class="lead">Follow the medication-safety example distributed with AGENT-O. These are illustrative, synthetic records, not evidence of a deployed or clinically validated system.</p><p>Start at <code>example:MedicationSafetyAgent</code>. The records below show this entity and its directly connected example entities. Colored links open schema definitions.</p><a class="button secondary" href="downloads/data/examples/governance_reporting_profile_example.ttl" download>Download the complete example ↓</a><section>' + ''.join(sections) + '</section>')


if __name__ == '__main__':
    main()
