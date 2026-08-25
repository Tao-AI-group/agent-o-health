import csv
import statistics
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_frozen_public_reporting_outputs_are_consistent() -> None:
    manifest = read_csv("data/manifest/paper_manifest_public.csv")
    scores = read_csv("outputs/reporting_completeness/llm_judged_scores.csv")

    assert len(manifest) == len(scores) == 279
    assert {row["paper_id"] for row in manifest} == {row["paper_id"] for row in scores}
    assert all(not row["error"] for row in scores)
    assert {row["human_verification_status"] for row in scores} == {"not_human_verified"}
    assert "unclear" not in {row["paper_type"] for row in scores}

    values = [float(row["total_score"]) for row in scores]
    assert round(statistics.mean(values), 1) == 63.7
    assert statistics.median(values) == 67.5
    assert min(values) == 0.0
    assert max(values) == 100.0

    assert Counter(row["paper_type"] for row in scores) == {
        "agent_system": 148,
        "benchmark": 39,
        "conceptual_commentary": 5,
        "governance_policy": 2,
        "method_model": 73,
        "survey_review": 12,
    }
