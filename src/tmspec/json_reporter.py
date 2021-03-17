import json

class JSONThreatsReporter:
    def __init__(self, results):
        def make_threat_issue(t):
            return  {
                'id': t.get_id(),
                'elements': [ e.name for e in t.get_elements() ],
                'short_decription': t.get_short_description(),
                'long_decription': t.get_long_description(),
            }
        threats = [make_threat_issue(t) for t in results.get_threats()]
        self.report = {
            'version': '0.0',
            'threats': threats,
        }
    def get(self):
        return json.dumps(self.report, sort_keys=True, indent=4)


class JsonReporter:
    def __init__(self):
        pass

    def report(self, results, out_file, errors=True, questions=True, threats=False, errors_file=None, questions_file=None, threats_file=None):
        pass

