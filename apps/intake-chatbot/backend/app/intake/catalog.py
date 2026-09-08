from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import yaml

from app.ontology.loader import OntologyBundle


@dataclass(frozen=True)
class FieldDefinition:
    id: str
    section: str
    label: str
    question: str
    subject: str
    predicate_uri: str
    object_kind: str
    required: bool
    source: str
    datatype_uri: str | None = None
    object_type_uri: str | None = None
    help: str = ""


class IntakeCatalog:
    def __init__(
        self,
        path: Path,
        ontology: OntologyBundle,
        question_overrides_path: Path | None = None,
    ):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        overrides = {}
        if question_overrides_path:
            override_data = yaml.safe_load(question_overrides_path.read_text(encoding="utf-8"))
            overrides = (override_data or {}).get("questions", {})
        self.fields = [self._build_field(item, ontology, overrides) for item in raw["fields"]]
        self.by_id = {item.id: item for item in self.fields}
        if len(self.by_id) != len(self.fields):
            raise ValueError("Duplicate intake field IDs")
        invalid_sources = sorted({item.source for item in self.fields} - {"profile", "shacl"})
        if invalid_sources:
            raise ValueError("Unknown intake field source(s): " + ", ".join(invalid_sources))
        ontology.assert_allowed(
            uri
            for item in self.fields
            for uri in (item.predicate_uri, item.object_type_uri, item.datatype_uri)
            if uri and uri.startswith("https://w3id.org/agent-o/")
        )
        self._validate_shacl_contract(ontology)

    @staticmethod
    def _humanize(value: str) -> str:
        local = value.rsplit("#", 1)[-1].rsplit("/", 1)[-1]
        spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", local).replace("_", " ").strip()
        if spaced.lower().startswith("has "):
            spaced = spaced[4:]
        return spaced[:1].upper() + spaced[1:]

    @classmethod
    def _build_field(
        cls,
        raw: dict[str, Any],
        ontology: OntologyBundle,
        overrides: dict[str, Any],
    ) -> FieldDefinition:
        item = dict(raw)
        predicate_uri = item["predicate_uri"]
        override = overrides.get(predicate_uri, {})
        ontology_label = ontology.term_label(predicate_uri)
        item["label"] = item.get("label") or cls._humanize(ontology_label or predicate_uri)
        item["help"] = item.get("help") or override.get("help", "") or ontology.term_comment(predicate_uri)
        if not item.get("question"):
            shape_message = next(iter(ontology.shape_messages(predicate_uri)), "")
            item["question"] = (
                override.get("prompt")
                or (f"{shape_message.rstrip('.')} What should the Card record?" if shape_message else "")
                or (f"What should the Card record for {item['label'].lower()}?")
            )
        return FieldDefinition(**item)

    def _validate_shacl_contract(self, ontology: OntologyBundle) -> None:
        for field in self.fields:
            if field.source != "shacl":
                continue
            if field.predicate_uri not in ontology.shacl_path_uris:
                raise ValueError(
                    f"SHACL-backed intake field {field.id} does not match a loaded sh:path"
                )
            direct = [
                item for item in ontology.constraints if item.path == field.predicate_uri
            ]
            if any((item.min_count or 0) > 0 for item in direct) and not field.required:
                raise ValueError(f"SHACL-required intake field {field.id} is marked optional")
            datatypes = {item.datatype for item in direct if item.datatype}
            if datatypes and field.datatype_uri not in datatypes:
                raise ValueError(f"Datatype mismatch for SHACL-backed field {field.id}")
            value_classes = {item.value_class for item in direct if item.value_class}
            if value_classes and field.object_type_uri not in value_classes:
                raise ValueError(f"Class mismatch for SHACL-backed field {field.id}")

    def section_fields(self, section: str) -> list[FieldDefinition]:
        return [field for field in self.fields if field.section == section]

    def public(self) -> list[dict[str, Any]]:
        return [
            {
                "id": field.id,
                "section": field.section,
                "label": field.label,
                "question": field.question,
                "required": field.required,
                "source": field.source,
                "ontology_term": field.predicate_uri,
                "help": field.help,
            }
            for field in self.fields
        ]
