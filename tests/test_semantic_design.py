"""Semantic counterexamples from the October 2026 design review.

These tests check entailments and real validation outcomes, rather than
requiring a particular serialization or a fixed number of ontology terms.
"""

from itertools import combinations
from pathlib import Path
import unittest

from owlrl import DeductiveClosure, OWLRL_Semantics
from pyshacl import validate
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL, SKOS


ROOT = Path(__file__).resolve().parents[1]
C = Namespace("https://w3id.org/agent-o/core#")
D = Namespace("https://w3id.org/agent-o/doc#")
E = Namespace("https://w3id.org/agent-o/eval#")
G = Namespace("https://w3id.org/agent-o/gov#")
H = Namespace("https://w3id.org/agent-o/health#")
R = Namespace("https://w3id.org/agent-o/reporting#")
X = Namespace("https://w3id.org/agent-o/tests/semantic#")
SH = Namespace("http://www.w3.org/ns/shacl#")


def clone(graph):
    result = Graph()
    result += graph
    return result


def disjoint_conflicts(graph):
    pairs = set(graph.subject_objects(OWL.disjointWith))
    for node in graph.subjects(RDF.type, OWL.AllDisjointClasses):
        for head in graph.objects(node, OWL.members):
            pairs.update(combinations(Collection(graph, head), 2))
    return [
        (individual, left, right)
        for left, right in pairs
        for individual in set(graph.subjects(RDF.type, left)) & set(graph.subjects(RDF.type, right))
    ]


class SemanticDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = Graph()
        for folder in ["ontology/modules", "ontology/alignments", "ontology/profiles"]:
            for path in sorted((ROOT / folder).glob("*.ttl")):
                cls.schema.parse(path, format="turtle")
        cls.examples = clone(cls.schema)
        for path in sorted((ROOT / "data/examples").glob("*.ttl")):
            cls.examples.parse(path, format="turtle")
        cls.closed_examples = clone(cls.examples)
        DeductiveClosure(OWLRL_Semantics).expand(cls.closed_examples)
        facts = """
            @prefix c: <https://w3id.org/agent-o/core#> .
            @prefix d: <https://w3id.org/agent-o/doc#> .
            @prefix e: <https://w3id.org/agent-o/eval#> .
            @prefix g: <https://w3id.org/agent-o/gov#> .
            @prefix h: <https://w3id.org/agent-o/health#> .
            @prefix r: <https://w3id.org/agent-o/reporting#> .
            @prefix x: <https://w3id.org/agent-o/tests/semantic#> .
            x:system a c:AgentSystem ; c:hasWorkflow x:workflow ;
                c:hasMemberAgent x:actor ; c:hasComponent x:component ;
                c:usesModel x:component ; c:usesTool x:tool ;
                r:hasAgentCard x:card ; g:hasRisk x:risk .
            x:healthSystem a h:ClinicalDecisionSupportAgentSystem .
            x:component c:usesModelResource x:model ; c:hasModelComponentRole x:role .
            x:model a c:LanguageModel ; d:hasLicense x:license ; c:modelVersion "v1" .
            x:specification a c:AIModelSpecification ; c:specifiesModel x:model .
            x:modelCard a r:ModelCardReport ; r:describesModelResource x:model .
            x:run c:usesModelDeployment x:deployment .
            x:deployment c:deploysModelResource x:model .
            x:benchmark a r:BenchmarkReport ; r:containsStatement x:statement .
            x:mixedReport a r:AgentSystemReport, r:BenchmarkReport .
            x:ehr a h:EHRInput .
            x:requirement a g:SafetyRequirement ; g:basedOnPrinciple x:principle .
            x:dataContext a e:DatasetUseContext ; e:hasDataUsePermission x:permission .
            x:task a h:ClinicalTask ; h:hasClinicalSetting x:setting .
            x:step a c:WorkflowStep ; h:usesFHIRResourceType "Patient" .
            x:study e:evaluates x:evaluatedModel .
            x:evaluatedModel a c:AIModelResource .
            x:source a h:HealthDataSource .
            x:biasStudy a e:BiasAssessment ; e:producesResult x:biasResult .
            x:mixedRecord a h:StructuredHealthDataArtifact, h:UnstructuredHealthDataArtifact .
            x:collectiveActor a c:AgentSystem, c:Agent .
        """
        cls.inferred = clone(cls.schema)
        cls.inferred.parse(data=facts, format="turtle")
        cls.inferred.add((SKOS.exactMatch, RDF.type, OWL.SymmetricProperty))
        cls.inferred.add((SKOS.exactMatch, RDF.type, OWL.TransitiveProperty))
        DeductiveClosure(OWLRL_Semantics).expand(cls.inferred)

    def assert_type(self, individual, expected):
        self.assertIn((individual, RDF.type, expected), self.inferred)

    def assert_not_type(self, individual, unexpected):
        self.assertNotIn((individual, RDF.type, unexpected), self.inferred)

    def test_system_membership_and_shared_properties_do_not_confer_agency(self):
        self.assert_type(X.actor, C.Agent)
        for system in [X.system, X.healthSystem]:
            self.assert_type(system, C.AgentSystem)
            self.assert_not_type(system, C.Agent)
        self.assert_not_type(X.actor, C.AgentSystem)

    def test_independently_asserted_collective_agency_is_allowed(self):
        self.assert_type(X.collectiveActor, C.Agent)
        self.assert_type(X.collectiveActor, C.AgentSystem)
        self.assertFalse(disjoint_conflicts(self.inferred))

    def test_specification_is_a_document_about_a_model(self):
        self.assert_type(X.specification, D.Document)
        self.assert_not_type(X.specification, C.Model)
        self.assert_type(X.model, C.Model)
        self.assert_not_type(X.model, C.AIModelSpecification)

    def test_license_metadata_does_not_confer_agency(self):
        self.assert_not_type(X.model, C.Agent)
        models = set(self.closed_examples.subjects(RDF.type, C.AIModelResource))
        self.assertGreaterEqual(len(models), 4)
        self.assertFalse([m for m in models if (m, RDF.type, C.Agent) in self.closed_examples])

    def test_benchmark_statements_do_not_change_report_identity(self):
        self.assert_type(X.benchmark, R.AssessableReport)
        self.assert_not_type(X.benchmark, R.AgentSystemReport)
        self.assert_type(X.mixedReport, R.AgentSystemReport)
        self.assert_type(X.mixedReport, R.BenchmarkReport)
        self.assertFalse(disjoint_conflicts(self.inferred))

    def test_ehr_origin_does_not_imply_fhir_representation(self):
        self.assert_type(X.ehr, C.Artifact)
        self.assert_not_type(X.ehr, H.FHIRResourceInput)
        conforms, _, _ = validate(
            self.schema + Graph().parse(data=f"<{X.ehr}> a <{H.EHRInput}> .", format="turtle"),
            shacl_graph=Graph().parse(ROOT / "shapes/agento-architecture-shapes.ttl"), inference="rdfs",
        )
        self.assertTrue(conforms)

    def test_governance_requirement_is_not_its_motivating_principle(self):
        self.assert_type(X.requirement, G.GovernanceRequirement)
        self.assert_type(X.principle, G.EthicalPrinciple)
        self.assert_not_type(X.requirement, G.EthicalPrinciple)
        self.assert_not_type(X.requirement, G.Policy)

    def test_standalone_model_card_is_not_system_documentation(self):
        self.assert_type(X.modelCard, D.Document)
        self.assert_not_type(X.modelCard, R.AgentSystemDocumentation)
        self.assert_not_type(X.modelCard, C.AIModelResource)

    def test_bias_study_and_its_result_have_distinct_identities(self):
        self.assert_type(X.biasStudy, E.EvaluationStudy)
        self.assert_type(X.biasResult, E.MetricResult)
        self.assert_not_type(X.biasResult, E.EvaluationStudy)

    def test_documented_property_scopes_do_not_retype_unrelated_entities(self):
        for individual, unexpected in [
            (X.dataContext, E.Dataset), (X.task, C.Agent),
            (X.step, C.Artifact), (X.evaluatedModel, C.Agent), (X.source, E.Dataset),
        ]:
            with self.subTest(individual=individual):
                self.assert_not_type(individual, unexpected)

    def test_profile_type_references_do_not_instantiate_document_sections(self):
        for predicate in [R.requiresReportingSection, R.recommendedReportingSection, R.requirementTargetsSection]:
            for section_type in self.schema.objects(None, predicate):
                self.assertNotIn((section_type, RDF.type, R.ReportingSection), self.inferred)
        self.assertNotIn((G.SafetyRequirement, RDF.type, G.EthicalPrinciple), self.inferred)

    def test_declared_profile_checks_real_section_instances(self):
        graph = clone(self.schema)
        for triple in [
            (X.profile, RDF.type, R.ReportingProfile),
            (X.profile, R.requiresReportingSection, R.RuntimeArchitectureSection),
            (X.profile, R.alignsWithGuideline, X.guideline),
            (X.report, RDF.type, R.BenchmarkReport),
            (X.report, R.documentsEvaluatedEntity, X.framework),
            (X.report, R.hasReportingProfile, X.profile),
            (X.report, R.hasReportingSection, X.unrelatedSection),
            (X.unrelatedSection, RDF.type, R.EvaluationReportingSection),
        ]:
            graph.add(triple)
        shape_graph = Graph().parse(ROOT / "shapes/agento-reporting-shapes.ttl")
        conforms, results, _ = validate(graph, shacl_graph=shape_graph, inference="rdfs")
        self.assertFalse(conforms)
        self.assertIn((None, SH.sourceShape, R.DeclaredReportingProfileShape), results)
        graph.add((X.report, R.hasReportingSection, X.actualRuntimeSection))
        graph.add((X.actualRuntimeSection, RDF.type, R.RuntimeArchitectureSection))
        conforms, _, _ = validate(graph, shacl_graph=shape_graph, inference="rdfs")
        self.assertTrue(conforms)

    def test_string_model_version_does_not_entail_an_object_version_link(self):
        swo_has_version = URIRef("http://www.ebi.ac.uk/swo/SWO_0004000")
        self.assertNotIn((X.model, swo_has_version, Literal("v1")), self.inferred)

    def test_developer_mapping_does_not_force_every_model_to_be_software(self):
        graph = clone(self.schema)
        swo_developer = URIRef("http://www.ebi.ac.uk/swo/SWO_0000394")
        swo_software = URIRef("http://www.ebi.ac.uk/swo/SWO_0000001")
        graph.add((swo_developer, RDFS.domain, swo_software))
        graph.add((X.parameterResource, C.hasDeveloper, X.developer))
        DeductiveClosure(OWLRL_Semantics).expand(graph)
        self.assertNotIn((X.parameterResource, RDF.type, swo_software), graph)

    def test_shared_who_source_does_not_equate_distinct_principles(self):
        concepts = [G.WHOHumanAutonomy, G.WHOTransparencyExplainability,
                    G.WHOResponsibilityAccountability, G.WHOInclusivenessEquity, G.WHOSafetyPrivacy]
        for left, right in combinations(concepts, 2):
            self.assertNotIn((left, SKOS.exactMatch, right), self.inferred)

    def test_active_named_classes_have_explicit_definitions(self):
        missing = [str(term) for term in self.schema.subjects(RDF.type, OWL.Class)
                   if isinstance(term, URIRef) and str(term).startswith("https://w3id.org/agent-o/")
                   and not self.schema.value(term, OWL.deprecated)
                   and not self.schema.value(term, RDFS.comment)]
        self.assertEqual(missing, [])

    def test_component_role_model_and_deployment_remain_distinct(self):
        self.assert_type(X.component, C.ModelComponent)
        self.assert_type(X.role, C.ModelComponentRole)
        self.assert_type(X.deployment, C.ModelDeployment)
        for individual, unexpected in [(X.component, C.AIModelResource),
                                       (X.component, C.ModelComponentRole), (X.run, C.ModelDeployment)]:
            self.assert_not_type(individual, unexpected)

    def test_step_occurrence_cannot_belong_to_two_runs(self):
        graph = clone(self.schema)
        for triple in [(X.stepOccurrence, RDF.type, C.WorkflowStep),
                       (X.stepOccurrence, C.executedInRun, X.firstRun)]:
            graph.add(triple)
        shape_graph = Graph().parse(ROOT / "shapes/agento-architecture-shapes.ttl")
        conforms, _, _ = validate(graph, shacl_graph=shape_graph, inference="rdfs")
        self.assertTrue(conforms)
        graph.add((X.stepOccurrence, C.executedInRun, X.secondRun))
        conforms, _, _ = validate(graph, shacl_graph=shape_graph, inference="rdfs")
        self.assertFalse(conforms)

    def test_unknown_controlled_values_are_rejected(self):
        shapes = Graph().parse(ROOT / "shapes/agento-reporting-shapes.ttl")
        for predicate in [R.hasCompletenessLabel, R.hasHumanVerificationStatus]:
            graph = clone(self.examples)
            assessment, value = next(graph.subject_objects(predicate))
            graph.remove((assessment, predicate, value))
            graph.add((assessment, predicate, X.UnknownControlledValue))
            conforms, results, _ = validate(graph, shacl_graph=shapes, inference="rdfs", allow_warnings=True)
            self.assertFalse(conforms)
            self.assertTrue([
                result for result in results.subjects(SH.focusNode, assessment)
                if (result, SH.resultPath, predicate) in results
                and (result, SH.sourceConstraintComponent, SH.InConstraintComponent) in results
            ])

    def test_mixed_health_artifacts_are_representable(self):
        self.assert_type(X.mixedRecord, H.StructuredHealthDataArtifact)
        self.assert_type(X.mixedRecord, H.UnstructuredHealthDataArtifact)
        self.assertFalse(disjoint_conflicts(self.inferred))

    def test_current_examples_have_no_detected_disjoint_type_conflict(self):
        self.assertEqual(disjoint_conflicts(self.closed_examples), [])

    def test_high_risk_governance_covers_actors_and_systems(self):
        shapes = Graph().parse(ROOT / "shapes/agento-governance-shapes.ttl")
        for subject_type in [C.Agent, C.AgentSystem]:
            with self.subTest(subject_type=subject_type):
                graph = clone(self.schema)
                graph.add((X.highRiskSubject, RDF.type, subject_type))
                graph.add((X.highRiskSubject, G.hasRisk, X.highRisk))
                graph.add((X.highRisk, G.hasSeverity, Literal("high")))
                conforms, results, _ = validate(
                    graph, shacl_graph=shapes, inference="rdfs", allow_warnings=True,
                )
                findings = list(results.subjects(SH.sourceShape, R.HighRiskGovernanceShape))
                self.assertEqual(len(findings), 1)
                self.assertIn((findings[0], SH.focusNode, X.highRiskSubject), results)
                self.assertIn((findings[0], SH.resultSeverity, SH.Warning), results)
                self.assertTrue(conforms)

    def test_removing_either_high_risk_control_is_detected(self):
        ex = Namespace("https://w3id.org/agent-o/examples/governance-reporting-profile#")
        shapes = Graph().parse(ROOT / "shapes/agento-governance-shapes.ttl")
        for predicate in [G.hasFallbackStrategy, G.hasEscalationPlan]:
            with self.subTest(missing_control=predicate):
                graph = clone(self.examples)
                graph.remove((ex.MedicationSafetyPolicy, predicate, None))
                conforms, results, _ = validate(
                    graph, shacl_graph=shapes, inference="rdfs", allow_warnings=True,
                )
                findings = list(results.subjects(SH.sourceShape, R.HighRiskGovernanceShape))
                self.assertEqual(len(findings), 1)
                self.assertIn((findings[0], SH.focusNode, ex.MedicationSafetyAgent), results)
                self.assertIn((findings[0], SH.resultSeverity, SH.Warning), results)
                self.assertTrue(conforms)

    def test_assessment_section_must_belong_to_assessed_report(self):
        ex = Namespace("https://w3id.org/agent-o/examples/governance-reporting-profile#")
        shapes = Graph().parse(ROOT / "shapes/agento-reporting-shapes.ttl")
        for section in [X.unknownSection, ex.PrivacySecurityComplianceSection]:
            with self.subTest(section=section):
                graph = clone(self.examples)
                graph.remove((ex.AgentArenaEvaluationAssessment, R.assessesSection, None))
                graph.add((ex.AgentArenaEvaluationAssessment, R.assessesSection, section))
                conforms, results, _ = validate(
                    graph, shacl_graph=shapes, inference="rdfs", allow_warnings=True,
                )
                self.assertFalse(conforms)
                self.assertTrue([
                    result for result in results.subjects(SH.focusNode, ex.AgentArenaEvaluationAssessment)
                    if (result, SH.resultSeverity, SH.Violation) in results
                ])

    def test_missing_and_not_applicable_need_no_fictitious_section(self):
        ex = Namespace("https://w3id.org/agent-o/examples/governance-reporting-profile#")
        shapes = Graph().parse(ROOT / "shapes/agento-reporting-shapes.ttl")
        for label in [R.Missing, R.NotApplicable]:
            with self.subTest(label=label):
                graph = clone(self.examples)
                graph.remove((ex.AgentArenaPrivacyComplianceAssessment, R.assessesSection, None))
                graph.set((ex.AgentArenaPrivacyComplianceAssessment, R.hasCompletenessLabel, label))
                conforms, results, _ = validate(
                    graph, shacl_graph=shapes, inference="rdfs", allow_warnings=True,
                )
                self.assertTrue(conforms)
                self.assertEqual(list(results.subjects(RDF.type, SH.ValidationResult)), [])

    def test_present_and_partial_assessments_require_actual_sections(self):
        ex = Namespace("https://w3id.org/agent-o/examples/governance-reporting-profile#")
        shapes = Graph().parse(ROOT / "shapes/agento-reporting-shapes.ttl")
        for label in [R.Present, R.Partial]:
            with self.subTest(label=label):
                graph = clone(self.examples)
                graph.remove((ex.AgentArenaEvaluationAssessment, R.assessesSection, None))
                graph.set((ex.AgentArenaEvaluationAssessment, R.hasCompletenessLabel, label))
                graph.add((ex.AgentArenaEvaluationAssessment, R.hasGapExplanation, Literal("Partial evidence.")))
                conforms, results, _ = validate(
                    graph, shacl_graph=shapes, inference="rdfs", allow_warnings=True,
                )
                self.assertFalse(conforms)
                self.assertTrue([
                    result for result in results.subjects(SH.focusNode, ex.AgentArenaEvaluationAssessment)
                    if (result, SH.resultSeverity, SH.Violation) in results
                ])

    def test_sparql_governance_findings_are_warnings(self):
        shapes = Graph().parse(ROOT / "shapes/agento-governance-shapes.ttl")
        for subject_type, source_shape in [
            (H.HealthAgentSystem, R.HealthPHIGovernanceShape),
            (H.ClinicalDecisionSupportAgentSystem, R.ClinicalDecisionSupportGovernanceShape),
            (H.PatientFacingAgentSystem, R.PatientFacingGovernanceShape),
        ]:
            with self.subTest(source_shape=source_shape):
                graph = clone(self.schema)
                graph.add((X.system, RDF.type, subject_type))
                graph.add((X.system, G.hasPrivacyConstraint, X.privacy))
                graph.add((X.privacy, G.containsPHI, Literal(True)))
                conforms, results, _ = validate(
                    graph, shacl_graph=shapes, inference="rdfs", allow_warnings=True,
                )
                findings = list(results.subjects(SH.sourceShape, source_shape))
                self.assertEqual(len(findings), 1)
                self.assertIn((findings[0], SH.resultSeverity, SH.Warning), results)
                self.assertTrue(conforms)
                self.assertEqual(set(results.objects(None, SH.resultSeverity)), {SH.Warning})

    def test_reporting_gap_warning_does_not_weaken_required_fields(self):
        ex = Namespace("https://w3id.org/agent-o/examples/governance-reporting-profile#")
        graph = clone(self.examples)
        graph.remove((ex.AgentArenaHumanReviewAssessment, R.hasGapExplanation, None))
        graph.remove((ex.AgentArenaHumanReviewAssessment, R.hasRecommendedFix, None))
        shapes = Graph().parse(ROOT / "shapes/agento-reporting-shapes.ttl")
        conforms, results, _ = validate(
            graph, shacl_graph=shapes, inference="rdfs", allow_warnings=True,
        )
        self.assertTrue(conforms)
        findings = list(results.subjects(SH.sourceShape, R.ReportingCompletenessGapShape))
        self.assertEqual(len(findings), 1)
        self.assertIn((findings[0], SH.resultSeverity, SH.Warning), results)
        graph.remove((ex.AgentArenaHumanReviewAssessment, R.assessesReport, None))
        conforms, results, _ = validate(
            graph, shacl_graph=shapes, inference="rdfs", allow_warnings=True,
        )
        self.assertFalse(conforms)
        self.assertTrue([
            result for result in results.subjects(SH.focusNode, ex.AgentArenaHumanReviewAssessment)
            if (result, SH.resultPath, R.assessesReport) in results
            and (result, SH.resultSeverity, SH.Violation) in results
        ])

    def test_gap_query_includes_absent_sections(self):
        ex = Namespace("https://w3id.org/agent-o/examples/governance-reporting-profile#")
        rows = list(self.examples.query(
            (ROOT / "queries/competency/cq_reporting_gaps.rq").read_text(encoding="utf-8")
        ))
        absent_section_rows = [
            row for row in rows
            if row.report == ex.AgentArenaPOCReport and row.dimension == ex.PrivacyComplianceDimension
        ]
        self.assertEqual(len(absent_section_rows), 1)
        self.assertEqual(absent_section_rows[0].label, R.Missing)
        self.assertIsNone(absent_section_rows[0].section)

    def test_current_examples_have_no_shacl_findings_including_warnings(self):
        for path in sorted((ROOT / "shapes").glob("*.ttl")):
            with self.subTest(shape=path.name):
                conforms, results, _ = validate(
                    self.examples, shacl_graph=Graph().parse(path), inference="rdfs",
                    advanced=True, allow_infos=True, allow_warnings=True,
                )
                self.assertTrue(conforms)
                self.assertEqual(list(results.subjects(RDF.type, SH.ValidationResult)), [])


if __name__ == "__main__":
    unittest.main()
