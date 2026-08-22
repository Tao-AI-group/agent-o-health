#!/usr/bin/env python3
"""Generate a compact alignment matrix from AGENT-O alignment files."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

VENDOR_PATH = Path("/tmp/rdflib_validate")
if VENDOR_PATH.exists():
    sys.path.insert(0, str(VENDOR_PATH))

try:
    from rdflib import Graph, URIRef, RDFS, OWL, Namespace
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "rdflib is required. Run with PYTHONPATH=/tmp/rdflib_validate or install requirements.txt."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
AGENTO_PREFIX = "https://w3id.org/agent-o/"
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

MAPPING_PREDICATES = {
    OWL.equivalentClass: "owl:equivalentClass",
    OWL.equivalentProperty: "owl:equivalentProperty",
    RDFS.subClassOf: "rdfs:subClassOf",
    RDFS.subPropertyOf: "rdfs:subPropertyOf",
    SKOS.exactMatch: "skos:exactMatch",
    SKOS.closeMatch: "skos:closeMatch",
    SKOS.relatedMatch: "skos:relatedMatch",
}


def module_for(term: URIRef) -> str:
    text = str(term)
    for module in ["core", "doc", "eval", "gov", "health", "reporting"]:
        if text.startswith(f"{AGENTO_PREFIX}{module}#"):
            return "report" if module == "reporting" else module
    return "other"


def is_agento(term) -> bool:
    return isinstance(term, URIRef) and str(term).startswith(AGENTO_PREFIX)


def qname(graph: Graph, term) -> str:
    try:
        return graph.namespace_manager.normalizeUri(term)
    except Exception:
        return str(term)


def main() -> None:
    rows = []
    for path in sorted((ROOT / "ontology" / "alignments").glob("*.ttl")):
        graph = Graph().parse(path, format="turtle")
        graph.bind("skos", SKOS)
        for predicate, mapping_type in MAPPING_PREDICATES.items():
            for source, target in graph.subject_objects(predicate):
                if not is_agento(source):
                    continue
                rows.append(
                    {
                        "module": module_for(source),
                        "source": qname(graph, source),
                        "mapping_type": mapping_type,
                        "target": qname(graph, target),
                        "file": str(path.relative_to(ROOT)),
                    }
                )

    out_dir = ROOT / "outputs" / "alignment"
    paper_dir = ROOT / "outputs" / "paper_tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    paper_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "alignment_matrix.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["module", "source", "mapping_type", "target", "file"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    by_module = Counter(row["module"] for row in rows)
    by_type = Counter(row["mapping_type"] for row in rows)
    summary = {
        "mapping_count": len(rows),
        "by_module": dict(sorted(by_module.items())),
        "by_type": dict(sorted(by_type.items())),
    }
    (out_dir / "alignment_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# AGENT-O External Alignment Summary",
        "",
        f"- Alignment triples counted: `{len(rows)}`",
        "",
        "## By Module",
        "",
        "| Module | Count |",
        "| --- | ---: |",
    ]
    for module, count in sorted(by_module.items()):
        lines.append(f"| {module} | {count} |")
    lines.extend(["", "## By Mapping Type", "", "| Mapping type | Count |", "| --- | ---: |"])
    for mapping_type, count in sorted(by_type.items()):
        lines.append(f"| `{mapping_type}` | {count} |")
    (out_dir / "alignment_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    table = [
        "# Table: External Alignment",
        "",
        "| Module | AGENT-O source | Mapping | External target |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        table.append(f"| {row['module']} | `{row['source']}` | `{row['mapping_type']}` | `{row['target']}` |")
    (paper_dir / "table_external_alignment.md").write_text("\n".join(table) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
