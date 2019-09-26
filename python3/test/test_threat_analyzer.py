
import unittest
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

# from TmspecError import *
from TmspecParser import parseString
from ThreatAnalyzer import ThreatAnalyzer
from ThreatLibrary import ThreatLibrary


class FTOThreatAnalyzer(ThreatAnalyzer):
    # For Testing Only

    def variable(self):
        return self.query_engine.variable()

    def atom(self, name):
        return self.query_engine.atom(name)

    def query(self, name, args):
        return self.query_engine.query(name, args)

    def get_questions(self):
        return []


class TestThreatAnalyzer(unittest.TestCase):

    dfd_with_flows = parseString("""
version 0.0;
type encryptedflow(dataflow): https;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")

    def test_model_no_threats(self):
        a = ThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        r = a.analyze()
        self.assertEqual(r.get_threats(), [])
        self.assertEqual(r.get_questions(), [])

    def test_model_query_element_type(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        zone = self.dfd_with_flows.get_zones()[0]
        components = self.dfd_with_flows.get_zone_components(zone)
        elt = a.atom(components[0])
        value = a.variable()
        q = a.query('type', [elt, value])
        r = [ [elt.get_value(), value.get_value() ] for _ in q ]
        print(components[0].get_types()[0].name)
        self.assertEqual(r, [[components[0], components[0].get_types()[0]]])
    
    def test_model_query_element_type_inherited(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        zone = self.dfd_with_flows.get_zones()[0]
        flows = self.dfd_with_flows.get_flows()
        elt = a.atom(flows[0])
        value = a.variable()
        q = a.query('type', [elt, value])
        r = [ [elt.get_value(), value.get_value() ] for _ in q ]
        print(flows[0].get_types()[0].name)
        self.assertEqual(r, [[flows[0], flows[0].get_types()[0]]])

    
    def test_model_query_component_zone(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        elt = a.variable()
        value = a.variable()
        const_zone = a.atom('zone')
        q = a.query('property', [elt, const_zone, value])
        r = [ [elt.get_value(), value.get_value() ] for _ in q ]
        zone = self.dfd_with_flows.get_zones()[0]
        components = self.dfd_with_flows.get_zone_components(zone)
        self.assertEqual(r, [[components[0], zone], [components[1], zone]])

    def test_model_query_undefined_property(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        elt = a.variable()
        value = a.variable()
        const_key = a.atom('define_me')
        q = a.query('property', [elt, const_key, value])
        r = [ [elt.get_value(), value.get_value() ] for _ in q ]
        flows = self.dfd_with_flows.get_flows()
        self.assertEqual(r, [])
        self.assertEqual(len(a.get_questions()), 1)


    def test_model_query_flow_property(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        elt = a.variable()
        value = a.variable()
        const_key = a.atom('https')
        q = a.query('property', [elt, const_key, value])
        r = [ [elt.get_value(), value.get_value() ] for _ in q ]
        flows = self.dfd_with_flows.get_flows()
        self.assertEqual(r, [[flows[0], True]])

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


if __name__ == "__main__":
    unittest.main()
