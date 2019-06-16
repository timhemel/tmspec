from antlr4.error.ErrorListener import ErrorListener
from antlr4 import *

import sys
sys.path.insert(0, '..')
from tmspecLexer import *
from tmspecParser import *
from TmspecError import *
from TmspecModelVisitor import *

class ExceptionErrorListener(ErrorListener):

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise TmspecErrorParseError(msg, TmspecInputContext(line, column))


def _get_parse_tree(inp):
    error_listener = ExceptionErrorListener()
    lexer = tmspecLexer(inp)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)
    stream = CommonTokenStream(lexer)
    parser = tmspecParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    tree = parser.start()
    return tree

def _get_model(tree):
    visitor = TmspecModelVisitor()
    model = visitor.visit(tree)
    return model

def _parseStream(inp):
    tree = _get_parse_tree(inp)
    model = _get_model(tree)
    return model

def parseFile(fn):
    inp = FileStream(fn)
    return _parseStream(inp)

def parseString(data):
    inp = InputStream(data)
    return _parseStream(inp)

def parseStdin():
    inp = StdinStream()
    return _parseStream(inp)


