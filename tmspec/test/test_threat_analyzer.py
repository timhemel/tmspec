
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

    def get_model_loading_errors(self):
        return sorted(self.model_loading_errors, key=lambda x: x.elements[0].get_position())

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

    def test_model_query_dataflow_has_property(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        elt = a.variable()
        value = a.variable()
        const_key = a.atom('https')
        q = a.query('property', [elt, const_key, value])
        r = [[to_python(elt), to_python(value)] for _ in q]
        flows = self.dfd_with_flows.get_flows()
        self.assertEqual(r, [[flows[0], True]])

    def test_model_query_flow_clause(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)
        v_from = a.variable()
        v_to = a.variable()
        v_elt = a.variable()
        q = a.query('flow', [v_elt, v_from, v_to])
        r = [[to_python(v_elt), to_python(v_from), to_python(v_to)] for _ in q]
        flows = self.dfd_with_flows.get_flows()
        self.assertEqual(r, [[flows[0], flows[0].source, flows[0].target]])

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

    def find_component_by_name(self, model, name):
        l = [
            c for z in model.get_zones()
            for c in model.get_zone_components(z)
            if c.name == name ]
        if l == []:
            return None
        return l[0]

    def test_error_component_without_flow(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_without_flows)
        self.assertEqual(len(a.get_model_loading_errors()),2)
        self.assertEqual(a.get_model_loading_errors()[0].get_short_description(),
                'component without flow')
        webapp = self.find_component_by_name(self.dfd_without_flows, 'webapp')
        self.assertEqual(a.get_model_loading_errors()[0].get_position(), webapp.get_position())

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
threat_descr(['test', '001', 0], 'Test threat', 'This is a threat to test').
threat(['test', '001', 0], [X])
    :- process(X), property(X,'authentication::login',yes).
% any flow is a threat
threat_descr(['test', '002', 0], 'threat to $v1', 'One more threat (on $v1).').
threat(['test', '002', 0], [X]) :- dataflow(X)."""

    threatlib_errors_code = """
% any datastore is an error
error_descr(['test', '001', 0], 'Error test', 'An error.').
error(['test', '001', 0], [X]) :- datastore(X).
"""

    threatlib_extra_errors_code = """
% any process is an error
error_descr(['test', '002', 0], 'Extra error test', 'An extra error.').
error(['test', '002', 0], [X]) :- process(X).
"""

    def add_threat_library_from_source(self, analyzer, source):
        t = ThreatLibrary()
        t.from_string(source)
        analyzer.add_threat_library(t)

    def test_model_threats_multiple_libraries(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)

        self.add_threat_library_from_source(a, self.threatlib_base_code)
        self.add_threat_library_from_source(a, self.threatlib_threats_code)
        self.add_threat_library_from_source(a, self.threatlib_errors_code)

        r = a.analyze()
        self.assertEqual(len(r.get_threats()), 1)
        self.assertEqual(len(r.get_questions()), 1)
        self.assertEqual(len(r.get_errors()), 1)

    # loading multiple threat libraries should not overwrite definitions
    def test_model_analyze_with_extra_library(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)

        self.add_threat_library_from_source(a, self.threatlib_base_code)
        self.add_threat_library_from_source(a, self.threatlib_threats_code)
        self.add_threat_library_from_source(a, self.threatlib_errors_code)
        self.add_threat_library_from_source(a, self.threatlib_extra_errors_code)

        r = a.analyze()
        self.assertEqual(len(r.get_threats()), 1)
        self.assertEqual(len(r.get_questions()), 1)
        self.assertEqual(len(r.get_errors()), 2)

    # errors should include components without flows
    def test_model_analyze_components_without_flows(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_without_flows)
        r = a.analyze()
        self.assertEqual(r.get_threats(), [])
        self.assertEqual(r.get_questions(), [])
        self.assertEqual(len(r.get_errors()), 2)



    # must clear errors, threats, questions etc. between analyses
    def test_model_analyze_again_with_extra_library(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)

        self.add_threat_library_from_source(a, self.threatlib_base_code)
        self.add_threat_library_from_source(a, self.threatlib_threats_code)
        self.add_threat_library_from_source(a, self.threatlib_errors_code)

        r = a.analyze()
        self.add_threat_library_from_source(a, self.threatlib_extra_errors_code)
        r = a.analyze()
        self.assertEqual(len(r.get_threats()), 1)
        self.assertEqual(len(r.get_questions()), 1)
        self.assertEqual(len(r.get_errors()), 2)

    def test_model_analyze_components_without_flows_twice(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_without_flows)
        r = a.analyze()
        r = a.analyze()
        self.assertEqual(r.get_threats(), [])
        self.assertEqual(r.get_questions(), [])
        self.assertEqual(len(r.get_errors()), 2)

    # test that templating works in short description of threats and errors
    def test_model_result_short_descr_templating(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)

        self.add_threat_library_from_source(a, self.threatlib_base_code)
        self.add_threat_library_from_source(a, self.threatlib_threats_code)
        self.add_threat_library_from_source(a, self.threatlib_errors_code)

        r = a.analyze()
        threat = r.get_threats()[0]
        flow = self.dfd_with_flows.get_flows()[0]
        self.assertRegex(threat.get_short_description(), flow.name)

    def test_reporting_interface(self):
        a = FTOThreatAnalyzer()
        a.set_model(self.dfd_with_flows)

        self.add_threat_library_from_source(a, self.threatlib_base_code)
        self.add_threat_library_from_source(a, self.threatlib_threats_code)
        self.add_threat_library_from_source(a, self.threatlib_errors_code)

        r = a.analyze()
        threat = r.get_threats()[0]
        flow = self.dfd_with_flows.get_flows()[0]
        self.assertRegex(threat.get_short_description(), flow.name)
        self.assertEqual(threat.get_position(), flow.get_position())
        self.assertRegex(threat.get_long_description(), flow.name)
        self.assertEqual(threat.get_id(), 'test-002-0')
        self.assertEqual(threat.get_elements(), [flow])


    # ensure that errors, threats and questions are sorted
    # test that invalid libraries throw exception, TODO: how do we handle this?

if __name__ == "__main__":
    unittest.main()
