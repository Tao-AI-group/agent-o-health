from __future__ import annotations

from typing import Any

from pyshacl import validate
from rdflib import Graph, Namespace, RDF

from app.ontology.loader import OntologyBundle


SH = Namespace("http://www.w3.org/ns/shacl#")


def validate_graph(graph: Graph, ontology: OntologyBundle) -> dict[str, Any]:
    conforms, report_graph, report_text = validate(
        data_graph=graph,
        shacl_graph=ontology.shapes_graph,
        ont_graph=ontology.ontology_graph,
        inference="owlrl",
        advanced=True,
        meta_shacl=False,
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
    )
    results = []
    for result in report_graph.subjects(RDF.type, SH.ValidationResult):
        severity = next(iter(report_graph.objects(result, SH.resultSeverity)), None)
        focus = next(iter(report_graph.objects(result, SH.focusNode)), None)
        path = next(iter(report_graph.objects(result, SH.resultPath)), None)
        value = next(iter(report_graph.objects(result, SH.value)), None)
        message = next(iter(report_graph.objects(result, SH.resultMessage)), None)
        source_shape = next(iter(report_graph.objects(result, SH.sourceShape)), None)
        results.append(
            {
                "severity": str(severity).rsplit("#", 1)[-1] if severity else "Violation",
                "focus_node": str(focus or ""),
                "path": str(path or ""),
                "value": str(value or ""),
                "message": str(message or "Validation constraint was not satisfied."),
                "source_shape": str(source_shape or ""),
            }
        )
    results.sort(key=lambda item: (item["severity"], item["focus_node"], item["path"], item["message"]))
    return {
        "conforms": bool(conforms),
        "results": results,
        "summary": {
            "Violation": sum(item["severity"] == "Violation" for item in results),
            "Warning": sum(item["severity"] == "Warning" for item in results),
            "Info": sum(item["severity"] == "Info" for item in results),
        },
        "engine": "pySHACL",
        "report_text": report_text,
    }
