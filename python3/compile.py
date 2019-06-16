#!/usr/bin/env python3

import sys
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from tmspecLexer import *
from tmspecParser import *
import argparse

class VerboseErrorListener(ErrorListener):
    def __init__(self):
        super(VerboseErrorListener, self).__init__()
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print(line, column, msg, e)

class CompilerApp:
    def __init__(self):
        parser = argparse.ArgumentParser(description="tmspec compiler")
        parser.add_argument('sourcefile', metavar='SOURCE', type=str,
                            nargs='?', help='tmspec source file')
        parser.add_argument('-d', '--debug', action='store_true',
                            help='generate debug output')
        self.args = parser.parse_args()
    def _error(self, msg):
        sys.stderr.write('Error: '+msg+"\n")
    def _debug(self, *args):
        if self.args.debug:
            self.args.outfile.write('# ' + " ".join([str(a) for a in args]) + '\n')
    def run(self):
        self.args.outfile = sys.stdout
        if self.args.sourcefile is None or self.args.sourcefile == '-':
            inp = StdinStream()
        else:
            try:
                inp = FileStream(self.args.sourcefile, encoding='utf8')
            except IOError:
                self._error("Could not open input file '%s.'" % self.args.sourcefile)
                sys.exit(1)
        self._debug(self.args)
        error_listener = VerboseErrorListener()
        lexer = tmspecLexer(inp)
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)
        stream = CommonTokenStream(lexer)
        parser = tmspecParser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
        tree = parser.start()
        # visitor = YPPrologVisitor(self.args)
        # program = visitor.visit(tree)
        # compiler = YPPrologCompiler(self.args)
        # code = compiler.compileProgram(program)
        # generator = YPPythonCodeGenerator()
        # pythoncode = generator.generate(code)
        # print (pythoncode)
        print(tree)

if __name__ == "__main__":
    CompilerApp().run()
