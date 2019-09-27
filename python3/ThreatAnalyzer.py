
import yldprolog.engine
from yldprolog.engine import get_value, to_python
from yldprolog.engine import Atom

class ThreatAnalysisError:

    def __init__(self, element, message):
        """An error during the analysis. element is the element for which
        the error is raised (multiple elements is not possible, because we
        want one (line, column) pair for error reporting).
        message is a string with the error message."""

        self.message = message
        self.element = element

class AnalysisResult:

    def get_threats(self):
        return []

    def get_questions(self):
        return []

class ThreatAnalyzer:

    def __init__(self):
        self.query_engine = yldprolog.engine.YP()
        self.set_prolog_base_functions()
        self.threat_libraries = []
        self.undefined_properties = set()
        self.errors = []

    def set_prolog_base_functions(self):
        self.query_engine.register_function('property',
            self.get_element_property)

    def add_undefined_property(self, element, key):
        self.undefined_properties.add((element, key))

    def get_element_property(self, element, prop_key, prop_value):
        """Answers the query property(element, prop_key, prop_value).
        element, prop_key and prop_value are all prolog data types.
        If the property is not defined, it gets recorded in the
        list of requested but undefined properties, but only if
        prop_key is not a variable.
        """
        const_element = self.query_engine.atom('element')
        vtype = self.query_engine.variable()
        # first unify element(v1, element)
        for l1 in self.query_engine.match_dynamic(const_element,
                [element, vtype]):
            element_value = get_value(element)
            prop_key_value = get_value(prop_key)
            if isinstance(prop_key_value, Atom):
                # property key is a constant value, which means it is
                # specifically requested.
                v_prop_value = self.query_engine.variable()
                q = list(self.query_engine.query('prop', [element_value,
                    prop_key_value, v_prop_value ]))
                if q == []:
                    # property is not defined
                    self.add_undefined_property(to_python(element_value),
                        to_python(prop_key_value))
            const_prop = self.query_engine.atom('prop')
            for l2 in self.query_engine.match_dynamic(const_prop, [
                element, prop_key, prop_value]):
                yield False

    def set_model(self, model):
        self.model = model
        self.query_engine.clear()
        self.set_prolog_base_functions()
        self.add_prolog_facts_from_model()

    def add_threat_library(self, threat_library):
        # TODO: handle exceptions
        self.add_prolog_rules_from_threat_library(threat_library)
        self.threat_libraries.append(threat_library)

    def add_clause_element(self, element, element_type):
        c_element = self.query_engine.atom('element')
        a_element = self.query_engine.atom(element)
        a_element_type = self.query_engine.atom(element_type)
        self.query_engine.assert_fact(c_element, [a_element, a_element_type])

    def add_clause_prop(self, element, key, value):
        c_property = self.query_engine.atom('prop')
        a_element = self.query_engine.atom(element)
        a_key = self.query_engine.atom(key)
        a_value = self.query_engine.atom(value)
        self.query_engine.assert_fact(c_property, [a_element, a_key, a_value])

    def add_clause_type(self, tmtype):
        c_type = self.query_engine.atom('type')
        a_name = self.query_engine.atom(tmtype.name)
        a_tmtype = self.query_engine.atom(tmtype)
        self.query_engine.assert_fact(c_type, [a_name, a_tmtype])

    def add_element_types(self, element):
        for element_type in element.get_types():
            self.add_clause_element(element, element_type)

    def add_element_properties(self, element):
        for key, value in element.get_attributes().items():
            self.add_clause_prop(element, key, value)

    def add_prolog_facts_from_model(self):
        for tmtype in self.model.get_types():
            self.add_clause_type(tmtype)
        components = set()
        for z in self.model.get_zones():
            for component in self.model.get_zone_components(z):
                self.add_element_types(component)
                self.add_element_properties(component)
                components.add(component)
        for flow in self.model.get_flows():
            self.add_element_types(flow)
            self.add_element_properties(flow)
            components.remove(flow.source)
            components.remove(flow.target)
            # print(flow.name, flow.source, flow.target, flow.get_attributes())
        for c in components:
            e = ThreatAnalysisError(c, 'component without flow')
            self.errors.append(e)
        

    def add_prolog_rules_from_threat_library(self, threat_library):
        self.query_engine.load_script_from_string(threat_library.get_python_source())

    def analyze_errors(self):
        v_error = self.query_engine.variable()
        v_elements = self.query_engine.variable()
        v_short_desc = self.query_engine.variable()
        v_long_desc = self.query_engine.variable()
        q = self.query_engine.query('error', [
            v_error, v_elements, v_short_desc, v_long_desc ])
        for r in q:
            print(v_error, v_elements, v_short_desc, v_long_desc)

    def analyze_threats(self):
        v_threat = self.query_engine.variable()
        v_elements = self.query_engine.variable()
        v_short_desc = self.query_engine.variable()
        v_long_desc = self.query_engine.variable()
        # print(self.query_engine.eval_context)
        print([v_threat, v_elements, v_short_desc, v_long_desc])
        q = self.query_engine.query('threat', [
            v_threat, v_elements, v_short_desc, v_long_desc ])

        r = [(v_threat, v_elements, v_short_desc, v_long_desc) for r in q]
        print('r=',r)
        return r

    def analyze(self):
        errors = self.analyze_errors()
        threats = self.analyze_threats()
        return AnalysisResult()

