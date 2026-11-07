"""Counterexamples from the comprehensive October 29 ontology review."""

from pathlib import Path
import unittest

from owlrl import DeductiveClosure, OWLRL_Semantics
from pyshacl import validate
from rdflib import Graph, Literal, Namespace, RDF

from scripts import validate_ontology


ROOT = Path(__file__).resolve().parents[1]
C = Namespace("https://w3id.org/agent-o/core#")
D = Namespace("https://w3id.org/agent-o/doc#")
E = Namespace("https://w3id.org/agent-o/eval#")
G = Namespace("https://w3id.org/agent-o/gov#")
H = Namespace("https://w3id.org/agent-o/health#")
R = Namespace("https://w3id.org/agent-o/reporting#")
X = Namespace("https://w3id.org/agent-o/tests/deep#")
EX = Namespace("https://w3id.org/agent-o/examples/governance-reporting-profile#")
SH = Namespace("http://www.w3.org/ns/shacl#")


class DeepSemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = Graph()
        for directory in ["ontology/modules", "ontology/alignments", "ontology/profiles"]:
            for path in sorted((ROOT / directory).glob("*.ttl")):
                cls.schema.parse(path)
        cls.examples = cls.schema + Graph()
        for path in sorted((ROOT / "data/examples").glob("*.ttl")):
            cls.examples.parse(path)
        cls.closed = cls.schema + Graph()
        cls.closed.parse(data="""
            @prefix c: <https://w3id.org/agent-o/core#> .
            @prefix d: <https://w3id.org/agent-o/doc#> .
            @prefix e: <https://w3id.org/agent-o/eval#> .
            @prefix g: <https://w3id.org/agent-o/gov#> .
            @prefix h: <https://w3id.org/agent-o/health#> .
            @prefix r: <https://w3id.org/agent-o/reporting#> .
            @prefix x: <https://w3id.org/agent-o/tests/deep#> .
            x:system a c:AgentSystem ; c:generates x:education ;
                c:producesProposedAction x:proposal ;
                g:hasGovernanceRequirement x:reviewRequirement .
            x:education a h:PatientFacingOutput ; h:hasOutputCategory "education" .
            x:reviewRequirement a g:HumanReviewRequirement .
            x:study e:evaluates x:tool, x:data .
            x:tool a c:Tool .
            x:data a c:Artifact .
            x:evaluator a e:Evaluator .
            x:accountability a g:AccountabilityRole .
            x:task a e:BenchmarkTask .
            x:planner a c:Planner .
            x:reasoner a c:Reasoner .
            x:observation a c:Observation .
            x:failureDescription a e:FailureCase .
            x:section a r:ReportingSection .
            x:context a e:DatasetUseContext ; e:hasDataUsePermission x:permission ;
                e:hasDataUseRestriction x:restriction .
            x:policy g:hasEscalationPlan x:plan ; g:hasOverrideCapability x:capability .
            x:plan g:hasTriggerCondition x:condition ; g:plannedRecipient x:reviewer .
            x:capability g:canOverrideAction x:proposal .
            x:actualEscalation g:triggeredBy x:condition .
        """, format="turtle")
        DeductiveClosure(OWLRL_Semantics).expand(cls.closed)

    def validate_graph(self, graph, filename):
        return validate(
            graph, shacl_graph=Graph().parse(ROOT / "shapes" / filename),
            inference="rdfs", advanced=True, allow_warnings=True,
        )

    def test_general_information_output_is_not_necessarily_a_proposed_action(self):
        self.assertIn((X.education, RDF.type, C.Artifact), self.closed)
        self.assertNotIn((X.education, RDF.type, C.ProposedAction), self.closed)

    def test_proposed_action_is_also_a_general_information_output(self):
        self.assertIn((X.proposal, RDF.type, C.ProposedAction), self.closed)
        self.assertIn((X.proposal, RDF.type, C.Artifact), self.closed)
        self.assertIn((X.system, C.generates, X.proposal), self.closed)

    def test_defined_general_identities_are_available_to_queries(self):
        for individual, parent in [
            (X.evaluator, C.Agent), (X.accountability, C.Role), (X.task, C.Task),
            (X.planner, C.ExecutionUnit), (X.reasoner, C.ExecutionUnit),
            (X.planner, C.Resource), (X.observation, C.Artifact),
            (X.failureDescription, C.Artifact), (X.section, C.Artifact),
        ]:
            with self.subTest(individual=individual, parent=parent):
                self.assertIn((individual, RDF.type, parent), self.closed)

    def test_data_use_permissions_and_restrictions_are_queryable_as_conditions(self):
        for condition in [X.permission, X.restriction]:
            self.assertIn((condition, RDF.type, G.DataUseCondition), self.closed)
            self.assertIn((X.context, E.hasDataUseCondition, condition), self.closed)
        self.assertNotIn((X.context, RDF.type, E.Dataset), self.closed)

    def test_tools_and_artifacts_can_be_selected_as_evaluation_targets(self):
        for target in [X.tool, X.data]:
            self.assertIn((target, RDF.type, E.EvaluableEntity), self.closed)
            self.assertNotIn((target, RDF.type, C.Agent), self.closed)
            self.assertNotIn((target, RDF.type, C.AgentSystem), self.closed)
            self.assertNotIn((target, RDF.type, C.Model), self.closed)

    def test_component_cannot_be_its_own_role(self):
        graph = self.examples + Graph()
        graph.set((EX.MedicationSafetyModelComponent, C.hasModelComponentRole,
                   EX.MedicationSafetyModelComponent))
        conforms, results, _ = self.validate_graph(graph, "agento-architecture-shapes.ttl")
        self.assertFalse(conforms)
        self.assertTrue(list(results.subjects(SH.focusNode, EX.MedicationSafetyModelComponent)))

    def test_configured_controls_do_not_assert_actual_occurrences(self):
        self.assertIn((X.plan, RDF.type, G.EscalationPlan), self.closed)
        self.assertNotIn((X.plan, RDF.type, G.EscalationEvent), self.closed)
        self.assertNotIn((X.plan, G.triggeredBy, X.condition), self.closed)
        self.assertIn((X.capability, RDF.type, G.OverrideCapability), self.closed)
        self.assertNotIn((X.capability, RDF.type, G.OverrideAction), self.closed)
        self.assertIn((X.actualEscalation, RDF.type, G.EscalationEvent), self.closed)
        self.assertIn((X.actualEscalation, G.hasTriggerCondition, X.condition), self.closed)

    def test_control_plans_cannot_masquerade_as_occurrences(self):
        for planned, occurrence in [(G.EscalationPlan, G.EscalationEvent),
                                    (G.OverrideCapability, G.OverrideAction)]:
            with self.subTest(planned=planned):
                graph = self.schema + Graph()
                graph.add((X.control, RDF.type, planned))
                graph.add((X.control, RDF.type, occurrence))
                conforms, results, _ = self.validate_graph(graph, "agento-governance-shapes.ttl")
                self.assertFalse(conforms)
                self.assertTrue(list(results.subjects(SH.focusNode, X.control)))

    def test_assessment_must_use_a_report_read_by_its_generating_activity(self):
        graph = self.examples + Graph()
        graph.set((EX.AgentArenaEvaluationAssessment, R.assessesReport, EX.MedicationSafetyAgentReport))
        graph.set((EX.AgentArenaEvaluationAssessment, R.assessesSection, EX.EvaluationReportingSection))
        conforms, results, _ = self.validate_graph(graph, "agento-reporting-shapes.ttl")
        self.assertFalse(conforms)
        self.assertTrue(list(results.subjects(SH.focusNode, EX.AgentArenaEvaluationAssessment)))

    def test_either_direction_of_assessment_generation_is_valid(self):
        for predicate in [R.generatedAssessment, R.generatedByAssessmentActivity]:
            with self.subTest(omitted_direction=predicate):
                graph = self.examples + Graph()
                graph.remove((None, predicate, None))
                conforms, results, _ = self.validate_graph(graph, "agento-reporting-shapes.ttl")
                self.assertTrue(conforms)
                self.assertEqual(list(results.subjects(RDF.type, SH.ValidationResult)), [])

    def test_nonclinical_configured_system_needs_neither_clinical_context_nor_past_run(self):
        graph = self.schema + Graph()
        graph.add((X.researchSystem, RDF.type, H.HealthAgentSystem))
        graph.add((X.researchSystem, C.hasComponent, X.component))
        conforms, results, _ = self.validate_graph(graph, "agento-architecture-shapes.ttl")
        self.assertTrue(conforms)
        self.assertEqual(list(results.subjects(RDF.type, SH.ValidationResult)), [])
        graph.add((X.researchSystem, RDF.type, H.ClinicalAgentSystem))
        conforms, results, _ = self.validate_graph(graph, "agento-architecture-shapes.ttl")
        self.assertFalse(conforms)
        self.assertTrue([
            node for node in results.subjects(SH.focusNode, X.researchSystem)
            if (node, SH.resultPath, H.hasIntendedClinicalUse) in results
        ])

    def test_negative_severity_text_does_not_match_high_risk(self):
        graph = self.schema + Graph()
        graph.add((X.actor, RDF.type, C.Agent))
        graph.add((X.actor, G.hasRisk, X.risk))
        graph.add((X.risk, G.hasSeverity, Literal("not high")))
        conforms, results, _ = self.validate_graph(graph, "agento-governance-shapes.ttl")
        self.assertTrue(conforms)
        self.assertEqual(list(results.subjects(RDF.type, SH.ValidationResult)), [])

    def test_undeclared_local_predicates_are_detected(self):
        graph = self.schema + Graph()
        self.assertEqual(validate_ontology.undefined_local_predicates(graph), [])
        graph.add((X.record, D.unknownTracePredicate, Literal("text")))
        self.assertEqual(validate_ontology.undefined_local_predicates(graph), ["doc:unknownTracePredicate"])

    def test_all_packaged_example_predicates_have_declarations(self):
        self.assertEqual(validate_ontology.undefined_local_predicates(self.examples), [])

    def test_system_level_review_requirement_does_not_turn_the_system_into_an_action(self):
        self.assertNotIn((X.system, RDF.type, C.ProposedAction), self.closed)
        graph = self.schema + Graph()
        graph.add((X.system, RDF.type, H.ClinicalDecisionSupportAgentSystem))
        graph.add((X.system, G.hasGovernanceRequirement, X.review))
        graph.add((X.review, RDF.type, G.HumanReviewRequirement))
        _, results, _ = self.validate_graph(graph, "agento-governance-shapes.ttl")
        self.assertEqual(list(results.subjects(SH.sourceShape, R.ClinicalDecisionSupportGovernanceShape)), [])

    def test_governance_query_distinguishes_controls_from_actual_events(self):
        graph = self.examples + Graph()
        DeductiveClosure(OWLRL_Semantics).expand(graph)
        rows = list(graph.query((ROOT / "queries/competency/cq_governance_profile_checklist.rq").read_text()))
        row = next(row for row in rows if row.agent == EX.MedicationSafetyAgent)
        self.assertEqual(row.escalationPlan, EX.PharmacistEscalation)
        self.assertEqual(row.overrideCapability, EX.ClinicianOverride)
        self.assertIsNone(row.escalationEvent)


if __name__ == "__main__":
    unittest.main()
