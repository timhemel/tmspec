
from .ThreatAnalyzer import ThreatAnalysisError, ThreatAnalysisQuestion, ThreatAnalysisThreat

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

def report_items(outf, items):
    r_items = sorted(items, key= lambda x: (x.get_filename(), x.get_position()))
    for i in r_items:
        outf.write(make_error_line(i))
        outf.write('\n')

class QuickfixReporter:
    def __init__(self):
        pass

    def report(self, results, out_file, errors=True, questions=True, threats=False, errors_file=None, questions_file=None, threats_file=None):
        if errors:
            outf_errors = errors_file if errors_file else out_file
            report_items(outf_errors, results.get_errors())
        if questions:
            outf_questions = questions_file if questions_file else out_file
            report_items(outf_questions, results.get_questions())
        if threats:
            outf_threats = threats_file if threats_file else out_file
            report_items(outf_threats, results.get_threats())


