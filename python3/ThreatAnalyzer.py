
import yldprolog.engine

class AnalysisResult:

    def get_threats(self):
        return []

    def get_questions(self):
        return []

class ThreatAnalyzer:

    def __init__(self):
        self.query_engine = yldprolog.engine.YP()
        self.threat_libraries = []

    def set_model(self, model):
        self.model = model
        self.query_engine.clear()
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
        c_property = self.query_engine.atom('property')
        a_element = self.query_engine.atom(element)
        a_key = self.query_engine.atom(key)
        a_value = self.query_engine.atom(value)
        self.query_engine.assert_fact(c_property, [a_element, a_key, a_value])

    def add_element_types(self, element):
        for element_type in element.get_types():
            self.add_clause_element(element, element_type)

    def add_element_properties(self, element):
        for key, value in element.get_attributes().items():
            self.add_clause_prop(element, key, value)

    def add_prolog_facts_from_model(self):
        for z in self.model.get_zones():
            for component in self.model.get_zone_components(z):
                self.add_element_types(component)
                self.add_element_properties(component)
        for flow in self.model.get_flows():
            self.add_element_types(flow)
            self.add_element_properties(flow)
            # print(flow.name, flow.source, flow.target, flow.get_attributes())

    def add_prolog_rules_from_threat_library(self, threat_library):
        pass

    def analyze(self):
        return AnalysisResult()

