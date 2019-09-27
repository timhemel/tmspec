
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

    def test_model_types_defined(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        name = a.variable()
        tmtype = a.variable()
        q = a.query('type', [name, tmtype])
        r = [[to_python(name), to_python(tmtype)] for _ in q]
        types = self.dfd_with_flows.get_types()
        self.assertEqual(r, [[t.name, t] for t in types])

    def test_model_subtypes_defined(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        tmtype = a.variable()
        parent_type = a.variable()
        q = a.query('subtype', [tmtype, parent_type])
        r = [[to_python(tmtype), to_python(parent_type)] for _ in q]
        tmtype = self.dfd_with_flows.get_flows()[0].get_types()[0]
        self.assertEqual(r, [[tmtype, t] for t in tmtype.get_types()])


    def test_error_component_without_flow(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_without_flows)
        self.assertEqual(len(a.get_errors()),2)
        self.assertEqual(a.get_errors()[0].message, 'component without flow')
        self.assertEqual(a.get_errors()[0].element.name, 'webapp')

    def test_analyzer_loads_script(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        tl = ThreatLibrary()
        tl.from_string('animal(monkey).')
        a.add_prolog_rules_from_threat_library(tl)
        v = a.variable()
        q = a.query('animal', [v])
        r = [to_python(v) for _ in q]
        self.assertEqual(r[0], 'monkey')
        

    def test_analyze_model_no_threats(self):
        a = ThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        r = a.analyze()
        self.assertEqual(r.get_threats(), [])
        self.assertEqual(r.get_questions(), [])

    threatlib_base_code = """
isoftype(T,T).
isoftype(T1,T2) :- subtype(T1,T), isoftype(T,T2).
process(X) :- type(process,TP), element(X,T), isoftype(T,TP).
dataflow(X) :- type(dataflow,TF), element(X,T), isoftype(T,TF).
datastore(X) :- type(datastore,TF), element(X,T), isoftype(T,TF).
"""
    threatlib_threats_code = """
% process with authentication::login is a threat
threat(['test', '001', 0], [P], 'Test threat', 'This is a threat to test')
    :- process(P), property(P,'authentication::login',yes).
% any flow is a threat
threat(['test', '002', 0], [F], 'Another test', 'One more threat.')
    :- dataflow(F)."""

    threatlib_errors_code = """
% any datastore is an error
error(['test', '001', 0], [S], 'Error test', 'An error.') :- datastore(S).
"""

    def test_model_threats_multiple_libraries(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)

        t1 = ThreatLibrary()
        t1.from_string(self.threatlib_base_code)
        a.add_threat_library(t1)

        t2 = ThreatLibrary()
        t2.from_string(self.threatlib_threats_code)
        a.add_threat_library(t2)

        t3 = ThreatLibrary()
        t3.from_string(self.threatlib_errors_code)
        a.add_threat_library(t3)

        r = a.analyze()
        self.assertEqual(len(r.get_threats()), 1)
        self.assertEqual(len(r.get_questions()), 1)
        self.assertEqual(len(r.get_errors()), 1)

    # must clear errors, threats, questions etc. between analyses
    # ensure that errors, threats and questions are sorted
    # loading multiple threat libraries should not overwrite definitions
    # test that templating works in threats and error messages
    # errors should include components without flows
    # test that invalid libraries throw exception, TODO: how do we handle this?

if __name__ == "__main__":
    unittest.main()
