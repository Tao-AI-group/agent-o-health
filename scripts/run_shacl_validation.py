#!/usr/bin/env python3
"""Run AGENT-O SHACL profile validation over ontology, profiles, and examples."""

from __future__ import annotations

import json
import sys
from pathlib import Path

VENDOR_PATH = Path("/tmp/rdflib_validate")
if VENDOR_PATH.exists():
    sys.path.insert(0, str(VENDOR_PATH))

try:
    from pyshacl import validate
    from pyshacl.errors import ValidationFailure
    from rdflib import Graph, Namespace, RDF
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "pyshacl and rdflib are required. Run with PYTHONPATH=/tmp/rdflib_validate or install requirements.txt."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
SH = Namespace("http://www.w3.org/ns/shacl#")


def data_inputs() -> list[Path]:
    paths = [ROOT / "ontology" / "agento.ttl"]
    paths.extend(sorted((ROOT / "ontology" / "alignments").glob("*.ttl")))
    paths.extend(sorted((ROOT / "ontology" / "profiles").glob("*.ttl")))
    paths.extend(sorted((ROOT / "data" / "examples").glob("*.ttl")))
    return [path for path in paths if path.exists()]


def load_graph(paths: list[Path]) -> Graph:
    graph = Graph()
    for path in paths:
        graph.parse(path, format="turtle")
    return graph


def qname(graph: Graph, term) -> str | None:
    if term is None:
        return None
    try:
        return graph.namespace_manager.normalizeUri(term)
    except Exception:
        return str(term)


def summarize_results(results_graph: Graph) -> dict:
    if isinstance(results_graph, ValidationFailure):
        return {
            "severity_counts": {"ValidationFailure": 1},
            "results": [
                {
                    "severity": "ValidationFailure",
                    "focus_node": None,
                    "source_shape": None,
                    "message": str(results_graph),
                }
            ],
        }
    severities: dict[str, int] = {}
    items = []
    for result in sorted(results_graph.subjects(RDF.type, SH.ValidationResult), key=str):
        severity = next(results_graph.objects(result, SH.resultSeverity), None)
        focus = next(results_graph.objects(result, SH.focusNode), None)
        source_shape = next(results_graph.objects(result, SH.sourceShape), None)
        message = next(results_graph.objects(result, SH.resultMessage), None)
        severity_key = qname(results_graph, severity) or "unknown"
        severities[severity_key] = severities.get(severity_key, 0) + 1
        items.append(
            {
                "severity": severity_key,
                "focus_node": qname(results_graph, focus),
                "source_shape": qname(results_graph, source_shape),
                "message": str(message) if message is not None else None,
            }
        )
    return {"severity_counts": severities, "results": items}


def main() -> None:
    data_paths = data_inputs()
    data_graph = load_graph(data_paths)
    shape_paths = sorted((ROOT / "shapes").glob("*.ttl"))
    out_dir = ROOT / "outputs" / "shacl"
    out_dir.mkdir(parents=True, exist_ok=True)

    shape_results = {}
    for shape_path in shape_paths:
        shape_graph = Graph().parse(shape_path, format="turtle")
        conforms, results_graph, results_text = validate(
            data_graph=data_graph,
            shacl_graph=shape_graph,
            inference="rdfs",
            abort_on_first=False,
            allow_infos=True,
            allow_warnings=True,
            advanced=True,
            meta_shacl=False,
        )
        summary = summarize_results(results_graph)
        shape_results[shape_path.stem] = {
            "shape": str(shape_path.relative_to(ROOT)),
            "conforms": bool(conforms),
            "result_count": len(summary["results"]),
            **summary,
        }
        (out_dir / f"{shape_path.stem}_validation.md").write_text(results_text, encoding="utf-8")

    payload = {
        "data_files": [str(path.relative_to(ROOT)) for path in data_paths],
        "data_triples": len(data_graph),
        "shape_results": shape_results,
        "conforms": all(item["conforms"] for item in shape_results.values()),
    }
    (out_dir / "shacl_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# AGENT-O SHACL Validation Summary",
        "",
        f"- Data triples: `{payload['data_triples']}`",
        f"- Shape files: `{len(shape_results)}`",
        f"- Conforms: `{payload['conforms']}`",
        "",
        "| Shape file | Conforms | Results | Severities |",
        "| --- | --- | ---: | --- |",
    ]
    for name, item in shape_results.items():
        severities = ", ".join(f"{key}: {value}" for key, value in sorted(item["severity_counts"].items())) or "none"
        lines.append(f"| `{name}` | `{item['conforms']}` | {item['result_count']} | {severities} |")
    lines.extend([
        "",
        "## Notes",
        "",
        "- Warning-level findings, if present, are treated as profile findings for missing or partial reporting/governance coverage.",
        "- The current result table reports whether any such findings were detected.",
    ])
    (out_dir / "shacl_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({k: payload[k] for k in ["conforms", "data_triples"]}, indent=2))
    raise SystemExit(0 if payload["conforms"] else 1)


if __name__ == "__main__":
    main()
