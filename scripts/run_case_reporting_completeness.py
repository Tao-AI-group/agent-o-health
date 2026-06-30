#!/usr/bin/env python3
"""Aggregate reporting-completeness gaps and score paper completeness cases."""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

VENDOR_PATH = Path("/tmp/rdflib_validate")
if VENDOR_PATH.exists():
    sys.path.insert(0, str(VENDOR_PATH))

try:
    from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "rdflib is required. Run with PYTHONPATH=/tmp/rdflib_validate or install requirements.txt."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]

CORE = Namespace("https://w3id.org/agent-o/core#")
DOC = Namespace("https://w3id.org/agent-o/doc#")
EVAL = Namespace("https://w3id.org/agent-o/eval#")
GOV = Namespace("https://w3id.org/agent-o/gov#")
HEALTH = Namespace("https://w3id.org/agent-o/health#")
REPORT = Namespace("https://w3id.org/agent-o/reporting#")

EVAL_DEMO = Namespace("https://w3id.org/agent-o/examples/eval-demo#")
GOV_REPORT_EX = Namespace("https://w3id.org/agent-o/examples/governance-reporting-profile#")

LABEL_SCORES = {
    str(REPORT.Present): 1.0,
    str(REPORT.Partial): 0.5,
    str(REPORT.Missing): 0.0,
    str(REPORT.NotApplicable): None,
}

DIMENSIONS = [
    {
        "id": "runtime_architecture",
        "name": "Runtime/architecture",
        "weight": 25,
        "section_classes": {
            REPORT.AgentIdentityScopeSection,
            REPORT.RuntimeArchitectureSection,
            REPORT.ModelComponentsSection,
            REPORT.ToolUseSection,
            REPORT.WorkflowSection,
            REPORT.PlanningReasoningSection,
            REPORT.InputOutputDataSection,
            REPORT.ClinicalContextSection,
        },
    },
    {
        "id": "evaluation",
        "name": "Evaluation",
        "weight": 25,
        "section_classes": {
            REPORT.EvaluationReportingSection,
            REPORT.DatasetsMetricsSection,
            REPORT.SubgroupEquityEvaluationSection,
        },
    },
    {
        "id": "provenance_reproducibility",
        "name": "Provenance/reproducibility",
        "weight": 20,
        "section_classes": {
            REPORT.ReproducibilitySection,
        },
    },
    {
        "id": "governance_safety",
        "name": "Governance/safety",
        "weight": 20,
        "section_classes": {
            REPORT.GovernanceReportingSection,
            REPORT.HumanReviewSection,
            REPORT.RiskUncertaintySection,
            REPORT.PrivacySecurityComplianceSection,
            REPORT.DeploymentMonitoringSection,
            REPORT.FailureFallbackSection,
            REPORT.DataUseSection,
        },
    },
    {
        "id": "benchmark_process_alignment",
        "name": "Benchmark-process alignment",
        "weight": 10,
        "section_classes": {
            EVAL.BenchmarkTask,
            REPORT.EvaluationReportingSection,
        },
    },
]

DIMENSIONS_BY_SECTION_CLASS: dict[str, list[str]] = {}
for dimension in DIMENSIONS:
    for section_class in dimension["section_classes"]:
        DIMENSIONS_BY_SECTION_CLASS.setdefault(str(section_class), []).append(dimension["id"])


@dataclass(frozen=True)
class TargetCase:
    paper_id: str
    name: str
    agent: URIRef
    report: URIRef | None
    note: str


TARGETS = [
    TargetCase(
        "agentarena",
        "AgentArena benchmark-alignment case",
        GOV_REPORT_EX.AgentArenaBenchmarkDescription,
        GOV_REPORT_EX.AgentArenaPOCReport,
        "Benchmark-alignment case grounded in the AgentArena POC annotations.",
    ),
    TargetCase(
        "trial_simulation_agent",
        "Trial Simulation Assistance Tool",
        EVAL_DEMO.TrialSimulationAgent,
        None,
        "Clinical cohort-construction agent from the prior ACRO evaluation examples.",
    ),
    TargetCase(
        "medagent_pro",
        "MedAgent-Pro",
        EVAL_DEMO.MedAgentPro,
        None,
        "Single-agent multimodal diagnostic reasoning workflow from the prior ACRO evaluation examples.",
    ),
    TargetCase(
        "consensus_matrix_system",
        "Multi-Agent Medical Decision Consensus Matrix System",
        EVAL_DEMO.ConsensusMatrixSystem,
        None,
        "Multi-agent clinical consensus framework from the prior ACRO evaluation examples.",
    ),
]


def ttl_inputs() -> list[Path]:
    paths = [ROOT / "ontology" / "agento.ttl"]
    paths.extend(sorted((ROOT / "ontology" / "alignments").glob("*.ttl")))
    paths.extend(sorted((ROOT / "ontology" / "profiles").glob("*.ttl")))
    paths.extend(sorted((ROOT / "data" / "examples").glob("*.ttl")))
    return [path for path in paths if path.exists()]


def load_graph() -> Graph:
    graph = Graph()
    graph.bind("core", CORE)
    graph.bind("doc", DOC)
    graph.bind("eval", EVAL)
    graph.bind("gov", GOV)
    graph.bind("health", HEALTH)
    graph.bind("report", REPORT)
    for path in ttl_inputs():
        graph.parse(path, format="turtle")
    return graph


def qname(graph: Graph, term) -> str:
    if term is None:
        return ""
    try:
        return graph.namespace_manager.normalizeUri(term)
    except Exception:
        return str(term)


def local_name(term) -> str:
    text = str(term)
    if "#" in text:
        return text.rsplit("#", 1)[1]
    return text.rstrip("/").rsplit("/", 1)[-1]


def text_value(graph: Graph, subject, predicate) -> str | None:
    value = next(graph.objects(subject, predicate), None)
    return str(value) if value is not None else None


def label(graph: Graph, term) -> str:
    if term is None:
        return ""
    for predicate in [CORE.hasName, RDFS.label]:
        value = text_value(graph, term, predicate)
        if value:
            return value
    return local_name(term)


def objects(graph: Graph, subject, predicate) -> list:
    return sorted(set(graph.objects(subject, predicate)), key=str)


def subjects(graph: Graph, predicate, obj) -> list:
    return sorted(set(graph.subjects(predicate, obj)), key=str)


def yes_no(values: Iterable) -> bool:
    return bool(list(values))


def generated_actions(graph: Graph, agent: URIRef) -> list:
    return objects(graph, agent, CORE.generates)


def evaluation_studies(graph: Graph, agent: URIRef) -> list:
    return subjects(graph, EVAL.evaluates, agent)


def evidence_list(graph: Graph, title: str, terms: Iterable, limit: int = 4) -> list[str]:
    values = [label(graph, term) for term in terms]
    values = [value for value in values if value]
    if not values:
        return []
    suffix = "" if len(values) <= limit else f"; +{len(values) - limit} more"
    return [f"{title}: {', '.join(values[:limit])}{suffix}."]


def label_from_score(value: float | None) -> str:
    if value is None:
        return "not_applicable"
    if value >= 0.9:
        return "present"
    if value > 0:
        return "partial"
    return "missing"


def score_from_label_uri(label_uri: URIRef) -> float | None:
    return LABEL_SCORES.get(str(label_uri), 0.0)


def explicit_assessments(graph: Graph, target: TargetCase) -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {dimension["id"]: [] for dimension in DIMENSIONS}
    if target.report is None:
        return results

    for assessment in subjects(graph, REPORT.assessesReport, target.report):
        section = next(graph.objects(assessment, REPORT.assessesSection), None)
        label_uri = next(graph.objects(assessment, REPORT.hasCompletenessLabel), None)
        if section is None or label_uri is None:
            continue
        dimension_ids = []
        for section_type in graph.objects(section, RDF.type):
            dimension_ids.extend(DIMENSIONS_BY_SECTION_CLASS.get(str(section_type), []))
        dimension_ids = sorted(set(dimension_ids))
        if not dimension_ids:
            continue
        item = {
            "assessment": str(assessment),
            "section": label(graph, section),
            "label": local_name(label_uri).lower(),
            "score": score_from_label_uri(label_uri),
            "evidence": text_value(graph, assessment, REPORT.hasEvidenceQuote),
            "gap": text_value(graph, assessment, REPORT.hasGapExplanation),
            "recommendation": text_value(graph, assessment, REPORT.hasRecommendedFix),
        }
        for dimension_id in dimension_ids:
            results[dimension_id].append(dict(item))
    return results


def report_sections(graph: Graph, target: TargetCase, dimension_id: str) -> list:
    if target.report is None:
        return []
    dimension = next(item for item in DIMENSIONS if item["id"] == dimension_id)
    sections = []
    for section in objects(graph, target.report, REPORT.hasReportingSection):
        if any((section, RDF.type, section_class) in graph for section_class in dimension["section_classes"]):
            sections.append(section)
    return sections


def infer_runtime(graph: Graph, target: TargetCase) -> dict:
    agent = target.agent
    evidence = []
    feature_count = 0
    feature_groups = [
        ("workflow", objects(graph, agent, CORE.hasWorkflow)),
        ("tools", objects(graph, agent, CORE.usesTool)),
        ("capabilities", objects(graph, agent, CORE.hasCapability)),
        ("planner", objects(graph, agent, CORE.usesPlanner)),
        ("reasoner", objects(graph, agent, CORE.usesReasoner)),
        ("memory", objects(graph, agent, CORE.usesMemory)),
        ("environment", objects(graph, agent, CORE.operatesIn)),
        ("generated actions", generated_actions(graph, agent)),
        ("sub-agents", objects(graph, agent, CORE.invokesAgent) + objects(graph, agent, CORE.coordinatesWith)),
    ]
    for title, values in feature_groups:
        if values:
            feature_count += 1
            evidence.extend(evidence_list(graph, title, values))
    if feature_count >= 3:
        score = 1.0
    elif feature_count > 0:
        score = 0.5
    else:
        score = 0.0
    return {
        "score": score,
        "evidence": evidence or ["No runtime architecture, workflow, tool, model, or execution evidence found in the current annotation."],
        "gap": None if score == 1.0 else "Runtime architecture needs more explicit workflow, tool, environment, model, memory, or execution-step detail.",
    }


def infer_evaluation(graph: Graph, target: TargetCase) -> dict:
    studies = evaluation_studies(graph, target.agent)
    datasets = []
    results = []
    metrics = []
    for study in studies:
        datasets.extend(objects(graph, study, EVAL.usesDataset))
        results.extend(objects(graph, study, EVAL.producesResult))
    for result in results:
        metrics.extend(objects(graph, result, EVAL.forMetric))
    evidence = []
    evidence.extend(evidence_list(graph, "evaluation studies", studies))
    evidence.extend(evidence_list(graph, "datasets", datasets))
    evidence.extend(evidence_list(graph, "metric results", results))
    evidence.extend(evidence_list(graph, "metrics", metrics))
    if studies and datasets and results:
        score = 1.0
    elif studies or datasets or results:
        score = 0.5
    else:
        score = 0.0
    return {
        "score": score,
        "evidence": evidence or ["No evaluation study, dataset, metric, or result evidence found in the current annotation."],
        "gap": None if score == 1.0 else "Evaluation coverage should specify benchmark tasks, datasets, baselines, metrics, results, and error analysis.",
    }


def infer_provenance(graph: Graph, target: TargetCase) -> dict:
    agent = target.agent
    traces = objects(graph, agent, DOC.hasLineageTrace)
    provenance = objects(graph, agent, DOC.hasProvenanceRecord)
    references = objects(graph, agent, DOC.hasReference)
    action_traces = []
    for action in generated_actions(graph, agent):
        action_traces.extend(objects(graph, action, DOC.hasLineageTrace))
    workflows = objects(graph, agent, CORE.hasWorkflow)
    evidence = []
    evidence.extend(evidence_list(graph, "lineage traces", traces + action_traces))
    evidence.extend(evidence_list(graph, "provenance records", provenance))
    evidence.extend(evidence_list(graph, "references", references))
    evidence.extend(evidence_list(graph, "workflows", workflows))
    if (traces or action_traces) and (provenance or references or workflows):
        score = 1.0
    elif traces or action_traces or provenance or references or workflows:
        score = 0.5
    else:
        score = 0.0
    return {
        "score": score,
        "evidence": evidence or ["No lineage, provenance, reference, or reproducibility artifact evidence found in the current annotation."],
        "gap": None if score == 1.0 else "Reproducibility coverage should include lineage traces, source artifacts, versioned tools, provenance records, and rerun instructions.",
    }


def infer_governance(graph: Graph, target: TargetCase) -> dict:
    agent = target.agent
    actions = generated_actions(graph, agent)
    review_requirements = []
    confidences = []
    uncertainties = []
    for action in actions:
        review_requirements.extend(objects(graph, action, GOV.requiresReview))
        confidences.extend(objects(graph, action, GOV.hasConfidenceScore))
        uncertainties.extend(objects(graph, action, GOV.hasUncertainty))
    policies = subjects(graph, GOV.constrains, agent)
    escalations = []
    fallbacks = []
    overrides = []
    for policy in policies:
        escalations.extend(objects(graph, policy, GOV.triggersEscalation))
        fallbacks.extend(objects(graph, policy, GOV.hasFallbackStrategy))
        overrides.extend(objects(graph, policy, GOV.enablesOverride))
    feature_groups = [
        ("automation level", objects(graph, agent, GOV.hasAutomationLevel)),
        ("human review", review_requirements),
        ("policies", policies),
        ("risks", objects(graph, agent, GOV.hasRisk)),
        ("privacy constraints", objects(graph, agent, GOV.hasPrivacyConstraint)),
        ("compliance requirements", objects(graph, agent, GOV.requiresCompliance)),
        ("escalation events", escalations),
        ("fallback strategies", fallbacks),
        ("monitoring rules", objects(graph, agent, GOV.monitoredBy)),
        ("confidence scores", confidences),
        ("uncertainties", uncertainties),
        ("override actions", overrides),
    ]
    evidence = []
    present = 0
    for title, values in feature_groups:
        if values:
            present += 1
            evidence.extend(evidence_list(graph, title, values))
    if present >= 5:
        score = 1.0
    elif present >= 2:
        score = 0.5
    elif present == 1:
        score = 0.25
    else:
        score = 0.0
    return {
        "score": score,
        "evidence": evidence or ["No governance, review, risk, privacy, compliance, fallback, or monitoring evidence found in the current annotation."],
        "gap": None if score == 1.0 else "Governance coverage should define accountability, automation level, review authority, risks, fallback, escalation, monitoring, privacy, and compliance.",
    }


def infer_benchmark(graph: Graph, target: TargetCase) -> dict:
    studies = evaluation_studies(graph, target.agent)
    datasets = []
    results = []
    metrics = []
    benchmark_tasks = []
    for study in studies:
        datasets.extend(objects(graph, study, EVAL.usesDataset))
        results.extend(objects(graph, study, EVAL.producesResult))
        benchmark_tasks.extend(objects(graph, study, EVAL.hasBenchmarkTask))
    for result in results:
        metrics.extend(objects(graph, result, EVAL.forMetric))
    evidence = []
    evidence.extend(evidence_list(graph, "benchmark/evaluation studies", studies))
    evidence.extend(evidence_list(graph, "benchmark datasets", datasets))
    evidence.extend(evidence_list(graph, "benchmark metrics", metrics))
    evidence.extend(evidence_list(graph, "benchmark tasks", benchmark_tasks))
    if studies and datasets and metrics:
        score = 1.0
    elif studies or datasets or metrics or benchmark_tasks:
        score = 0.5
    else:
        score = 0.0
    return {
        "score": score,
        "evidence": evidence or ["No benchmark-process evidence found in the current annotation."],
        "gap": None if score == 1.0 else "Benchmark-process coverage should separate runtime from evaluation and report tasks, validity/refusal handling, reliability, stability, and cost.",
    }


INFER_DIMENSION = {
    "runtime_architecture": infer_runtime,
    "evaluation": infer_evaluation,
    "provenance_reproducibility": infer_provenance,
    "governance_safety": infer_governance,
    "benchmark_process_alignment": infer_benchmark,
}


def combine_explicit_and_inferred(graph: Graph, target: TargetCase, dimension: dict, explicit: list[dict]) -> dict:
    inferred = INFER_DIMENSION[dimension["id"]](graph, target)
    sections = report_sections(graph, target, dimension["id"])
    if explicit:
        scored = [item["score"] for item in explicit if item["score"] is not None]
        score = sum(scored) / len(scored) if scored else None
        evidence = [item["evidence"] for item in explicit if item.get("evidence")]
        gaps = [item["gap"] for item in explicit if item.get("gap")]
        recommendations = [item["recommendation"] for item in explicit if item.get("recommendation")]
        if sections and not evidence:
            evidence.extend(evidence_list(graph, "report sections", sections))
        return {
            "dimension_id": dimension["id"],
            "dimension": dimension["name"],
            "weight": dimension["weight"],
            "score_fraction": score,
            "weighted_score": round((score or 0.0) * dimension["weight"], 2),
            "label": label_from_score(score),
            "evidence": evidence or inferred["evidence"],
            "gap": None if score == 1.0 else ("; ".join(gaps) if gaps else inferred.get("gap")),
            "recommendation": "; ".join(recommendations) if recommendations else None,
            "basis": "explicit_assessment",
        }
    if sections:
        inferred = dict(inferred)
        inferred["evidence"] = evidence_list(graph, "report sections", sections) + inferred["evidence"]
        inferred["score"] = max(inferred["score"] or 0.0, 0.5)
    score = inferred["score"]
    return {
        "dimension_id": dimension["id"],
        "dimension": dimension["name"],
        "weight": dimension["weight"],
        "score_fraction": score,
        "weighted_score": round((score or 0.0) * dimension["weight"], 2),
        "label": label_from_score(score),
        "evidence": inferred["evidence"],
        "gap": inferred.get("gap"),
        "recommendation": None,
        "basis": "graph_inference",
    }


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_node(value: str | None) -> str | None:
    if not value:
        return None
    if value.startswith("<") and value.endswith(">"):
        return value[1:-1]
    return value


def collect_cq_gaps(cq_payload: dict) -> list[dict]:
    rows = cq_payload.get("queries", {}).get("cq_reporting_gaps", {}).get("rows", [])
    return [
        {
            "report": row.get("report"),
            "report_name": row.get("reportName"),
            "agent": row.get("agent"),
            "section": row.get("section"),
            "label": local_name(row.get("label", "")),
            "evidence": row.get("evidenceQuote"),
            "gap": row.get("gapExplanation"),
            "recommendation": row.get("recommendedFix"),
        }
        for row in rows
    ]


def collect_shacl_warnings(shacl_payload: dict, graph: Graph) -> list[dict]:
    warnings = []
    for shape_name, shape_result in shacl_payload.get("shape_results", {}).items():
        for result in shape_result.get("results", []):
            if "Warning" not in result.get("severity", ""):
                continue
            focus_uri = normalize_node(result.get("focus_node"))
            focus = URIRef(focus_uri) if focus_uri else None
            warnings.append(
                {
                    "shape": shape_name,
                    "focus": focus_uri,
                    "focus_label": label(graph, focus) if focus else "",
                    "message": result.get("message"),
                }
            )
    return warnings


def attach_target_warnings(target: TargetCase, warnings: list[dict]) -> list[dict]:
    focus_values = {str(target.agent)}
    if target.report is not None:
        focus_values.add(str(target.report))
    return [warning for warning in warnings if warning.get("focus") in focus_values]


def score_target(graph: Graph, target: TargetCase, shacl_warnings: list[dict]) -> dict:
    explicit = explicit_assessments(graph, target)
    dimensions = []
    for dimension in DIMENSIONS:
        dimensions.append(combine_explicit_and_inferred(graph, target, dimension, explicit[dimension["id"]]))
    total = round(sum(item["weighted_score"] for item in dimensions), 2)
    missing_or_partial = [
        item
        for item in dimensions
        if item["label"] in {"missing", "partial"} and item["score_fraction"] is not None
    ]
    return {
        "paper_id": target.paper_id,
        "name": target.name,
        "agent": str(target.agent),
        "agent_label": label(graph, target.agent),
        "report": str(target.report) if target.report else None,
        "note": target.note,
        "total_score": total,
        "max_score": sum(item["weight"] for item in DIMENSIONS),
        "dimensions": dimensions,
        "shacl_warnings": attach_target_warnings(target, shacl_warnings),
        "missing_or_partial_dimensions": missing_or_partial,
    }


def markdown_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return lines


def write_per_target_outputs(out_dir: Path, result: dict) -> None:
    (out_dir / f"{result['paper_id']}_completeness.json").write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )
    lines = [
        f"# {result['name']} Missing Information",
        "",
        f"- Agent: `{result['agent_label']}`",
        f"- Completeness score: `{result['total_score']}/{result['max_score']}`",
        "",
        "## Dimension Results",
        "",
    ]
    lines.extend(
        markdown_table(
            ["Dimension", "Label", "Weighted score", "Basis", "Gap"],
            [
                [
                    item["dimension"],
                    item["label"],
                    f"{item['weighted_score']}/{item['weight']}",
                    item["basis"],
                    item.get("gap") or "",
                ]
                for item in result["dimensions"]
            ],
        )
    )
    lines.extend(["", "## Missing Or Partial Items", ""])
    gaps = [item for item in result["dimensions"] if item["label"] in {"missing", "partial"}]
    if gaps:
        for item in gaps:
            lines.extend(
                [
                    f"### {item['dimension']}",
                    "",
                    f"- Label: `{item['label']}`",
                    f"- Gap: {item.get('gap') or 'No gap explanation available.'}",
                ]
            )
            if item.get("recommendation"):
                lines.append(f"- Recommended fix: {item['recommendation']}")
            if item.get("evidence"):
                lines.append(f"- Evidence: {item['evidence'][0]}")
            lines.append("")
    else:
        lines.append("No missing or partial dimensions were identified by the current rubric.")
    (out_dir / f"{result['paper_id']}_missing_info.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_scores_csv(out_dir: Path, results: list[dict]) -> None:
    fieldnames = [
        "paper_id",
        "name",
        "total_score",
        "runtime_architecture",
        "evaluation",
        "provenance_reproducibility",
        "governance_safety",
        "benchmark_process_alignment",
    ]
    with (out_dir / "completeness_scores.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            row = {
                "paper_id": result["paper_id"],
                "name": result["name"],
                "total_score": result["total_score"],
            }
            for item in result["dimensions"]:
                row[item["dimension_id"]] = item["weighted_score"]
            writer.writerow(row)
    (out_dir / "completeness_scores.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


def write_reporting_gap_table(paper_dir: Path, cq_gaps: list[dict], results: list[dict]) -> None:
    rows = []
    for result in results:
        for item in result["dimensions"]:
            if item["label"] in {"missing", "partial"}:
                rows.append(
                    [
                        result["name"],
                        item["dimension"],
                        item["label"],
                        item.get("gap") or "",
                        item.get("recommendation") or "",
                    ]
                )
    lines = ["# Table: Reporting-Completeness Reporting Gaps", ""]
    lines.extend(markdown_table(["Case", "Dimension", "Label", "Gap", "Recommended fix"], rows))
    if cq_gaps:
        lines.extend(["", "## CQ-Extracted Gaps", ""])
        lines.extend(
            markdown_table(
                ["Report", "Section", "Label", "Gap"],
                [[gap["report_name"] or gap["report"], local_name(gap["section"]), gap["label"], gap["gap"] or ""] for gap in cq_gaps],
            )
        )
    (paper_dir / "table_reporting_gaps.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_score_table(paper_dir: Path, results: list[dict]) -> None:
    rows = []
    for result in results:
        row = [result["name"], f"{result['total_score']}/{result['max_score']}"]
        row.extend(f"{item['label']} ({item['weighted_score']}/{item['weight']})" for item in result["dimensions"])
        rows.append(row)
    lines = ["# Table: Completeness Scores", ""]
    lines.extend(
        markdown_table(
            ["Case", "Total", "Runtime", "Evaluation", "Provenance", "Governance", "Benchmark process"],
            rows,
        )
    )
    (paper_dir / "table_completeness_scores.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_aggregate_report(out_dir: Path, results: list[dict], cq_gaps: list[dict], shacl_warnings: list[dict]) -> None:
    lines = [
        "# AGENT-O Reporting-Completeness Aggregate Gap Report",
        "",
        "This report aggregates `cq_reporting_gaps`, SHACL profile findings, and graph-derived completeness scoring for AgentArena plus the three prior agent-paper examples.",
        "",
        "## Scoring Rubric",
        "",
    ]
    lines.extend(
        markdown_table(
            ["Dimension", "Weight"],
            [[dimension["name"], f"{dimension['weight']}%"] for dimension in DIMENSIONS],
        )
    )
    lines.extend(["", "Labels are converted to scores as `present = 1.0`, `partial = 0.5`, `missing = 0`, and `not_applicable` is excluded from the weighted numerator.", ""])
    lines.extend(["## Completeness Scores", ""])
    lines.extend(
        markdown_table(
            ["Case", "Total", "Runtime", "Evaluation", "Provenance", "Governance", "Benchmark process"],
            [
                [
                    result["name"],
                    f"{result['total_score']}/{result['max_score']}",
                    *[f"{item['label']} ({item['weighted_score']}/{item['weight']})" for item in result["dimensions"]],
                ]
                for result in results
            ],
        )
    )
    lines.extend(["", "## Case-Level Gaps", ""])
    for result in results:
        lines.extend([f"### {result['name']}", "", f"- Score: `{result['total_score']}/{result['max_score']}`", f"- Agent: `{result['agent_label']}`", ""])
        gap_items = [item for item in result["dimensions"] if item["label"] in {"missing", "partial"}]
        if gap_items:
            lines.extend(
                markdown_table(
                    ["Dimension", "Label", "Gap", "Evidence"],
                    [
                        [
                            item["dimension"],
                            item["label"],
                            item.get("gap") or "",
                            item["evidence"][0] if item.get("evidence") else "",
                        ]
                        for item in gap_items
                    ],
                )
            )
        else:
            lines.append("No missing or partial dimensions were identified by the current rubric.")
        target_warnings = result.get("shacl_warnings", [])
        if target_warnings:
            lines.extend(["", "SHACL profile findings:", ""])
            lines.extend(markdown_table(["Shape", "Focus", "Message"], [[warning["shape"], warning["focus_label"], warning["message"]] for warning in target_warnings]))
        lines.append("")
    lines.extend(["## CQ-Extracted Reporting Gaps", ""])
    if cq_gaps:
        lines.extend(
            markdown_table(
                ["Report", "Section", "Label", "Gap", "Recommended fix"],
                [
                    [
                        gap["report_name"] or gap["report"],
                        local_name(gap["section"]),
                        gap["label"],
                        gap["gap"] or "",
                        gap["recommendation"] or "",
                    ]
                    for gap in cq_gaps
                ],
            )
        )
    else:
        lines.append("No CQ reporting gaps were found.")
    lines.extend(["", "## SHACL Profile Findings", ""])
    if shacl_warnings:
        lines.extend(
            markdown_table(
                ["Shape", "Focus", "Message"],
                [[warning["shape"], warning["focus_label"] or warning["focus"], warning["message"]] for warning in shacl_warnings],
            )
        )
    else:
        lines.append("No SHACL profile findings were found.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- AgentArena is useful as a benchmark-alignment case because it makes runtime/evaluation separation visible, but the current POC annotation still lacks health-governance details such as accountability, escalation, privacy, and compliance.",
            "- The Trial Simulation example is strong on runtime workflow and provenance, but the current annotation does not yet include a formal evaluation dataset/metric block.",
            "- MedAgent-Pro and the Consensus Matrix System are stronger on evaluation coverage because their annotations include datasets and metric results.",
            "- The reporting-completeness pipeline now distinguishes ontology coverage from paper-description completeness: AGENT-O can represent the concepts, while the score identifies what each paper or annotation does not yet report.",
            "",
            "## Next Steps",
            "",
            "1. Add explicit `report:ReportingCompletenessAssessment` records for the three prior agent papers, using short source quotes from the original paper extracts.",
            "2. Expand AgentArena annotation with benchmark-task, validity/refusal, reliability/stability, and cost/latency terms.",
            "3. Convert this graph-derived POC into a reusable `data/reporting_completeness/paper_annotations/*.json` input format for larger corpus scoring.",
        ]
    )
    (out_dir / "aggregate_gap_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    graph = load_graph()
    cq_payload = load_json(ROOT / "outputs" / "sparql" / "cq_results.json")
    shacl_payload = load_json(ROOT / "outputs" / "shacl" / "shacl_results.json")
    cq_gaps = collect_cq_gaps(cq_payload)
    shacl_warnings = collect_shacl_warnings(shacl_payload, graph)

    results = [score_target(graph, target, shacl_warnings) for target in TARGETS]

    out_dir = ROOT / "outputs" / "reporting_completeness"
    paper_dir = ROOT / "outputs" / "paper_tables"
    out_dir.mkdir(parents=True, exist_ok=True)
    paper_dir.mkdir(parents=True, exist_ok=True)

    for result in results:
        write_per_target_outputs(out_dir, result)
    write_scores_csv(out_dir, results)
    write_reporting_gap_table(paper_dir, cq_gaps, results)
    write_score_table(paper_dir, results)
    write_aggregate_report(out_dir, results, cq_gaps, shacl_warnings)

    payload = {
        "cases": len(results),
        "cq_reporting_gaps": len(cq_gaps),
        "shacl_warnings": len(shacl_warnings),
        "outputs": [
            "outputs/reporting_completeness/aggregate_gap_report.md",
            "outputs/reporting_completeness/completeness_scores.csv",
            "outputs/reporting_completeness/completeness_scores.json",
            "outputs/paper_tables/table_reporting_gaps.md",
            "outputs/paper_tables/table_completeness_scores.md",
        ],
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
