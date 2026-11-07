# AGENT-O Formal Quality Report

- Files checked: `25`
- Parse failures: `0`
- Active files containing old ACRO URIs: `0`
- Classes missing labels: `0`
- Object properties missing labels: `0`
- Datatype properties missing labels: `0`
- Active named classes/properties missing definitions: `0/0`
- Object properties missing domain/range: `0/0`
- Datatype properties missing domain/range: `0/0`
- Undefined AGENT-O terms in alignments: `0`
- Undeclared AGENT-O predicates in active graphs: `0`
- Integrated ontology matches module union: `True`
- Integrated RDF triples: `2646`
- Active named classes: `260`
- Anonymous class expressions: `50`
- Active object properties: `203`
- Active datatype properties: `52`
- RDF-level schema-axiom statements: `713`
- Passed: `True`

## Module Inventory

| Module | RDF triples | Active classes | Active object properties | Active datatype properties |
| --- | ---: | ---: | ---: | ---: |
| `agento-core` | 983 | 80 | 79 | 18 |
| `agento-doc` | 124 | 10 | 10 | 8 |
| `agento-eval` | 234 | 22 | 23 | 4 |
| `agento-gov` | 469 | 42 | 40 | 8 |
| `agento-health` | 351 | 52 | 23 | 3 |
| `agento-report` | 482 | 54 | 28 | 11 |

## Notes

- Deprecated ACRO URIs are allowed only in `ontology/deprecated/`.
- Alignment files may reference external ontology IRIs, but AGENT-O terms used in alignments must be defined by active AGENT-O ontology files.
- Triple, entity, and schema-axiom-statement counts are reported separately; the RDF-level schema count is not presented as an OWLAPI logical-axiom count.
- Schema-axiom counting rule: RDF statements using rdfs:subClassOf, rdfs:subPropertyOf, rdfs:domain, rdfs:range, owl:equivalentClass, owl:disjointWith, owl:equivalentProperty, owl:inverseOf, owl:propertyDisjointWith, or an OWL property-characteristic type. This is a transparent RDF-level count, not an OWLAPI logical-axiom count.
