import sys
import unittest
from pathlib import Path

VENDOR_PATH = Path("/tmp/rdflib_validate")
if VENDOR_PATH.exists():
    sys.path.insert(0, str(VENDOR_PATH))

from rdflib import Graph, Literal, Namespace, RDF, RDFS
from rdflib.collection import Collection
from rdflib.namespace import OWL

from scripts.build_integrated_ontology import TOP_ONTOLOGY


ROOT = Path(__file__).resolve().parents[1]
CORE = Namespace("https://w3id.org/agent-o/core#")
HEALTH = Namespace("https://w3id.org/agent-o/health#")
REPORT = Namespace("https://w3id.org/agent-o/reporting#")
SH = Namespace("http://www.w3.org/ns/shacl#")


def load(path: Path) -> Graph:
    return Graph().parse(path, format="turtle")


class OntologyArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = load(ROOT / "ontology" / "modules" / "agento-core.ttl")
        cls.health = load(ROOT / "ontology" / "modules" / "agento-health.ttl")
        cls.report = load(ROOT / "ontology" / "modules" / "agento-report.ttl")
        cls.architecture_shapes = load(ROOT / "shapes" / "agento-architecture-shapes.ttl")

    def test_model_roles_specs_and_deployments_are_distinct(self):
        self.assertIn((CORE.ModelComponent, RDFS.subClassOf, CORE.AgentComponent), self.core)
        self.assertIn((CORE.ModelComponent, OWL.disjointWith, CORE.AIModelSpecification), self.core)
        self.assertIn((CORE.ModelComponent, OWL.disjointWith, CORE.ModelDeployment), self.core)
        self.assertIn((CORE.LanguageModel, RDFS.subClassOf, CORE.AIModelSpecification), self.core)
        self.assertNotIn((CORE.LanguageModel, RDFS.subClassOf, CORE.ModelComponent), self.core)

    def test_model_reporting_fields_have_a_formal_home(self):
        required_paths = {
            CORE.hasName,
            CORE.modelIdentifier,
            CORE.modelVersion,
            CORE.modelArchitectureType,
            CORE.modelReleaseDate,
            CORE.hasDeveloper,
            CORE.hasModelInputSpecification,
            CORE.hasModelOutputSpecification,
            CORE.supportsInputModality,
            CORE.hasModelCapability,
            CORE.hasModelIntendedUse,
            CORE.hasModelLimitation,
        }
        shape_paths = set(self.architecture_shapes.objects(None, SH.path))
        self.assertTrue(required_paths.issubset(shape_paths))

    def test_model_card_is_a_document_not_a_model_resource(self):
        self.assertIn((REPORT.ModelCardReport, OWL.disjointWith, CORE.ModelComponent), self.report)
        self.assertIn((REPORT.ModelCardReport, OWL.disjointWith, CORE.AIModelSpecification), self.report)
        self.assertIn((REPORT.ModelCardReport, OWL.disjointWith, CORE.ModelDeployment), self.report)

    def test_clinical_intended_use_is_not_a_reporting_section(self):
        self.assertIn((HEALTH.ClinicalUseCase, RDF.type, OWL.Class), self.health)
        self.assertNotIn((REPORT.IntendedUse, RDFS.subClassOf, REPORT.ReportingSection), self.report)
        self.assertIn((REPORT.IntendedUse, OWL.deprecated, Literal(True)), self.report)
        self.assertIn((HEALTH.hasIntendedAction, RDFS.range, HEALTH.IntendedClinicalAction), self.health)
        self.assertIn((HEALTH.ContraindicatedUse, RDFS.subClassOf, HEALTH.ProhibitedUse), self.health)

    def test_paper_types_are_explicitly_disjoint(self):
        expected = {
            REPORT.AgentSystemReport,
            REPORT.BenchmarkReport,
            REPORT.SurveyReviewReport,
            REPORT.GovernancePolicyReport,
            REPORT.MethodModelReport,
            REPORT.ConceptualCommentaryReport,
        }
        found = []
        for node in self.report.subjects(RDF.type, OWL.AllDisjointClasses):
            for head in self.report.objects(node, OWL.members):
                found.append(set(Collection(self.report, head)))
        self.assertIn(expected, found)

    def test_reporting_assessment_is_represented_as_provenanced_activity(self):
        self.assertIn((REPORT.ReportingAssessmentActivity, RDF.type, OWL.Class), self.report)
        self.assertIn((REPORT.generatedByAssessmentActivity, RDF.type, OWL.ObjectProperty), self.report)
        self.assertIn((REPORT.EvidenceStatement, RDF.type, OWL.Class), self.report)
        self.assertIn((REPORT.ReportingAssessmentActivity, OWL.disjointWith, CORE.AgentSystem), self.report)

    def test_integrated_ontology_equals_module_union_plus_header(self):
        modules = Graph()
        for path in sorted((ROOT / "ontology" / "modules").glob("*.ttl")):
            modules.parse(path, format="turtle")
        integrated = load(ROOT / "ontology" / "agento.ttl")
        expected = Graph()
        for triple in modules:
            expected.add(triple)
        expected.add((TOP_ONTOLOGY, RDF.type, OWL.Ontology))
        expected.add((TOP_ONTOLOGY, RDFS.label, Literal("AGENT-O Ontology", lang="en")))
        expected.add(
            (
                TOP_ONTOLOGY,
                RDFS.comment,
                Literal(
                    "Integrated AGENT-O ontology covering agent systems, model specifications and deployments, "
                    "runtime workflow, evaluation, documentation and provenance, governance, clinical context, "
                    "health-data interoperability, and reporting-assessment representation.",
                    lang="en",
                ),
            )
        )
        self.assertTrue(integrated.isomorphic(expected))


if __name__ == "__main__":
    unittest.main()
