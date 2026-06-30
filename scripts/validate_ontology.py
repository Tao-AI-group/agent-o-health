#!/usr/bin/env python3
"""Validate generated AGENT-O ontology, alignment, and example Turtle files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

VENDOR_PATH = Path("/tmp/rdflib_validate")
if VENDOR_PATH.exists():
    sys.path.insert(0, str(VENDOR_PATH))

try:
    from rdflib import Graph, URIRef, RDF, RDFS, OWL, Namespace
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "rdflib is required. Run with PYTHONPATH=/tmp/rdflib_validate or install requirements.txt."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
AGENTO_PREFIX = "https://w3id.org/agent-o/"
OLD_ACRO_PREFIX = "https://example.org/acro/"
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


def is_agento(term) -> bool:
    return isinstance(term, URIRef) and str(term).startswith(AGENTO_PREFIX)


def ttl_files() -> list[Path]:
    candidates: list[Path] = []
    for directory in [
        ROOT / "ontology",
        ROOT / "shapes",
        ROOT / "queries",
        ROOT / "data" / "examples",
    ]:
        if directory.exists():
            candidates.extend(sorted(directory.rglob("*.ttl")))
    return sorted(set(candidates))


def active_ttl_files(files: list[Path]) -> list[Path]:
    return [
        path
        for path in files
        if "deprecated" not in path.parts
    ]


def parse_file(path: Path) -> tuple[bool, int | None, str | None]:
    graph = Graph()
    try:
        graph.parse(path, format="turtle")
    except Exception as exc:  # pragma: no cover
        return False, None, str(exc)
    return True, len(graph), None


def collect_graph(paths: list[Path]) -> Graph:
    graph = Graph()
    for path in paths:
        graph.parse(path, format="turtle")
    return graph


def qname(graph: Graph, term: URIRef) -> str:
    try:
        return graph.namespace_manager.normalizeUri(term)
    except Exception:
        return str(term)


def missing_labels(graph: Graph, rdf_type: URIRef) -> list[str]:
    values = []
    for term in sorted(set(graph.subjects(RDF.type, rdf_type)), key=str):
        if is_agento(term) and not list(graph.objects(term, RDFS.label)):
            values.append(qname(graph, term))
    return values


def missing_property_axioms(graph: Graph, rdf_type: URIRef, predicate: URIRef) -> list[str]:
    values = []
    for term in sorted(set(graph.subjects(RDF.type, rdf_type)), key=str):
        if is_agento(term) and not list(graph.objects(term, predicate)):
            values.append(qname(graph, term))
    return values


def active_old_uri_hits(paths: list[Path]) -> list[str]:
    hits = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if OLD_ACRO_PREFIX in text:
            hits.append(str(path.relative_to(ROOT)))
    return hits


def undefined_alignment_terms(graph: Graph, alignment_paths: list[Path], defined_graph: Graph) -> list[str]:
    defined_terms = set()
    for rdf_type in [OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, SKOS.Concept, SKOS.ConceptScheme]:
        defined_terms.update(t for t in defined_graph.subjects(RDF.type, rdf_type) if is_agento(t))
    undefined = set()
    for path in alignment_paths:
        local = Graph().parse(path, format="turtle")
        for s, p, o in local:
            for term in [s, p, o]:
                if is_agento(term) and term not in defined_terms and (term, RDF.type, OWL.Ontology) not in graph:
                    undefined.add(term)
    return [qname(graph, term) for term in sorted(undefined, key=str)]


def main() -> None:
    files = ttl_files()
    parse_results = {}
    parse_failures = []
    for path in files:
        ok, triples, error = parse_file(path)
        rel = str(path.relative_to(ROOT))
        parse_results[rel] = {"ok": ok, "triples": triples, "error": error}
        if not ok:
            parse_failures.append(rel)

    active_files = active_ttl_files(files)
    active_graph = collect_graph(active_files)
    ontology_files = [path for path in active_files if "ontology" in path.parts and "deprecated" not in path.parts]
    defined_graph = collect_graph(ontology_files)
    alignment_paths = [path for path in active_files if "alignments" in path.parts]

    results = {
        "files_checked": len(files),
        "parse_failures": parse_failures,
        "parse_results": parse_results,
        "active_old_acro_uri_files": active_old_uri_hits(active_files),
        "missing_class_labels": missing_labels(defined_graph, OWL.Class),
        "missing_object_property_labels": missing_labels(defined_graph, OWL.ObjectProperty),
        "missing_datatype_property_labels": missing_labels(defined_graph, OWL.DatatypeProperty),
        "object_properties_missing_domain": missing_property_axioms(defined_graph, OWL.ObjectProperty, RDFS.domain),
        "object_properties_missing_range": missing_property_axioms(defined_graph, OWL.ObjectProperty, RDFS.range),
        "datatype_properties_missing_domain": missing_property_axioms(defined_graph, OWL.DatatypeProperty, RDFS.domain),
        "datatype_properties_missing_range": missing_property_axioms(defined_graph, OWL.DatatypeProperty, RDFS.range),
        "undefined_alignment_terms": undefined_alignment_terms(active_graph, alignment_paths, defined_graph),
    }

    passed = not any(
        [
            results["parse_failures"],
            results["active_old_acro_uri_files"],
            results["missing_class_labels"],
            results["missing_object_property_labels"],
            results["missing_datatype_property_labels"],
            results["object_properties_missing_domain"],
            results["object_properties_missing_range"],
            results["datatype_properties_missing_domain"],
            results["datatype_properties_missing_range"],
            results["undefined_alignment_terms"],
        ]
    )
    results["passed"] = passed

    out_dir = ROOT / "outputs" / "validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "formal_quality_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    lines = [
        "# AGENT-O Formal Quality Report",
        "",
        f"- Files checked: `{results['files_checked']}`",
        f"- Parse failures: `{len(results['parse_failures'])}`",
        f"- Active files containing old ACRO URIs: `{len(results['active_old_acro_uri_files'])}`",
        f"- Classes missing labels: `{len(results['missing_class_labels'])}`",
        f"- Object properties missing labels: `{len(results['missing_object_property_labels'])}`",
        f"- Datatype properties missing labels: `{len(results['missing_datatype_property_labels'])}`",
        f"- Object properties missing domain/range: `{len(results['object_properties_missing_domain'])}/{len(results['object_properties_missing_range'])}`",
        f"- Datatype properties missing domain/range: `{len(results['datatype_properties_missing_domain'])}/{len(results['datatype_properties_missing_range'])}`",
        f"- Undefined AGENT-O terms in alignments: `{len(results['undefined_alignment_terms'])}`",
        f"- Passed: `{passed}`",
        "",
        "## Notes",
        "",
        "- Deprecated ACRO URIs are allowed only in `ontology/deprecated/`.",
        "- Alignment files may reference external ontology IRIs, but AGENT-O terms used in alignments must be defined by active AGENT-O ontology files.",
    ]
    (out_dir / "formal_quality_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: results[k] for k in ["passed", "files_checked", "parse_failures", "active_old_acro_uri_files"]}, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
