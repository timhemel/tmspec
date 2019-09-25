
class AnalysisResult:

    def get_threats(self):
        return []

    def get_questions(self):
        return []

class ThreatAnalyzer:

    def set_model(self, model):
        pass

    def add_threat_library(self, threat_library):
        pass

    def analyze(self):
        return AnalysisResult()

