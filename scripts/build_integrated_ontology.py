#!/usr/bin/env python3
"""Build the integrated AGENT-O ontology from the authoritative modules."""

from __future__ import annotations

import sys
from pathlib import Path

VENDOR_PATH = Path("/tmp/rdflib_validate")
if VENDOR_PATH.exists():
    sys.path.insert(0, str(VENDOR_PATH))

try:
    from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
    from rdflib.namespace import OWL
except ImportError as exc:  # pragma: no cover
    raise SystemExit("rdflib is required; install requirements.txt first.") from exc


ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = ROOT / "ontology" / "modules"
OUTPUT_PATH = ROOT / "ontology" / "agento.ttl"
AGENTO = Namespace("https://w3id.org/agent-o/")
TOP_ONTOLOGY = URIRef("https://w3id.org/agent-o")


def module_paths() -> list[Path]:
    return sorted(MODULE_DIR.glob("*.ttl"))


def build_graph() -> Graph:
    graph = Graph()
    for path in module_paths():
        graph.parse(path, format="turtle")

    graph.add((TOP_ONTOLOGY, RDF.type, OWL.Ontology))
    graph.add((TOP_ONTOLOGY, RDFS.label, Literal("AGENT-O Ontology", lang="en")))
    graph.add(
        (
            TOP_ONTOLOGY,
            RDFS.comment,
            Literal(
                "Integrated AGENT-O ontology covering agent systems, model specifications and deployments, "
                "runtime workflow, evaluation, documentation and provenance, governance, clinical context, "
                "health-data interoperability, and reporting-assessment representation.",
                lang="en",
            ),
        )
    )

    bindings = {
        "core": "https://w3id.org/agent-o/core#",
        "doc": "https://w3id.org/agent-o/doc#",
        "eval": "https://w3id.org/agent-o/eval#",
        "gov": "https://w3id.org/agent-o/gov#",
        "health": "https://w3id.org/agent-o/health#",
        "report": "https://w3id.org/agent-o/reporting#",
    }
    for prefix, iri in bindings.items():
        graph.bind(prefix, Namespace(iri))
    return graph


def main() -> None:
    paths = module_paths()
    if not paths:
        raise SystemExit(f"No module TTL files found under {MODULE_DIR}")
    graph = build_graph()
    graph.serialize(destination=OUTPUT_PATH, format="turtle")
    print(f"Built {OUTPUT_PATH.relative_to(ROOT)} from {len(paths)} modules ({len(graph)} triples).")


if __name__ == "__main__":
    main()
