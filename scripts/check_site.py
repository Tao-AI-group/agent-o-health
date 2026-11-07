#!/usr/bin/env python3
"""Check generated references, downloads, term coverage and source consistency."""
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

from rdflib import Graph, RDF, URIRef
from rdflib.namespace import OWL

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        self.urls.extend(v for k,v in attrs if k in {'href', 'src'} and v)


def main():
    errors = []
    pages = sorted(SITE.rglob('*.html'))
    for page in pages:
        parser = Links()
        parser.feed(page.read_text())
        for url in parser.urls:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            target = (page.parent / unquote(parts.path)).resolve()
            if not target.is_file():
                errors.append(f'{page.relative_to(SITE)}: broken link {url}')
    graph = Graph()
    for path in sorted((ROOT / 'ontology/modules').glob('*.ttl')):
        graph.parse(path)
    expected = {str(s) for s,t in graph.subject_objects(RDF.type)
                if isinstance(s, URIRef) and str(s).startswith('https://w3id.org/agent-o/')
                and t in {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty, OWL.NamedIndividual}}
    data = json.loads((SITE / 'assets/graph.json').read_text())
    actual = {n['id'] for n in data['nodes']}
    assert len(actual) == len(expected) == len(list((SITE / 'terms').glob('*.html')))
    for path in (ROOT / 'ontology').rglob('*.ttl'):
        assert path.read_bytes() == (SITE / 'downloads' / path.relative_to(ROOT)).read_bytes()
    manifest = json.loads((SITE / 'downloads/source-manifest.json').read_text())
    for name, digest in manifest['authoritative_modules_sha256'].items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == digest
    overview = json.loads((SITE / 'assets/overview-source-manifest.json').read_text())
    assert overview['source_files'] == manifest['authoritative_modules_sha256'], 'Overview needs regeneration for these module sources.'
    for forbidden in ['apps', '.git', 'paper', 'outputs']:
        assert not (SITE / forbidden).exists(), forbidden
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Passed: {len(pages)} HTML pages, {len(expected)} term pages, all local links and ontology downloads, source hashes and publication scope.')


if __name__ == '__main__':
    main()
