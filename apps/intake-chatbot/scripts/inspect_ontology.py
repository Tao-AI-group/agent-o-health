#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from app.config import PROJECT_ROOT, Settings
from app.ontology.loader import OntologyBundle


def git_value(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or "unavailable"


def render_report(bundle: OntologyBundle) -> str:
    status = git_value(bundle.agent_o_root / "release" / "agent-o-health", "status", "--short", "--branch")
    commit = git_value(bundle.agent_o_root / "release" / "agent-o-health", "rev-parse", "HEAD")
    lines = [
        "# AGENT-O Intake Discovery Report",
        "",
        "**Generated from the current read-only AGENT-O source.**",
        "",
        "## Source State",
        "",
        f"- AGENT-O root: `{bundle.agent_o_root}`",
        f"- Public release branch/status: `{status}`",
        f"- Public release commit: `{commit}`",
        f"- Integrated ontology: `{bundle.integrated_path}`",
        f"- Integrated triples: `{bundle.snapshot['integrated_triples']}`",
        f"- Snapshot ID: `{bundle.snapshot['id']}`",
        f"- Combined snapshot SHA-256: `{bundle.snapshot['combined_sha256']}`",
        "",
        "The six module files are authoritative. The integrated ontology is a generated read-only input for this application. Historical ACRO files and figure-only reduced TTL files are excluded.",
        "",
        "## Authoritative Modules",
        "",
        "| Module | SHA-256 |",
        "| --- | --- |",
    ]
    for path in bundle.module_paths:
        key = str(path.relative_to(bundle.agent_o_root))
        lines.append(f"| `{key}` | `{bundle.snapshot['hashes'][key]}` |")
    lines.extend(
        [
            "",
            "## Profile Contract",
            "",
            f"- Profile ID: `{bundle.manifest['profile']['id']}`",
            f"- Profile URI: `{bundle.manifest['profile']['uri']}`",
            f"- Profile version: `{bundle.manifest['profile']['version']}`",
            f"- Root report class: `{bundle.manifest['profile']['root_report_class']}`",
            f"- Root described-system class: `{bundle.manifest['profile']['root_system_class']}`",
            f"- Report-to-system property: `{bundle.manifest['profile']['report_to_system_property']}`",
            "",
            "### Required reporting sections",
            "",
        ]
    )
    lines.extend(f"- `{item}`" for item in bundle.required_sections)
    lines.extend(["", "### Recommended reporting sections", ""])
    lines.extend(f"- `{item}`" for item in bundle.recommended_sections)
    lines.extend(
        [
            "",
            "## SHACL Requirement Catalog",
            "",
            "| Shape | Target class | Path | Min | Max | Value constraint | Severity | Message | Source |",
            "| --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
        ]
    )
    for item in bundle.constraints:
        value = item.datatype or item.value_class or item.node_kind or ", ".join(item.allowed_values) or ""
        message = item.message.replace("|", "\\|")
        lines.append(
            f"| `{item.shape_uri}` | `{item.target_class}` | `{item.path}` | "
            f"{item.min_count if item.min_count is not None else ''} | "
            f"{item.max_count if item.max_count is not None else ''} | `{value}` | "
            f"{item.severity} | {message} | `{item.source_file}` |"
        )
    lines.extend(
        [
            "",
            "No current property shape declares `sh:group`, `sh:order`, `sh:in`, or `sh:pattern`; the loader nevertheless preserves these fields when future snapshots add them. Composite `sh:or` and SPARQL constraints remain available to pySHACL and are not reduced to property rows above.",
            "",
            "## Conversational Section Map",
            "",
            "The UI groups ontology requirements into the following conversational sections. These groups are navigation aids and do not replace ontology classes or SHACL paths.",
            "",
            "| Order | Section | Description |",
            "| ---: | --- | --- |",
        ]
    )
    for section in sorted(bundle.manifest["sections"], key=lambda value: value["order"]):
        lines.append(f"| {section['order']} | {section['label']} | {section['description']} |")
    lines.extend(
        [
            "",
            "## Applicability and N/A",
            "",
            "The Agent Card profile is intended for a concrete existing or planned agent system. Required SHACL paths are applicable whenever their target entity is instantiated. A user may mark an intake requirement not applicable only with a recorded reason; that workflow decision is stored separately from RDF completeness labels. No profile rule silently assigns N/A. Optional five-dimension scoring excludes confirmed N/A requirements from its denominator.",
            "",
            "## Golden Fixtures",
            "",
            "- `data/examples/converted_test_agent_annotations.ttl`: broad architecture/reporting fixture.",
            "- `data/examples/governance_reporting_profile_example.ttl`: governance and reporting fixture.",
            "- `data/examples/health_interoperability_example.ttl`: clinical/FHIR fixture.",
            "- `data/examples/prov_decision_trace_example.ttl`: provenance trace fixture.",
            "",
            "The chatbot uses synthetic data derived from these patterns. It does not modify or redistribute source-paper content.",
            "",
            "## LLM and Credential Integration",
            "",
            "The existing `agent-o/scripts/run_llm_reverse_validation.py` provides a reusable credential-record loader, OAuth client-credentials token refresh pattern, retry behavior, and OpenAI-compatible chat payload. This application reimplements those behaviors behind an `LLMClient` protocol and redacts all errors. Credential values are loaded only at runtime and are never included in this report, the database, logs, frontend responses, or exports.",
            "",
            "Streaming, JSON-schema response format, and tool-calling support are gateway/deployment capabilities that still require an explicitly enabled synthetic live smoke test. The default provider is the deterministic mock and health checks never call the gateway.",
            "",
            "## Expert Confirmation Items",
            "",
            "- Confirm whether every one of the 18 reporting-profile sections should block a conformant export or whether some should remain reporting-completeness requirements only.",
            "- Confirm organization/person modeling for model developers and deployment providers, because the current range is `core:Agent`.",
            "- Confirm institution-specific retention, authentication, PHI handling, and gateway model/deployment settings before a real internal pilot.",
            "- Confirm whether reporting assessments should be embedded in every exported Agent Card or remain in the separate validation report for the MVP.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Parse and verify the configured ontology bundle")
    parser.add_argument("--write-report", action="store_true", help="Write docs/DISCOVERY_REPORT.md")
    args = parser.parse_args()
    settings = Settings(app_host="127.0.0.1")
    bundle = OntologyBundle(PROJECT_ROOT, settings.agent_o_root)
    if args.write_report:
        output = PROJECT_ROOT / "docs" / "DISCOVERY_REPORT.md"
        output.write_text(render_report(bundle), encoding="utf-8")
        print(f"Wrote {output}")
    print(
        f"AGENT-O snapshot {bundle.snapshot['id']}: "
        f"{bundle.snapshot['integrated_triples']} triples, "
        f"{len(bundle.constraints)} property constraints, "
        f"{len(bundle.allowed_uris)} allowed URIs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
