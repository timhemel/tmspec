
import re
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

# from tmspec.tmspec_error import *
from tmspec.parser import parseString
from tmspec.threat_analyzer import ThreatAnalyzer
from tmspec.threat_library import ThreatLibrary

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

    def get_model_loading_errors(self):
        return sorted(self.model_loading_errors, key=lambda x: x.elements[0].get_position())


dfd_without_flows = parseString("""
version 0.0;
type encryptedflow(dataflow): https;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;
""")

dfd_with_flows = parseString("""
version 0.0;
type encryptedflow(dataflow): https=yes;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")

dfd_with_flows_and_invalid_property = parseString("""
version 0.0;
type encryptedflow(dataflow): https=invalid;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")


dfd_nested_zones = parseString("""
version 0.0;
zone company;
zone office: zone=company, network=ethernet;

component database(datastore): zone=office;
""")

def test_model_query_element_type():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)
    zone = dfd_with_flows.get_zones()[0]
    components = dfd_with_flows.get_zone_components(zone)
    elt = a.atom(components[0])
    value = a.variable()
    q = a.query('element', [elt, value])
    r = [[to_python(elt), to_python(value) ] for _ in q]
    assert r == [[components[0], components[0].get_types()[0]]]

    
def test_model_query_element_type_inherited():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)
    zone = dfd_with_flows.get_zones()[0]
    flows = dfd_with_flows.get_flows()
    elt = a.atom(flows[0])
    value = a.variable()
    q = a.query('element', [elt, value])
    r = [[to_python(elt), to_python(value)] for _ in q]
    assert r == [[flows[0], flows[0].get_types()[0]]]

def test_model_query_component_zone():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)
    elt = a.variable()
    value = a.variable()
    const_zone = a.atom('zone')
    q = a.query('property', [elt, const_zone, value])
    r = [[to_python(elt), to_python(value)] for _ in q]
    zone = dfd_with_flows.get_zones()[0]
    components = dfd_with_flows.get_zone_components(zone)
    assert r == [[components[0], zone], [components[1], zone]]

def test_model_query_zone_zone():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_nested_zones)
    elt = a.variable()
    value = a.variable()
    const_zone = a.atom('zone')
    q = a.query('property', [elt, const_zone, value])
    r = [[to_python(elt), to_python(value)] for _ in q]
    office_zone = dfd_nested_zones.zones['office']
    company_zone = dfd_nested_zones.zones['company']
    components = dfd_nested_zones.get_zone_components(office_zone)
    assert r == [[office_zone, company_zone], [components[0], office_zone]]

def test_model_zone_valid_values():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_nested_zones)

    add_threat_library_from_source(a, '''
    prop_valid(X,https,yes).
    prop_valid(X,https,no).
    ''')

    z = dfd_nested_zones.get_zones()[1]
    elt = dfd_nested_zones.get_zone_components(z)[0]
    elt = a.variable()
    value = a.variable()
    const_zone = a.atom('zone')
    q = a.query('prop_valid', [elt, const_zone, value])
    r = [ to_python(value) for _ in q ]
    assert r == dfd_nested_zones.get_zones()

def test_model_query_undefined_property():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)
    flows = dfd_with_flows.get_flows()
    # elt = a.variable()
    elt = a.atom(flows[0])
    value = a.variable()
    const_key = a.atom('define_me')
    q = a.query('property', [elt, const_key, value])
    r = [[to_python(elt), to_python(value)] for _ in q]
    assert r == []
    assert len(a.undefined_properties) == 1
    assert len(a.invalid_properties) == 0

def test_model_query_dataflow_has_property():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)

    add_threat_library_from_source(a, '''
    prop_valid(X,https,yes).
    prop_valid(X,https,no).
    ''')

    elt = a.variable()
    value = a.variable()
    const_key = a.atom('https')
    q = a.query('property', [elt, const_key, value])
    r = [[to_python(elt), to_python(value)] for _ in q]
    flows = dfd_with_flows.get_flows()
    assert r == [[flows[0], 'yes']]
    assert len(a.invalid_properties) == 0

def test_model_query_invalid_dataflow_property():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows_and_invalid_property)

    tl = ThreatLibrary()
    tl.from_string('''
    prop_valid(X,https,yes).
    prop_valid(X,https,no).
    ''')
    a.add_prolog_rules_from_threat_library(tl)

    flows = dfd_with_flows_and_invalid_property.get_flows()
    elt = a.atom(flows[0])
    value = a.variable()
    const_key = a.atom('https')
    q = a.query('property', [elt, const_key, value])
    r = [[to_python(elt), to_python(value)] for _ in q]
    assert len(r) == 1
    assert len(a.undefined_properties) == 0
    assert len(a.invalid_properties) == 1


def test_model_query_flow_clause():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)
    v_from = a.variable()
    v_to = a.variable()
    v_elt = a.variable()
    q = a.query('flow', [v_elt, v_from, v_to])
    r = [[to_python(v_elt), to_python(v_from), to_python(v_to)] for _ in q]
    flows = dfd_with_flows.get_flows()
    assert r == [[flows[0], flows[0].source, flows[0].target]]

def test_model_types_defined():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)
    name = a.variable()
    tmtype = a.variable()
    q = a.query('type', [name, tmtype])
    r = [[to_python(name), to_python(tmtype)] for _ in q]
    types = dfd_with_flows.get_types()
    assert r == [[t.name, t] for t in types]

def test_model_subtypes_defined():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)
    tmtype = a.variable()
    parent_type = a.variable()
    q = a.query('subtype', [tmtype, parent_type])
    r = [[to_python(tmtype), to_python(parent_type)] for _ in q]
    tmtype = dfd_with_flows.get_flows()[0].get_types()[0]
    assert r == [[tmtype, t] for t in tmtype.get_types()]

def find_component_by_name(model, name):
    l = [
        c for z in model.get_zones()
        for c in model.get_zone_components(z)
        if c.name == name ]
    if l == []:
        return None
    return l[0]

def test_error_component_model_loading_errors():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_without_flows)
    # no model loading errors defined in ThreatAnalyzer
    assert a.get_model_loading_errors() == []

def test_analyzer_loads_script():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)
    tl = ThreatLibrary()
    tl.from_string('animal(monkey).')
    a.add_prolog_rules_from_threat_library(tl)
    v = a.variable()
    q = a.query('animal', [v])
    r = [to_python(v) for _ in q]
    assert r[0] == 'monkey'
    

def test_analyze_model_no_threats():
    a = ThreatAnalyzer()
    a.set_model(dfd_with_flows)
    r = a.analyze()
    assert r.get_threats() == []
    assert r.get_questions() == []

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


def add_threat_library_from_source(analyzer, source):
    t = ThreatLibrary()
    t.from_string(source)
    analyzer.add_threat_library(t)

def test_model_threats_multiple_libraries():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)

    add_threat_library_from_source(a, threatlib_base_code)
    add_threat_library_from_source(a, threatlib_threats_code)
    add_threat_library_from_source(a, threatlib_errors_code)

    r = a.analyze()
    assert len(r.get_threats()) == 1
    assert len(r.get_questions()) == 1
    assert len(r.get_errors()) == 1

# loading multiple threat libraries should not overwrite definitions
def test_model_analyze_with_extra_library():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)

    add_threat_library_from_source(a, threatlib_base_code)
    add_threat_library_from_source(a, threatlib_threats_code)
    add_threat_library_from_source(a, threatlib_errors_code)
    add_threat_library_from_source(a, threatlib_extra_errors_code)

    r = a.analyze()
    assert len(r.get_threats()) == 1
    assert len(r.get_questions()) == 1
    assert len(r.get_errors()) == 2

# must clear errors, threats, questions etc. between analyses
def test_model_analyze_again_with_extra_library():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)

    add_threat_library_from_source(a, threatlib_base_code)
    add_threat_library_from_source(a, threatlib_threats_code)
    add_threat_library_from_source(a, threatlib_errors_code)

    r = a.analyze()
    add_threat_library_from_source(a, threatlib_extra_errors_code)
    r = a.analyze()
    assert len(r.get_threats()) == 1
    assert len(r.get_questions()) == 1
    assert len(r.get_errors()) == 2

def test_model_analyze_errors_twice():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_without_flows)
    add_threat_library_from_source(a, threatlib_base_code)
    add_threat_library_from_source(a, threatlib_errors_code)
    r = a.analyze()
    r = a.analyze()
    assert r.get_threats() == []
    assert r.get_questions() == []
    assert len(r.get_errors()) == 1

def test_model_analyze_warnings():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows_and_invalid_property)

    add_threat_library_from_source(a, threatlib_base_code)

    add_threat_library_from_source(a, '''
    prop_valid(X,https,yes).
    prop_valid(X,https,no).
    threat_descr(['test', '001', 0], 'Test threat', 'This is a threat to test').
    threat(['test', '001', 0], [X]) :-
        dataflow(X), property(X,'https',no).
    ''')

    r = a.analyze()
    assert r.get_threats() == []
    assert r.get_questions() == []
    assert r.get_errors() == []
    assert len(r.get_warnings()) == 1



# test that templating works in short description of threats and errors
def test_model_result_short_descr_templating():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)

    add_threat_library_from_source(a, threatlib_base_code)
    add_threat_library_from_source(a, threatlib_threats_code)
    add_threat_library_from_source(a, threatlib_errors_code)

    r = a.analyze()
    threat = r.get_threats()[0]
    flow = dfd_with_flows.get_flows()[0]
    assert re.search(flow.name, threat.get_short_description())

def test_reporting_interface():
    a = FTOThreatAnalyzer()
    a.set_model(dfd_with_flows)

    add_threat_library_from_source(a, threatlib_base_code)
    add_threat_library_from_source(a, threatlib_threats_code)
    add_threat_library_from_source(a, threatlib_errors_code)

    r = a.analyze()
    threat = r.get_threats()[0]
    flow = dfd_with_flows.get_flows()[0]
    assert re.search(flow.name, threat.get_short_description())
    assert threat.get_position() == flow.get_position()
    assert re.search(flow.name, threat.get_long_description())
    assert threat.get_id() == 'test-002-0'
    assert threat.get_elements() == [flow]


# ensure that errors, threats and questions are sorted
# test that invalid libraries throw exception, TODO: how do we handle this?

