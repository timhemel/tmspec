
import unittest
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

# from TmspecError import *
from TmspecParser import parseString
from ThreatAnalyzer import ThreatAnalyzer
from ThreatLibrary import ThreatLibrary



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
    
    def test_model_query_zone(self):
        a = ThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        elt = a.query_engine.variable()
        value = a.query_engine.variable()
        const_zone = a.query_engine.atom('zone')
        q = a.query_engine.query('property', [elt, const_zone, value])
        r = [ [elt.get_value(), value.get_value() ] for _ in q ]
        zone = self.dfd_with_flows.get_zones()[0]
        components = self.dfd_with_flows.get_zone_components(zone)
        self.assertEqual(r, [[components[0], zone], [components[1], zone]])

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
