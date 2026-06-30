#!/usr/bin/env python3
"""Run deterministic corpus-scale reporting completeness assessment over extracted paper Markdown files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    path: Path


DIMENSIONS = [
    {
        "id": "runtime_architecture",
        "name": "Runtime/architecture",
        "weight": 25,
        "required_any": ["agent", "workflow", "framework", "architecture", "pipeline", "system"],
        "signals": ["tool", "planner", "planning", "reasoning", "memory", "environment", "execution", "step", "multi-agent", "orchestr"],
        "gap": "Paper should describe the agent identity, runtime framework, architecture, workflow, planning/reasoning, memory, tools, and execution environment.",
    },
    {
        "id": "evaluation",
        "name": "Evaluation",
        "weight": 25,
        "required_any": ["evaluation", "experiment", "benchmark", "dataset", "task"],
        "signals": ["metric", "accuracy", "f1", "auc", "baseline", "result", "leaderboard", "ablation", "error analysis", "comparison"],
        "gap": "Paper should report evaluation datasets, benchmark tasks, baselines, metrics, results, and error analysis.",
    },
    {
        "id": "provenance_reproducibility",
        "name": "Provenance/reproducibility",
        "weight": 20,
        "required_any": ["trace", "log", "provenance", "reproduc", "artifact", "code", "repository"],
        "signals": ["source", "lineage", "audit", "version", "prompt", "configuration", "implementation", "open-source", "github"],
        "gap": "Paper should include provenance, lineage, artifacts, implementation details, versioning, and reproducibility support.",
    },
    {
        "id": "governance_safety",
        "name": "Governance/safety",
        "weight": 20,
        "required_any": ["risk", "safety", "privacy", "security", "compliance", "human", "review", "oversight"],
        "signals": ["fallback", "escalation", "uncertainty", "confidence", "bias", "fairness", "equity", "consent", "hipaa", "gdpr", "refusal"],
        "gap": "Paper should specify governance, human review, fallback, uncertainty, risk, privacy, security, and compliance requirements.",
    },
    {
        "id": "benchmark_process_alignment",
        "name": "Benchmark-process alignment",
        "weight": 10,
        "required_any": ["benchmark", "arena", "leaderboard", "task", "evaluation framework"],
        "signals": ["runtime", "validity", "verification", "refusal", "reliability", "stability", "latency", "cost", "stepwise"],
        "gap": "Paper should separate runtime and evaluation frameworks and report stepwise verification, validity/refusal handling, reliability, stability, and cost.",
    },
]


PAPER_TYPE_RULES = [
    ("survey_review", ["survey", "review", "scoping review", "systematic review", "future directions"]),
    ("benchmark", ["benchmark", "leaderboard", "arena", "evaluation framework", "simulator"]),
    ("governance_policy", ["governance", "policy", "ethics", "trustworthiness", "lifecycle management"]),
    ("agent_system", ["agent", "multi-agent", "workflow", "tool", "planner", "reasoning"]),
]

MANUAL_PAPER_TYPE_OVERRIDES = {
    "hybrid-code-v2-zero-hallucination-clinical-icd-10-coding-via-neuro-symbolic-veri": "agent_system",
    "llm-based-medical-assistant-personalization-with-short-and-long-term-memory-coor": "agent_system",
    "retrieval-augmented-generation-for-knowledge-intensive-nlp-tasks": "method_model",
    "webgpt-browser-assisted-question-answering-with-human-feedback": "agent_system",
}


def slugify(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return value[:80] or "paper"


def unique_id(title: str, path: Path) -> str:
    return slugify(title)


def discover_markdown_papers(project_root: Path = PROJECT_ROOT, include_agentarena: bool = True) -> list[PaperRecord]:
    records: list[PaperRecord] = []
    if include_agentarena:
        arena = project_root / "paper" / "extracted" / "agentareana" / "auto" / "agentareana.md"
        if arena.exists():
            records.append(PaperRecord("agentarena", "AgentArena", arena))

    extracted_root = project_root / "paper_extraction_parsing" / "paper_list" / "extracted_content"
    if extracted_root.exists():
        for path in sorted(extracted_root.glob("*/vlm/*.md")):
            title = path.stem.strip()
            records.append(PaperRecord(unique_id(title, path), title, path))

    seen: set[Path] = set()
    seen_ids: set[str] = set()
    unique: list[PaperRecord] = []
    for record in records:
        if record.path in seen:
            continue
        seen.add(record.path)
        paper_id = record.paper_id
        if paper_id in seen_ids:
            digest = hashlib.sha1(str(record.path).encode("utf-8")).hexdigest()[:8]
            paper_id = f"{paper_id}-{digest}"
        seen_ids.add(paper_id)
        unique.append(PaperRecord(paper_id, record.title, record.path))
    return unique


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def classify_paper_type(title: str, text: str) -> str:
    manual_type = MANUAL_PAPER_TYPE_OVERRIDES.get(slugify(title))
    if manual_type:
        return manual_type

    lower_title = title.lower()
    haystack = f"{title}\n{text[:8000]}".lower()
    if any(term in lower_title for term in ["benchmark", "arena", "leaderboard", "simulator"]):
        return "benchmark"
    if any(term in lower_title for term in ["survey", "review", "scoping review", "systematic review"]):
        return "survey_review"
    if any(term in haystack for term in ["systematic review", "scoping review", "literature review", "narrative review"]):
        return "survey_review"
    if any(term in lower_title for term in ["agent", "multi-agent", "workflow", "system", "framework"]):
        return "agent_system"
    for paper_type, terms in PAPER_TYPE_RULES[1:]:
        if any(term in haystack for term in terms):
            return paper_type
    return "unclear"


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    return [part.strip() for part in parts if len(part.strip()) > 20]


def evidence_for_terms(text: str, terms: list[str], limit: int = 2) -> list[str]:
    sentences = split_sentences(text)
    lower_terms = [term.lower() for term in terms]
    evidence = []
    for sentence in sentences:
        lower_sentence = sentence.lower()
        if any(term in lower_sentence for term in lower_terms):
            evidence.append(sentence[:360])
        if len(evidence) >= limit:
            break
    return evidence


def dimension_score(text: str, dimension: dict) -> dict:
    lower_text = text.lower()
    required_hits = [term for term in dimension["required_any"] if term in lower_text]
    signal_hits = [term for term in dimension["signals"] if term in lower_text]

    if (required_hits and len(signal_hits) >= 2) or len(required_hits) >= 3:
        fraction = 1.0
        label = "present"
    elif required_hits or signal_hits:
        fraction = 0.5
        label = "partial"
    else:
        fraction = 0.0
        label = "missing"

    evidence = evidence_for_terms(text, required_hits + signal_hits)
    if not evidence and label == "missing":
        evidence = ["No matching evidence was found by the deterministic keyword pass."]

    return {
        "dimension_id": dimension["id"],
        "dimension": dimension["name"],
        "weight": dimension["weight"],
        "label": label,
        "score_fraction": fraction,
        "weighted_score": round(fraction * dimension["weight"], 2),
        "matched_required_terms": required_hits,
        "matched_signal_terms": signal_hits,
        "evidence": evidence,
        "gap": None if label == "present" else dimension["gap"],
    }


def adjust_for_paper_type(paper_type: str, dimensions: list[dict]) -> list[dict]:
    adjusted = []
    for item in dimensions:
        copy = dict(item)
        if paper_type == "survey_review" and copy["dimension_id"] in {"runtime_architecture", "benchmark_process_alignment"}:
            copy["label"] = "not_applicable"
            copy["score_fraction"] = None
            copy["weighted_score"] = 0.0
            copy["gap"] = "Survey/review papers may not describe a single runnable agent system."
        if paper_type == "governance_policy" and copy["dimension_id"] in {"runtime_architecture", "evaluation", "benchmark_process_alignment"}:
            if copy["label"] == "missing":
                copy["label"] = "not_applicable"
                copy["score_fraction"] = None
                copy["weighted_score"] = 0.0
                copy["gap"] = "Governance/policy papers may not define a concrete evaluated agent instance."
        adjusted.append(copy)
    return adjusted


def normalized_total(dimensions: list[dict]) -> tuple[float, float]:
    applicable_weight = sum(item["weight"] for item in dimensions if item["score_fraction"] is not None)
    if applicable_weight == 0:
        return 0.0, 0.0
    weighted = sum(item["weighted_score"] for item in dimensions)
    return round(weighted / applicable_weight * 100, 2), applicable_weight


def score_paper(paper_id: str, title: str, text: str, path: str | None = None) -> dict:
    normalized = normalize_text(text)
    paper_type = classify_paper_type(title, normalized)
    dimensions = [dimension_score(normalized, dimension) for dimension in DIMENSIONS]
    dimensions = adjust_for_paper_type(paper_type, dimensions)
    total_score, applicable_weight = normalized_total(dimensions)
    return {
        "paper_id": paper_id,
        "title": title,
        "path": path,
        "paper_type": paper_type,
        "total_score": total_score,
        "applicable_weight": applicable_weight,
        "dimensions": dimensions,
        "missing_or_partial": [
            item
            for item in dimensions
            if item["label"] in {"missing", "partial"}
        ],
    }


def read_paper(record: PaperRecord) -> str:
    return record.path.read_text(encoding="utf-8", errors="ignore")


def write_manifest(records: list[PaperRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["paper_id", "title", "path"])
        writer.writeheader()
        for record in records:
            writer.writerow({"paper_id": record.paper_id, "title": record.title, "path": str(record.path)})


def markdown_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return lines


def write_per_paper_outputs(results: list[dict], out_dir: Path) -> None:
    per_paper = out_dir / "per_paper"
    per_paper.mkdir(parents=True, exist_ok=True)
    for result in results:
        (per_paper / f"{result['paper_id']}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        lines = [
            f"# {result['title']} Reporting-Completeness Summary",
            "",
            f"- Paper type: `{result['paper_type']}`",
            f"- Completeness score: `{result['total_score']}/100`",
            f"- Source: `{result['path']}`",
            "",
            "## Dimension Scores",
            "",
        ]
        lines.extend(
            markdown_table(
                ["Dimension", "Label", "Weighted score", "Gap"],
                [
                    [
                        item["dimension"],
                        item["label"],
                        f"{item['weighted_score']}/{item['weight']}",
                        item.get("gap") or "",
                    ]
                    for item in result["dimensions"]
                ],
            )
        )
        lines.extend(["", "## Evidence", ""])
        for item in result["dimensions"]:
            lines.extend([f"### {item['dimension']}", ""])
            for evidence in item["evidence"]:
                lines.append(f"- {evidence}")
            lines.append("")
        (per_paper / f"{result['paper_id']}.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_scores(results: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "corpus_completeness_scores.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["paper_id", "title", "paper_type", "total_score"] + [dimension["id"] for dimension in DIMENSIONS]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            row = {
                "paper_id": result["paper_id"],
                "title": result["title"],
                "paper_type": result["paper_type"],
                "total_score": result["total_score"],
            }
            for item in result["dimensions"]:
                row[item["dimension_id"]] = item["label"]
            writer.writerow(row)
    (out_dir / "corpus_completeness_scores.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


def aggregate_gap_counts(results: list[dict]) -> dict[str, dict[str, int]]:
    counts = {dimension["id"]: {"present": 0, "partial": 0, "missing": 0, "not_applicable": 0} for dimension in DIMENSIONS}
    for result in results:
        for item in result["dimensions"]:
            counts[item["dimension_id"]][item["label"]] += 1
    return counts


def write_aggregate_report(results: list[dict], out_dir: Path, paper_table_dir: Path, total_discovered: int) -> None:
    counts = aggregate_gap_counts(results)
    lines = [
        "# Corpus Reporting-Completeness Pilot Report",
        "",
        f"- Papers discovered: `{total_discovered}`",
        f"- Papers scored in this pilot: `{len(results)}`",
        "- Method: deterministic section/keyword/evidence pass; no LLM API used in this pilot run.",
        "",
        "## Completeness Scores",
        "",
    ]
    lines.extend(
        markdown_table(
            ["Paper", "Type", "Score", "Runtime", "Evaluation", "Provenance", "Governance", "Benchmark"],
            [
                [
                    result["title"],
                    result["paper_type"],
                    f"{result['total_score']}/100",
                    *[item["label"] for item in result["dimensions"]],
                ]
                for result in results
            ],
        )
    )
    lines.extend(["", "## Gap Counts", ""])
    lines.extend(
        markdown_table(
            ["Dimension", "Present", "Partial", "Missing", "Not applicable"],
            [
                [
                    next(dimension["name"] for dimension in DIMENSIONS if dimension["id"] == dimension_id),
                    values["present"],
                    values["partial"],
                    values["missing"],
                    values["not_applicable"],
                ]
                for dimension_id, values in counts.items()
            ],
        )
    )
    lines.extend(["", "## Highest Priority Missing Or Partial Items", ""])
    gap_rows = []
    for result in results:
        for item in result["dimensions"]:
            if item["label"] in {"missing", "partial"}:
                gap_rows.append([result["title"], item["dimension"], item["label"], item.get("gap") or ""])
    lines.extend(markdown_table(["Paper", "Dimension", "Label", "Gap"], gap_rows[:80]) if gap_rows else ["No missing or partial items found."])
    lines.extend(
        [
            "",
            "## Recommended Next Step",
            "",
            "Use this pilot output to calibrate the deterministic rubric, then add an optional LLM-assisted evidence pass for papers with low evidence confidence or many partial dimensions.",
        ]
    )
    (out_dir / "aggregate_gap_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    table_lines = ["# Table: Corpus Reporting Completeness Assessment Pilot", ""]
    table_lines.extend(
        markdown_table(
            ["Paper", "Type", "Score", "Main gaps"],
            [
                [
                    result["title"],
                    result["paper_type"],
                    f"{result['total_score']}/100",
                    "; ".join(f"{item['dimension']}: {item['label']}" for item in result["missing_or_partial"][:3]),
                ]
                for result in results
            ],
        )
    )
    paper_table_dir.mkdir(parents=True, exist_ok=True)
    (paper_table_dir / "table_corpus_reporting_completeness.md").write_text("\n".join(table_lines) + "\n", encoding="utf-8")


def run(limit: int | None = 20, project_root: Path = PROJECT_ROOT, output_root: Path = ROOT) -> dict:
    records = discover_markdown_papers(project_root)
    selected = records[:limit] if limit is not None else records
    manifest_path = output_root / "data" / "reporting_completeness" / "paper_manifest.csv"
    write_manifest(records, manifest_path)

    results = [
        score_paper(record.paper_id, record.title, read_paper(record), str(record.path))
        for record in selected
    ]

    out_dir = output_root / "outputs" / "reporting_completeness_corpus"
    write_per_paper_outputs(results, out_dir)
    write_scores(results, out_dir)
    write_aggregate_report(results, out_dir, output_root / "outputs" / "paper_tables", len(records))

    payload = {
        "papers_discovered": len(records),
        "papers_scored": len(results),
        "manifest": str(manifest_path.relative_to(output_root)),
        "outputs": [
            "outputs/reporting_completeness_corpus/aggregate_gap_report.md",
            "outputs/reporting_completeness_corpus/corpus_completeness_scores.csv",
            "outputs/reporting_completeness_corpus/corpus_completeness_scores.json",
            "outputs/reporting_completeness_corpus/per_paper/",
            "outputs/paper_tables/table_corpus_reporting_completeness.md",
        ],
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=20, help="Number of discovered papers to score. Use 0 for all papers.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    args = parser.parse_args()

    limit = None if args.limit == 0 else args.limit
    payload = run(limit=limit, project_root=args.project_root, output_root=args.output_root)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
