from antlr4.error.ErrorListener import ErrorListener
from antlr4 import *

# import sys
# sys.path.insert(0, '..')
# TODO: remove this?
from .tmspecLexer import *
from .tmspecParser import *
from .error import *
from .model_creation_visitor import *

class ExceptionErrorListener(ErrorListener):

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise TmspecErrorParseError(msg,
            TmspecInputContext(self.filename, line, column))


def _get_parse_tree(inp, filename):
    # TODO: add filename to lexer and parser...
    error_listener = ExceptionErrorListener(filename)
    lexer = tmspecLexer(inp)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)
    stream = CommonTokenStream(lexer)
    parser = tmspecParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    tree = parser.start()
    return tree

def _get_model(tree, filename):
    visitor = TmspecModelVisitor(filename)
    model = visitor.visit(tree)
    return model

def _parse_stream(inp, filename):
    tree = _get_parse_tree(inp, filename)
    model = _get_model(tree, filename)
    return model

def parse_file(fn):
    inp = FileStream(fn)
    return _parse_stream(inp, str(fn))

def parse_string(data):
    inp = InputStream(data)
    return _parse_stream(inp, '<string>')

def parse_stdin():
    inp = StdinStream()
    return _parse_stream(inp, '<stdin>')


