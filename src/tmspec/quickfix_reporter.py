
import click

from .threat_analyzer import ThreatAnalysisError, ThreatAnalysisQuestion, ThreatAnalysisWarning, ThreatAnalysisThreat

def make_error_line(r):
    # filename:line:column:message
    filename = r.get_filename()
    line, column = r.get_position()
    if isinstance(r, ThreatAnalysisError):
        result_type = 'ERROR'
    elif isinstance(r, ThreatAnalysisQuestion):
        result_type = 'QUESTION'
    elif isinstance(r, ThreatAnalysisWarning):
        result_type = 'WARNING'
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
    def __init__(self, params):
        self.params = params

    def report(self, results, out_file):
        rep_items = [
            (self.params['report_errors'], results.get_errors(), self.params['errors_file']),
            (self.params['report_questions'], results.get_questions(), self.params['questions_file']),
            (self.params['report_warnings'], results.get_warnings(), self.params['warnings_file']),
            (self.params['report_threats'], results.get_threats(), self.params['threats_file']),
        ]
        for report, items, report_file in rep_items:
            if report:
                if report_file:
                    outf_items = click.open_file(report_file, "w")
                else:
                    outf_items = out_file
            report_items(outf_items, items)
            if items != [] and self.params['mode_continue'] == False:
                break

