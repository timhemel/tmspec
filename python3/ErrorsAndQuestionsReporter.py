
from ThreatAnalyzer import ThreatAnalysisError, ThreatAnalysisQuestion

class ErrorsAndQuestionsReporter:
    def __init__(self, results):
        def make_error_line(r):
            # filename:line:column:message
            filename = r.get_filename()
            line, column = r.get_position()
            if isinstance(r, ThreatAnalysisError):
                result_type = 'ERROR'
            elif isinstance(r, ThreatAnalysisQuestion):
                result_type = 'QUESTION'
            message = '%s %s: %s' % (result_type, r.get_id(), r.get_short_description())
            return "%s:%d:%d:%s" % (filename, line, column, message)
        items = sorted(results.get_errors() + results.get_questions(), key=
                lambda x: (x.get_filename(), x.get_position()))
        self.error_report = "\n".join([make_error_line(e) for e in items])
    def get(self):
        return self.error_report

