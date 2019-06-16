import unittest

import sys
sys.path.insert(0, '..')
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from tmspecLexer import *
from tmspecParser import *
from TmspecModelVisitor import *

class TestErrorListener(ErrorListener):
    def __init__(self):
        super(TestErrorListener, self).__init__()
        self.errors = []
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append((line, column, msg, e))


class TestParseSpec(unittest.TestCase):

    def get_parse_tree(self, data):
        inp = InputStream(data)
        lexer = tmspecLexer(inp)
        stream = CommonTokenStream(lexer)
        parser = tmspecParser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(TestErrorListener())
        tree = parser.start()
        return tree

    def get_model(self, tree):
        visitor = TmspecModelVisitor()
        model = visitor.visit(tree)
        return model

    def test_parse(self):
        tree = self.get_parse_tree("""
zone outside;

component webapp(process): zone=outside, cookies;
""")
        model = self.get_model(tree)
        outside_zone = list(model.zones)[0]
        self.assertEqual(model.components['webapp'].types, ['process'])
        self.assertEqual(model.components['webapp'].attr['cookies'], True)
        self.assertEqual(model.components['webapp'].attr['zone'], outside_zone)

    def test_parse_attribute_types(self):
        tree = self.get_parse_tree(r"""
zone outside;

component webapp(process): zone=outside, foo='bar\'s baz', https=true, lucky_number=13, cookies;
""")
        model = self.get_model(tree)
        outside_zone = list(model.zones)[0]
        self.assertEqual(model.components['webapp'].attr['cookies'], True)
        self.assertEqual(model.components['webapp'].attr['https'], True)
        self.assertEqual(model.components['webapp'].attr['lucky_number'], 13)
        self.assertEqual(model.components['webapp'].attr['foo'], 'bar\'s baz')
        self.assertEqual(model.components['webapp'].attr['zone'], outside_zone)

    def test_parse_attribute_qstring_ends_with_backslash(self):
        tree = self.get_parse_tree(r"""
component webapp(process): foo='bar\'s baz\\';
""")
        model = self.get_model(tree)
        self.assertEqual(model.components['webapp'].attr['foo'], 'bar\'s baz\\')



    def test_error_on_duplicate_zone(self):
        tree = self.get_parse_tree("""
zone outside;
zone outside;

component webapp(process): zone=outside, cookies;
""")
        try:
            model = self.get_model(tree)
            self.fail()
        except TmspecError:
            pass

    def test_conflicting_base_types(self):
        tree = self.get_parse_tree("""
component webapp(process, dataflow): ;
""")
        try:
            model = self.get_model(tree)
            self.fail()
        except TmspecError:
            pass

    def test_conflicting_derived_types(self):
        tree = self.get_parse_tree("""
type encryptedflow(dataflow): https;

component webapp(process, encryptedflow): ;
""")
        try:
            model = self.get_model(tree)
            self.fail()
        except TmspecError:
            pass




if __name__ == "__main__":
    unittest.main()
