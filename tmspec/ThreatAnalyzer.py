
from string import Template
import yldprolog.engine
from yldprolog.engine import get_value, to_python
from yldprolog.engine import Atom

class ThreatAnalysisResultItem:

    def __init__(self, result_id, elements, short_description,
            long_description):
        """A result item from the analysis.
        elements are the elements to which the item applies (the first element
        is used to report the position in the input.
        short_description is a string with a short description (one line) and
        can have references to elements via template placeholders $v1, $v2,
        etc."""

        self.result_id = result_id
        self.short_description = short_description
        self.long_description = long_description
        self.elements = elements

    def get_id(self):
        """returns a result item identifier to refer to the result item
        or its type."""
        return self.result_id

    def get_elements(self):
        """gives all elements to which the result item applies."""
        return self.elements

    def get_filename(self):
        return self.elements[0].get_filename()

    def get_position(self):
        return self.elements[0].get_position()

    def replace_template_variables(self, text):
        var_lookup = dict([('v'+str(i+1), e.name)
            for i, e in enumerate(self.elements)])
        s = Template(text).safe_substitute(var_lookup)
        return s

    def get_short_description(self):
        """returns the short description and replaces any template
        placeholders with element names."""
        return self.replace_template_variables(self.short_description)

    def get_long_description(self):
        """returns the long description and replaces any template
        placeholders with element names."""
        return self.replace_template_variables(self.long_description)



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
        self.model_loading_errors = []

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

    def add_clause_flow(self, flow):
        c_flow = self.query_engine.atom('flow')
        a_flow = self.query_engine.atom(flow)
        a_source = self.query_engine.atom(flow.source)
        a_target = self.query_engine.atom(flow.target)
        self.query_engine.assert_fact(c_flow, [a_flow, a_source, a_target])

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
            self.add_clause_flow(flow)
            self.add_element_properties(flow)
            components.discard(flow.source)
            components.discard(flow.target)
        for c in components:
            e = ThreatAnalysisError('COMPNOFLOW', [c], 'component without flow', '''Component $v1 does not have any incoming or outgoing flows.''')
            self.model_loading_errors.append(e)

    def add_prolog_rules_from_threat_library(self, threat_library):
        self.query_engine.load_script_from_string(threat_library.get_python_source(), overwrite=False)

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
        # message = "ERROR %s: %s" % (error_code, short_desc)
        error = ThreatAnalysisError(error_code, elements, short_desc, long_desc)
        return error

    def make_threat(self, results):
        issue_id, elements, short_desc, long_desc = results
        error_code = "%s-%s-%d" % tuple(issue_id)
        # message = "THREAT %s: %s" % (error_code, short_desc)
        error = ThreatAnalysisThreat(error_code, elements, short_desc, long_desc)
        return error

    def make_questions_from_undefined_properties(self):
        questions = []
        for element, prop in self.undefined_properties:
            short_descr = "undefined property: %s" % prop
            questions.append(ThreatAnalysisQuestion('PROPUNDEF', [element], short_descr,
                '''The property %s is not defined on element $v1.''' % prop))
        return questions

    def analyze(self):
        errors = [ self.make_error(i) for i in self.query_for_issues('error') ]
        threats = [ self.make_threat(i) for i in self.query_for_issues('threat') ]
        ar = AnalysisResult()
        ar.add_errors(self.model_loading_errors)
        ar.add_errors(errors)
        ar.add_threats(threats)
        questions = self.make_questions_from_undefined_properties()
        ar.add_questions(questions)
        return ar

