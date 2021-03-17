import json

def make_json_report_item(t):
    return  {
        'id': t.get_id(),
        'elements': [ e.name for e in t.get_elements() ],
        'short_decription': t.get_short_description(),
        'long_decription': t.get_long_description(),
    }

class JsonReporter:
    def __init__(self, params):
        self.params = params

    def report(self, results, out_file):
        self.report = {
            'version': '0.0',
            'errors': [make_json_report_item(i) for i in results.get_errors()],
            'questions': [make_json_report_item(i) for i in results.get_questions()],
            'threats': [make_json_report_item(i) for i in results.get_threats()],
        }
        json.dump(self.report, out_file, sort_keys=True, indent=4)

