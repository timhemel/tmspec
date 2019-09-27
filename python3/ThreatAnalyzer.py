
import yldprolog.engine
from yldprolog.engine import get_value, to_python
from yldprolog.engine import Atom

class ThreatAnalysisResultItem:

    def __init__(self, element, message):
        """A result item from the analysis.
        element is the element to which the item applies (only one element
        can be used, because we want to report only one position in the input
        message is a string with the item message."""

        self.message = message
        self.element = element


class ThreatAnalysisError(ThreatAnalysisResultItem):

    pass

class ThreatAnalysisThreat(ThreatAnalysisResultItem):

    pass

class ThreatAnalysisQuestion(ThreatAnalysisResultItem):

    pass



class AnalysisResult:

    def __init__(self):
        self.errors = []
        self.threats = []
        self.questions = []

    def get_errors(self):
        return self.errors

    def get_threats(self):
        return self.threats

    def get_questions(self):
        return self.questions

    def add_errors(self, errors):
        self.errors += errors

    def add_threats(self, threats):
        self.threats += threats

    def add_questions(self, questions):
        self.questions += questions

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

    def add_clause_subtype(self, tmtype, parent_type):
        c_subtype = self.query_engine.atom('subtype')
        a_tmtype = self.query_engine.atom(tmtype)
        a_parent_type = self.query_engine.atom(parent_type)
        self.query_engine.assert_fact(c_subtype, [a_tmtype, a_parent_type])

    def add_element_types(self, element):
        for element_type in element.get_types():
            self.add_clause_element(element, element_type)

    def add_element_properties(self, element):
        for key, value in element.get_attributes().items():
            self.add_clause_prop(element, key, value)

    def add_prolog_facts_from_model(self):
        for tmtype in self.model.get_types():
            self.add_clause_type(tmtype)
            for parent_type in tmtype.get_types():
                self.add_clause_subtype(tmtype, parent_type)
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
        for c in components:
            e = ThreatAnalysisError(c, 'component without flow')
            self.errors.append(e)

    def add_prolog_rules_from_threat_library(self, threat_library):
        self.query_engine.load_script_from_string(threat_library.get_python_source())

    def query_for_issues(self, issue_type):
        v_issue = self.query_engine.variable()
        v_elements = self.query_engine.variable()
        v_short_desc = self.query_engine.variable()
        v_long_desc = self.query_engine.variable()
        q = self.query_engine.query(issue_type, [
            v_issue, v_elements, v_short_desc, v_long_desc ])
        r = [list(map(to_python,
            [v_issue, v_elements, v_short_desc, v_long_desc])) for r in q]
        return r

    def make_error(self, results):
        issue_id, elements, short_desc, long_desc = results
        error_code = "%s-%s-%d" % tuple(issue_id)
        message = "ERROR %s: %s" % (error_code, short_desc)
        error = ThreatAnalysisError(elements[0], message)
        return error

    def make_threat(self, results):
        issue_id, elements, short_desc, long_desc = results
        error_code = "%s-%s-%d" % tuple(issue_id)
        message = "THREAT %s: %s" % (error_code, short_desc)
        error = ThreatAnalysisThreat(elements[0], message)
        return error

    def make_questions_from_undefined_properties(self):
        questions = []
        for element, prop in self.undefined_properties:
            message = "QUESTION: undefined property: %s" % prop
            questions.append(ThreatAnalysisQuestion(element, message))
        return questions

    def analyze(self):
        errors = [ self.make_error(i) for i in self.query_for_issues('error') ]
        threats = [ self.make_threat(i) for i in self.query_for_issues('threat') ]
        ar = AnalysisResult()
        ar.add_errors(errors)
        ar.add_threats(threats)
        questions = self.make_questions_from_undefined_properties()
        ar.add_questions(questions)
        return ar

