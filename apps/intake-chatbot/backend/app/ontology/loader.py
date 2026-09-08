from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml
from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import OWL


SH = Namespace("http://www.w3.org/ns/shacl#")
REPORT = Namespace("https://w3id.org/agent-o/reporting#")
PROFILE = Namespace("https://w3id.org/agent-o/profiles#")


@dataclass(frozen=True)
class ShapeConstraint:
    shape_uri: str
    target_class: str
    path: str
    min_count: int | None
    max_count: int | None
    datatype: str | None
    value_class: str | None
    node_kind: str | None
    allowed_values: list[str]
    pattern: str | None
    severity: str
    message: str
    group: str | None
    order: float | None
    source_file: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _local_name(value: URIRef | BNode | Literal | None) -> str:
    if value is None:
        return ""
    text = str(value)
    return text.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def _first(graph: Graph, subject: Any, predicate: URIRef) -> Any | None:
    return next(iter(graph.objects(subject, predicate)), None)


def _rdf_list(graph: Graph, head: Any | None) -> list[str]:
    if head is None:
        return []
    values: list[str] = []
    cursor = head
    visited: set[Any] = set()
    while cursor and cursor != RDF.nil and cursor not in visited:
        visited.add(cursor)
        value = _first(graph, cursor, RDF.first)
        if value is not None:
            values.append(str(value))
        cursor = _first(graph, cursor, RDF.rest)
    return values


def _path_text(graph: Graph, path: Any | None) -> str:
    if path is None:
        return ""
    if isinstance(path, URIRef):
        return str(path)
    sequence = _rdf_list(graph, path)
    return " / ".join(sequence) if sequence else str(path)


class OntologyBundle:
    """Loads an immutable snapshot of AGENT-O, its profiles, and SHACL shapes."""

    module_names = (
        "agento-core.ttl",
        "agento-doc.ttl",
        "agento-eval.ttl",
        "agento-gov.ttl",
        "agento-health.ttl",
        "agento-report.ttl",
    )

    def __init__(self, project_root: Path, agent_o_root: Path):
        self.project_root = project_root.resolve()
        self.agent_o_root = agent_o_root.resolve()
        self.manifest_path = self.project_root / "config" / "profile_manifest.yaml"
        self.manifest = yaml.safe_load(self.manifest_path.read_text(encoding="utf-8"))
        self.integrated_path = self.agent_o_root / self.manifest["profile"]["ontology_integrated"]
        self.module_paths = [
            self.agent_o_root / "ontology" / "modules" / name for name in self.module_names
        ]
        self.profile_paths = [
            self.agent_o_root / path for path in self.manifest["profile"]["profile_files"]
        ]
        self.shape_paths = [
            self.agent_o_root / path for path in self.manifest["profile"]["shape_files"]
        ]
        self._ensure_files()

        self.ontology_graph = Graph()
        self.ontology_graph.parse(self.integrated_path, format="turtle")
        for path in self.profile_paths:
            self.ontology_graph.parse(path, format="turtle")

        self.shapes_graph = Graph()
        self.shape_source: dict[str, str] = {}
        for path in self.shape_paths:
            graph = Graph().parse(path, format="turtle")
            self.shapes_graph += graph
            for shape in graph.subjects(RDF.type, SH.NodeShape):
                self.shape_source[str(shape)] = path.name

        self.allowed_uris = self._build_allow_list()
        self.constraints = self._read_constraints()
        self.shacl_path_uris = {
            str(value)
            for value in self.shapes_graph.objects(None, SH.path)
            if isinstance(value, URIRef)
        }
        self.required_sections, self.recommended_sections = self._read_sections()
        self.snapshot = self._snapshot()

    def _ensure_files(self) -> None:
        required = [
            self.manifest_path,
            self.integrated_path,
            *self.module_paths,
            *self.profile_paths,
            *self.shape_paths,
        ]
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise FileNotFoundError("Missing AGENT-O assets: " + ", ".join(missing))

    def _build_allow_list(self) -> set[str]:
        entity_types = (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty)
        allowed = {
            str(subject)
            for entity_type in entity_types
            for subject in self.ontology_graph.subjects(RDF.type, entity_type)
            if isinstance(subject, URIRef)
        }
        for predicate in self.ontology_graph.predicates():
            if isinstance(predicate, URIRef):
                allowed.add(str(predicate))
        for subject in self.ontology_graph.subjects():
            if isinstance(subject, URIRef):
                allowed.add(str(subject))
        allowed.update(str(value) for value in (RDF.type, RDFS.label))
        return allowed

    def _read_constraints(self) -> list[ShapeConstraint]:
        constraints: list[ShapeConstraint] = []
        for shape in self.shapes_graph.subjects(RDF.type, SH.NodeShape):
            targets = list(self.shapes_graph.objects(shape, SH.targetClass)) or [None]
            properties = list(self.shapes_graph.objects(shape, SH.property))
            for target in targets:
                for prop in properties:
                    min_value = _first(self.shapes_graph, prop, SH.minCount)
                    max_value = _first(self.shapes_graph, prop, SH.maxCount)
                    order_value = _first(self.shapes_graph, prop, SH.order)
                    constraints.append(
                        ShapeConstraint(
                            shape_uri=str(shape),
                            target_class=str(target or ""),
                            path=_path_text(self.shapes_graph, _first(self.shapes_graph, prop, SH.path)),
                            min_count=int(min_value) if min_value is not None else None,
                            max_count=int(max_value) if max_value is not None else None,
                            datatype=str(_first(self.shapes_graph, prop, SH.datatype) or "") or None,
                            value_class=str(_first(self.shapes_graph, prop, SH["class"]) or "") or None,
                            node_kind=str(_first(self.shapes_graph, prop, SH.nodeKind) or "") or None,
                            allowed_values=_rdf_list(
                                self.shapes_graph, _first(self.shapes_graph, prop, SH["in"])
                            ),
                            pattern=str(_first(self.shapes_graph, prop, SH.pattern) or "") or None,
                            severity=_local_name(
                                _first(self.shapes_graph, prop, SH.severity)
                                or _first(self.shapes_graph, shape, SH.severity)
                                or SH.Violation
                            ),
                            message=str(
                                _first(self.shapes_graph, prop, SH.message)
                                or _first(self.shapes_graph, shape, SH.message)
                                or ""
                            ),
                            group=str(_first(self.shapes_graph, prop, SH.group) or "") or None,
                            order=float(order_value) if order_value is not None else None,
                            source_file=self.shape_source.get(str(shape), "combined-shapes"),
                        )
                    )
        return constraints

    def _read_sections(self) -> tuple[list[str], list[str]]:
        profile_node = PROFILE.ReportingProfile
        required = sorted(
            str(value) for value in self.ontology_graph.objects(profile_node, REPORT.requiresReportingSection)
        )
        recommended = sorted(
            str(value)
            for value in self.ontology_graph.objects(profile_node, REPORT.recommendedReportingSection)
        )
        return required, recommended

    def _snapshot(self) -> dict[str, Any]:
        files = [self.integrated_path, *self.module_paths, *self.profile_paths, *self.shape_paths]
        hashes = {str(path.relative_to(self.agent_o_root)): sha256_file(path) for path in files}
        combined = hashlib.sha256(
            "".join(f"{key}:{hashes[key]}\n" for key in sorted(hashes)).encode("utf-8")
        ).hexdigest()
        return {
            "id": combined[:16],
            "catalog_version": self.manifest["profile"]["version"],
            "root": str(self.agent_o_root),
            "hashes": hashes,
            "combined_sha256": combined,
            "integrated_triples": len(Graph().parse(self.integrated_path, format="turtle")),
        }

    def status(self) -> dict[str, Any]:
        return {
            "loaded": True,
            "snapshot_id": self.snapshot["id"],
            "profile_uri": self.manifest["profile"]["uri"],
            "profile_version": self.manifest["profile"]["version"],
            "integrated_triples": self.snapshot["integrated_triples"],
            "allowed_uri_count": len(self.allowed_uris),
            "shape_constraint_count": len(self.constraints),
            "required_section_count": len(self.required_sections),
            "recommended_section_count": len(self.recommended_sections),
        }

    def constraint_dicts(self) -> list[dict[str, Any]]:
        return [asdict(item) for item in self.constraints]

    def term_label(self, uri: str) -> str:
        value = _first(self.ontology_graph, URIRef(uri), RDFS.label)
        return str(value or "")

    def term_comment(self, uri: str) -> str:
        value = _first(self.ontology_graph, URIRef(uri), RDFS.comment)
        return str(value or "")

    def shape_messages(self, predicate_uri: str) -> list[str]:
        return [
            item.message
            for item in self.constraints
            if item.path == predicate_uri and item.message
        ]

    def assert_allowed(self, uris: Iterable[str]) -> None:
        unknown = sorted({uri for uri in uris if uri not in self.allowed_uris})
        if unknown:
            raise ValueError("Unknown ontology URI(s): " + ", ".join(unknown))
