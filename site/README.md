# AGENT-O ontology website

The GitHub Pages website is generated directly from the six authoritative
`ontology/modules/*.ttl` sources. It includes an overview, six module pages,
one static page per declared term, a searchable index, a class-neighborhood
explorer, a synthetic example and the repository's competency questions.

## Build locally

From the repository root, with Python 3.11 or newer:

```bash
python -m pip install -r requirements.txt
python scripts/build_site.py
python scripts/check_site.py
python -m http.server 8000 --directory _site --bind 127.0.0.1
```

Open `http://127.0.0.1:8000`. `_site/` is generated and not committed.
The HTML term reference works without JavaScript; the search and interactive
neighborhood view use local JavaScript with no third-party CDN dependencies.

## Publish on GitHub Pages

In repository **Settings → Pages → Build and deployment → Source**, select
**GitHub Actions**. The `Ontology website` workflow validates, builds and deploys
on relevant `main` changes, or via **Actions → Ontology website → Run workflow**.
Pull requests build and validate without deploying.

Expected project URL: `https://tao-ai-group.github.io/agent-o-health/`.

Only the generated `_site/` directory is deployed. The build copies ontology,
shapes, queries and synthetic RDF examples into downloads; it does not copy
applications, papers, corpus assessments, local credentials or private paths.

## Source and diagram scope

Term pages reproduce direct assertions, expand anonymous OWL expressions and
link to the source namespace. Counts exclude deprecated terms and count named
declarations in the six modules only. Profiles and alignments are separate.
The graph shows direct named-class subclass axioms and named domain/range
patterns; it does not flatten union expressions or claim to be an OWL reasoner.

The 2026-11-05 overview is an intentionally selected review diagram. Its caption
is in `assets/overview-notes.md`. If any of its 23 classes or 20 relationships
change, regenerate and visually review it from the ontology workspace before
updating the website asset. The term reference always rebuilds from source.

WIDOCO, WebVOWL, OOPS! and WebProtégé are not integrated into this version.
The site uses a repository-owned static generator and GitHub issue feedback.
