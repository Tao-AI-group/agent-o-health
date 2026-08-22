import json
import unittest

from rdflib import Literal
from rdflib.namespace import XSD

from scripts.run_sparql_cqs import serialize


class SparqlResultSerializationTests(unittest.TestCase):
    def test_rdf_literals_are_json_serializable(self):
        values = {
            "date": serialize(Literal("2026-08-19", datatype=XSD.date)),
            "decimal": serialize(Literal("0.92", datatype=XSD.decimal)),
            "integer": serialize(Literal("3", datatype=XSD.integer)),
        }

        rendered = json.dumps(values)
        self.assertIn("2026-08-19", rendered)
        self.assertIn("0.92", rendered)
        self.assertEqual(values["integer"], 3)


if __name__ == "__main__":
    unittest.main()
