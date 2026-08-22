# AGENT-O Formal Quality Report

- Files checked: `25`
- Parse failures: `0`
- Active files containing old ACRO URIs: `0`
- Classes missing labels: `0`
- Object properties missing labels: `0`
- Datatype properties missing labels: `0`
- Object properties missing domain/range: `0/0`
- Datatype properties missing domain/range: `0/0`
- Undefined AGENT-O terms in alignments: `0`
- Integrated ontology matches module union: `True`
- Integrated RDF triples: `1962`
- Active classes: `252`
- Active object properties: `198`
- Active datatype properties: `51`
- RDF-level schema-axiom statements: `679`
- Passed: `True`

## Module Inventory

| Module | RDF triples | Active classes | Active object properties | Active datatype properties |
| --- | ---: | ---: | ---: | ---: |
| `agento-core` | 635 | 80 | 77 | 18 |
| `agento-doc` | 90 | 9 | 10 | 7 |
| `agento-eval` | 174 | 22 | 23 | 4 |
| `agento-gov` | 293 | 39 | 34 | 8 |
| `agento-health` | 301 | 48 | 23 | 3 |
| `agento-report` | 466 | 54 | 31 | 11 |

## Notes

- Deprecated ACRO URIs are allowed only in `ontology/deprecated/`.
- Alignment files may reference external ontology IRIs, but AGENT-O terms used in alignments must be defined by active AGENT-O ontology files.
- Triple, entity, and schema-axiom-statement counts are reported separately; the RDF-level schema count is not presented as an OWLAPI logical-axiom count.
- Schema-axiom counting rule: RDF statements using rdfs:subClassOf, rdfs:subPropertyOf, rdfs:domain, rdfs:range, owl:equivalentClass, owl:disjointWith, owl:equivalentProperty, owl:inverseOf, owl:propertyDisjointWith, or an OWL property-characteristic type. This is a transparent RDF-level count, not an OWLAPI logical-axiom count.
