
from .ThreatAnalyzer import ThreatAnalysisError, ThreatAnalysisQuestion, ThreatAnalysisThreat

class ErrorsAndQuestionsReporter:
    def __init__(self, results, errors=True, questions=True, threats=False):
        def make_error_line(r):
            # filename:line:column:message
            filename = r.get_filename()
            line, column = r.get_position()
            if isinstance(r, ThreatAnalysisError):
                result_type = 'ERROR'
            elif isinstance(r, ThreatAnalysisQuestion):
                result_type = 'QUESTION'
            elif isinstance(r, ThreatAnalysisThreat):
                result_type = 'THREAT'
            long_descr = "\n".join(['   '+l
                for l in r.get_long_description().splitlines()])
            message = '%s %s: %s\n%s' % (result_type, r.get_id(),
                r.get_short_description(), long_descr)
            return "%s:%d:%d:%s" % (filename, line, column, message)
        items = []
        if errors:
            items += results.get_errors()
        if questions:
            items += results.get_questions()
        if threats:
            items += results.get_threats()
        items = sorted(items, key=
                lambda x: (x.get_filename(), x.get_position()))
        self.error_report = "\n".join([make_error_line(e) for e in items])
    def get(self):
        return self.error_report

