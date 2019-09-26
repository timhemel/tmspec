
import unittest
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

# from TmspecError import *
from TmspecParser import parseString
from ThreatAnalyzer import ThreatAnalyzer
from ThreatLibrary import ThreatLibrary

from yldprolog.engine import get_value, to_python

class FTOThreatAnalyzer(ThreatAnalyzer):
    # For Testing Only

    def __init__(self):
        super().__init__()

    def variable(self):
        return self.query_engine.variable()

    def atom(self, name):
        return self.query_engine.atom(name)

    def query(self, name, args):
        return self.query_engine.query(name, args)

    def get_undefined_properties(self):
        return self.undefined_properties

    def get_errors(self):
        return sorted(self.errors, key=lambda x: x.element.get_position())

class TestThreatAnalyzer(unittest.TestCase):

    dfd_without_flows = parseString("""
version 0.0;
type encryptedflow(dataflow): https;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;
""")

    dfd_with_flows = parseString("""
version 0.0;
type encryptedflow(dataflow): https;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")

    def test_model_query_element_type(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        zone = self.dfd_with_flows.get_zones()[0]
        components = self.dfd_with_flows.get_zone_components(zone)
        elt = a.atom(components[0])
        value = a.variable()
        q = a.query('element', [elt, value])
        r = [[to_python(elt), to_python(value) ] for _ in q]
        self.assertEqual(r, [[components[0], components[0].get_types()[0]]])
    
    def test_model_query_element_type_inherited(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        zone = self.dfd_with_flows.get_zones()[0]
        flows = self.dfd_with_flows.get_flows()
        elt = a.atom(flows[0])
        value = a.variable()
        q = a.query('element', [elt, value])
        r = [[to_python(elt), to_python(value)] for _ in q]
        self.assertEqual(r, [[flows[0], flows[0].get_types()[0]]])
    
    def test_model_query_component_zone(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        elt = a.variable()
        value = a.variable()
        const_zone = a.atom('zone')
        q = a.query('property', [elt, const_zone, value])
        r = [[to_python(elt), to_python(value)] for _ in q]
        zone = self.dfd_with_flows.get_zones()[0]
        components = self.dfd_with_flows.get_zone_components(zone)
        self.assertEqual(r, [[components[0], zone], [components[1], zone]])

    def test_model_query_undefined_property(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        flows = self.dfd_with_flows.get_flows()
        # elt = a.variable()
        elt = a.atom(flows[0])
        value = a.variable()
        const_key = a.atom('define_me')
        q = a.query('property', [elt, const_key, value])
        r = [[to_python(elt), to_python(value)] for _ in q]
        self.assertEqual(r, [])
        self.assertEqual(len(a.get_undefined_properties()), 1)

    def test_model_query_flow_property(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        elt = a.variable()
        value = a.variable()
        const_key = a.atom('https')
        q = a.query('property', [elt, const_key, value])
        r = [[to_python(elt), to_python(value)] for _ in q]
        flows = self.dfd_with_flows.get_flows()
        self.assertEqual(r, [[flows[0], True]])

    def test_error_component_without_flow(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_without_flows)
        self.assertEqual(len(a.get_errors()),2)
        self.assertEqual(a.get_errors()[0].message, 'component without flow')
        self.assertEqual(a.get_errors()[0].element.name, 'webapp')


    def test_analyze_model_no_threats(self):
        a = ThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        r = a.analyze()
        self.assertEqual(r.get_threats(), [])
        self.assertEqual(r.get_questions(), [])

    def test_model_one_threat(self):
        a = ThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        t = ThreatLibrary()
        t.from_string("""
threat(['test', '001', 0], [P],
'Test threat',
'This is a threat to test',
'') :- process(P), property(P,'authentication::login',yes).""")
        a.add_threat_library(t)
        r = a.analyze()
        self.assertEqual(len(r.get_threats()), 1)
        self.assertEqual(len(r.get_questions()), 1)

    # must clear errors, threats, questions etc. between analyses
    # ensure that errors, threats and questions are sorted

if __name__ == "__main__":
    unittest.main()
