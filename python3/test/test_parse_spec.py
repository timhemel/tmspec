import unittest

import sys
sys.path.insert(0, '..')
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from tmspecLexer import *
from tmspecParser import *
from TmspecModelVisitor import *
from TmspecError import *

class TestErrorListener(ErrorListener):

    def __init__(self):
        super(TestErrorListener, self).__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append((line, column, msg, e))
        raise TmspecErrorParseError(msg, TmspecErrorContext(line, column))


class TestParseSpec(unittest.TestCase):

    def get_parse_tree(self, data):
        inp = InputStream(data)
        error_listener = TestErrorListener()
        lexer = tmspecLexer(inp)
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)
        stream = CommonTokenStream(lexer)
        parser = tmspecParser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
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
        types = [ t.name for t in model.components['webapp'].get_types() ]
        self.assertEqual(types, ['process'])
        self.assertEqual(model.components['webapp'].get_attr('cookies'), True)
        self.assertEqual(model.components['webapp'].get_attr('zone'), outside_zone)

    def test_parse_attribute_types(self):
        tree = self.get_parse_tree(r"""
zone outside;

component webapp(process): zone=outside, foo='bar\'s baz', https=true, lucky_number=13, cookies;
""")
        model = self.get_model(tree)
        outside_zone = list(model.zones)[0]
        self.assertEqual(model.components['webapp'].get_attr('cookies'), True)
        self.assertEqual(model.components['webapp'].get_attr('https'), True)
        self.assertEqual(model.components['webapp'].get_attr('lucky_number'), 13)
        self.assertEqual(model.components['webapp'].get_attr('foo'), 'bar\'s baz')
        self.assertEqual(model.components['webapp'].get_attr('zone'), outside_zone)

    def test_parse_attribute_qstring_ends_with_backslash(self):
        tree = self.get_parse_tree(r"""
component webapp(process): foo='bar\'s baz\\';
""")
        model = self.get_model(tree)
        self.assertEqual(model.components['webapp'].get_attr('foo'), 'bar\'s baz\\')

    def test_error_on_duplicate_zone(self):
        tree = self.get_parse_tree("""
zone outside;
zone outside;

component webapp(process): zone=outside, cookies;
""")
        with self.assertRaises(TmspecErrorDuplicateIdentifier) as cm:
            model = self.get_model(tree)
        # exc = cm.exception
        # self.assertEqual(exc.msg, "bla")

    def test_error_undefined_zone(self):
        tree = self.get_parse_tree("""
zone outside;

component webapp(process): zone=inside, cookies;
""")
        with self.assertRaises(TmspecErrorUnknownIdentifier):
            model = self.get_model(tree)

    def test_conflicting_base_types(self):
        tree = self.get_parse_tree("""
component webapp(process, dataflow): ;
""")
        with self.assertRaises(TmspecErrorConflictingTypes):
            model = self.get_model(tree)

    def test_conflicting_derived_types(self):
        tree = self.get_parse_tree("""
type encryptedflow(dataflow): https;

component webapp(process, encryptedflow): ;
""")
        with self.assertRaises(TmspecErrorConflictingTypes):
            model = self.get_model(tree)

    def test_component_identifier_already_used(self):
        tree = self.get_parse_tree("""
zone outside;
component outside(process): ;
""")
        with self.assertRaises(TmspecErrorDuplicateIdentifier):
            model = self.get_model(tree)

    def test_component_type_not_a_type(self):
        tree = self.get_parse_tree("""
zone outside;
component webapp(process,outside): ;
""")
        with self.assertRaises(TmspecErrorNotAType):
            model = self.get_model(tree)

    def test_component_unknown_type(self):
        tree = self.get_parse_tree("""
component webapp(yabbadabbadoo): ;
""")
        with self.assertRaises(TmspecErrorUnknownIdentifier):
            model = self.get_model(tree)

    def test_errors_report_file_context(self):
        tree = self.get_parse_tree("""
component webapp(yabbadabbadoo): ;
""")
        with self.assertRaises(TmspecErrorUnknownIdentifier) as cm:
            model = self.get_model(tree)
        exc = cm.exception
        self.assertEqual(exc.get_line(), 2)
        self.assertEqual(exc.get_column(), 17)

    def test_parse_error_raises_exception(self):
        with self.assertRaises(TmspecErrorParseError):
            tree = self.get_parse_tree("""
yabbadabbadoo
""")
            model = self.get_model(tree)

    def test_syntax_error_raises_exception(self):
        with self.assertRaises(TmspecErrorParseError):
            tree = self.get_parse_tree("""
*#!@#yabbadabbadoo
""")
            model = self.get_model(tree)

    def test_conflicting_types_in_definition(self):
        tree = self.get_parse_tree("""
type encryptedflow(dataflow,process): https;

component login(encryptedflow): ;
""")
        with self.assertRaises(TmspecErrorConflictingTypes):
            model = self.get_model(tree)

    def test_conflicting_types_with_derived_type_in_definition(self):
        tree = self.get_parse_tree("""
type webapp(process): ;
type encryptedflow(dataflow,webapp): https;

component login(encryptedflow): ;
""")
        with self.assertRaises(TmspecErrorConflictingTypes):
            model = self.get_model(tree)


    def test_component_has_derived_type_attributes(self):
        tree = self.get_parse_tree("""
type encryptedflow(dataflow): https;

component login(encryptedflow): ;
""")
        model = self.get_model(tree)
        self.assertEqual(model.components['login'].get_attr('https'), True)




if __name__ == "__main__":
    unittest.main()
