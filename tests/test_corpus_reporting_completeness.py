import tempfile
import unittest
from pathlib import Path

from scripts import run_corpus_reporting_completeness as corpus


class CorpusReportingCompletenessTests(unittest.TestCase):
    def test_discover_markdown_papers_only_vlm_papers_and_agentarena(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paper = root / "paper_extraction_parsing" / "paper_list" / "extracted_content" / "Agent Paper" / "vlm" / "Agent Paper.md"
            paper.parent.mkdir(parents=True)
            paper.write_text("# Agent Paper\n\nAgent workflow and evaluation.", encoding="utf-8")
            readme = root / "paper_extraction_parsing" / "MinerU" / "README.md"
            readme.parent.mkdir(parents=True)
            readme.write_text("# Tool README", encoding="utf-8")
            arena = root / "paper" / "extracted" / "agentareana" / "auto" / "agentareana.md"
            arena.parent.mkdir(parents=True)
            arena.write_text("# AgentArena\n\nBenchmark framework.", encoding="utf-8")

            papers = corpus.discover_markdown_papers(root)

            paths = [item.path for item in papers]
            self.assertEqual(paths, [arena, paper])
            self.assertEqual([item.paper_id for item in papers], ["agentarena", "agent-paper"])

    def test_classify_paper_type(self):
        self.assertEqual(corpus.classify_paper_type("A Survey of LLM Agents", "systematic review and survey"), "survey_review")
        self.assertEqual(corpus.classify_paper_type("AgentArena", "related work and literature review"), "benchmark")
        self.assertEqual(corpus.classify_paper_type("AgentClinic Benchmark", "benchmark leaderboard tasks"), "benchmark")
        self.assertEqual(corpus.classify_paper_type("AI Governance", "policy risk compliance governance"), "governance_policy")
        self.assertEqual(corpus.classify_paper_type("Diagnostic Agent", "workflow tool memory evaluation dataset"), "agent_system")

    def test_survey_review_does_not_score_as_concrete_agent_runtime(self):
        text = """
        # Survey of LLM Agents

        This review discusses agent workflows, tools, memory, evaluation datasets, governance,
        safety, privacy, risk, and benchmark trends across the literature.
        """
        result = corpus.score_paper("survey", "Survey of LLM Agents", text)

        by_id = {item["dimension_id"]: item for item in result["dimensions"]}
        self.assertEqual(result["paper_type"], "survey_review")
        self.assertEqual(by_id["runtime_architecture"]["label"], "not_applicable")
        self.assertEqual(by_id["benchmark_process_alignment"]["label"], "not_applicable")

    def test_score_agent_paper_returns_all_dimension_scores(self):
        text = """
        # Diagnostic Agent

        The agent uses a planner, tool execution, memory, and a workflow with multiple steps.
        Evaluation uses a benchmark dataset, baseline comparison, accuracy, F1, and error analysis.
        The paper reports logs, traces, artifacts, released code, and reproducibility details.
        Human review, risk mitigation, privacy, security, compliance, uncertainty, and fallback are described.
        The benchmark separates runtime from evaluation and reports validity, refusal, reliability, stability, latency, and cost.
        """
        result = corpus.score_paper("diagnostic-agent", "Diagnostic Agent", text)

        self.assertEqual(result["paper_type"], "agent_system")
        self.assertEqual(result["total_score"], 100.0)
        self.assertEqual({item["label"] for item in result["dimensions"]}, {"present"})
        self.assertTrue(all(item["evidence"] for item in result["dimensions"]))


if __name__ == "__main__":
    unittest.main()
