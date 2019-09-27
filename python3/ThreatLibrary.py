from yldprolog.compiler import compile_prolog_from_string
from yldprolog.compiler import compile_prolog_from_file

class ThreatLibrary:

    def __init__(self):
        self.python_source = ""

    def from_string(self, prolog_source):
        self.python_source = compile_prolog_from_string(prolog_source)

    def from_prolog_file(self, path):
        with open(path, "r") as f:
            self.python_source = compile_prolog_from_string(f.read())

    def get_python_source(self):
        return self.python_source
