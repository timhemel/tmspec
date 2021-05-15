from yldprolog.compiler import compile_prolog_from_string
from yldprolog.compiler import compile_prolog_from_file

class ThreatLibrary:

    def __init__(self):
        self.python_source = ""

    @classmethod
    def from_string(cls, prolog_source):
        t = cls()
        t.python_source = compile_prolog_from_string(prolog_source)
        return t

    @classmethod
    def from_prolog_file(cls, path):
        t = cls()
        with open(path, "r") as f:
            t.python_source = compile_prolog_from_string(f.read())
        return t

    def get_python_source(self):
        return self.python_source
