#!/usr/bin/env python3
"""Run AGENT-O competency SPARQL queries over ontology, alignments, and examples."""

from __future__ import annotations

import json
import sys
from pathlib import Path

VENDOR_PATH = Path("/tmp/rdflib_validate")
if VENDOR_PATH.exists():
    sys.path.insert(0, str(VENDOR_PATH))

try:
    from rdflib import Graph
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "rdflib is required. Run with PYTHONPATH=/tmp/rdflib_validate or install requirements.txt."
    ) from exc

try:
    from owlrl import DeductiveClosure, OWLRL_Semantics
except ImportError:  # pragma: no cover
    DeductiveClosure = None
    OWLRL_Semantics = None


ROOT = Path(__file__).resolve().parents[1]


def ttl_inputs() -> list[Path]:
    paths = [ROOT / "ontology" / "agento.ttl"]
    paths.extend(sorted((ROOT / "ontology" / "alignments").glob("*.ttl")))
    paths.extend(sorted((ROOT / "ontology" / "profiles").glob("*.ttl")))
    paths.extend(sorted((ROOT / "data" / "examples").glob("*.ttl")))
    return [path for path in paths if path.exists()]


def serialize(value):
    if value is None:
        return None
    return value.toPython() if hasattr(value, "toPython") else str(value)


def main() -> None:
    graph = Graph()
    for path in ttl_inputs():
        graph.parse(path, format="turtle")
    before = len(graph)
    if DeductiveClosure and OWLRL_Semantics:
        DeductiveClosure(OWLRL_Semantics).expand(graph)
    inferred = len(graph) - before

    results = {}
    for query_path in sorted((ROOT / "queries" / "competency").glob("*.rq")):
        rows = []
        query_result = graph.query(query_path.read_text(encoding="utf-8"))
        for row in query_result:
            rows.append({str(var): serialize(row[var]) for var in query_result.vars})
        results[query_path.stem] = {
            "query": str(query_path.relative_to(ROOT)),
            "row_count": len(rows),
            "status": "answered" if rows else "no_rows",
            "rows": rows,
        }

    out_dir = ROOT / "outputs" / "sparql"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "input_triples": before,
        "inferred_triples": inferred,
        "queries": results,
        "answered": sum(1 for item in results.values() if item["status"] == "answered"),
        "total": len(results),
    }
    (out_dir / "cq_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# AGENT-O Competency Query Summary",
        "",
        f"- Input triples: `{before}`",
        f"- Inferred triples: `{inferred}`",
        f"- Answered queries: `{payload['answered']}/{payload['total']}`",
        "",
        "| Query | Status | Rows |",
        "| --- | --- | ---: |",
    ]
    for name, item in results.items():
        lines.append(f"| `{name}` | {item['status']} | {item['row_count']} |")
    (out_dir / "cq_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ["answered", "total", "input_triples", "inferred_triples"]}, indent=2))
    raise SystemExit(0 if payload["answered"] == payload["total"] else 1)


if __name__ == "__main__":
    main()
