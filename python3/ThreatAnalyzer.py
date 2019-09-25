
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

    def add_prolog_facts_from_model(self):
        print(self.model.get_zones())
        for z in self.model.get_zones():
            for c in self.model.get_zone_components(z):
                print(z, c)
        for f in self.model.get_flows():
            print(f.name, f.source, f.target, f.get_attributes())

    def add_prolog_rules_from_threat_library(self, threat_library):
        pass

    def analyze(self):
        return AnalysisResult()

