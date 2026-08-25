# Supplementary Table S4A. SHACL profile validation and competency-query summary

| Evaluation item | Status/result | Rows or findings |
| --- | --- | --- |
| Agent/model architecture SHACL profile | Conforms | 0 findings |
| Governance SHACL profile | Conforms | 0 findings |
| Reporting SHACL profile | Conforms | 0 findings |
| Clinical intended-use competency query | Answered | 4 rows |
| Data-use permissions competency query | Answered | 1 row |
| FHIR-aligned health inputs competency query | Answered | 3 rows |
| Governance-profile checklist competency query | Answered | 3 rows |
| Model-card alignment competency query | Answered | 3 rows |
| Model-interface layering competency query | Answered | 4 rows |
| Model specification/deployment competency query | Answered | 3 rows |
| Provenance trace competency query | Answered | 3 rows |
| Report model/intended-use evidence competency query | Answered | 2 rows |
| Paper-type scope competency query | Answered | 1 row |
| Reporting-assessment provenance competency query | Answered | 5 rows |
| Reporting gaps competency query | Answered | 3 rows |
| Reasoning output | Input 3,644 triples; 6,364 additional triples after OWL-RL expansion |  |

Note: SHACL validation was performed over the AGENT-O ontology, alignment, application-profile, and example RDF graphs. All three suites conformed with zero violation- or warning-level findings. This result does not replace formal ontology-schema validation, factual verification of paper content, or clinical safety evaluation. Query row counts show that the competency questions are executable over the current example graph; they are not independent measures of ontology quality. The reporting-gaps query returns explicitly represented partial or missing reporting assessments and therefore does not indicate a SHACL failure. The complete natural-language questions, query files, expected evidence, and actual results are reported in Supplementary Table S4B.
