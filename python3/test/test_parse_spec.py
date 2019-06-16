import unittest
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

import sys
sys.path.insert(0, '..')
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
        raise TmspecErrorParseError(msg, TmspecInputContext(line, column))


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
        types = [t.name for t in model.components['webapp'].get_types()]
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
        with self.assertRaises(TmspecErrorDuplicateIdentifier):
            model = self.get_model(tree)

    def test_error_undefined_zone(self):
        tree = self.get_parse_tree("""
zone outside;

component webapp(process): zone=inside, cookies;
""")
        with self.assertRaises(TmspecErrorUnknownIdentifier):
            model = self.get_model(tree)

    def test_conflicting_base_types(self):
        tree = self.get_parse_tree("""
component webapp(process, datastore): ;
""")
        with self.assertRaises(TmspecErrorConflictingTypes):
            model = self.get_model(tree)

    def test_conflicting_derived_types(self):
        tree = self.get_parse_tree("""
type encryptedstore(datastore): encryption;

component webapp(process, encryptedstore): ;
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
type encryptedstore(datastore,process): encryption;

component login(encryptedstore): ;
""")
        with self.assertRaises(TmspecErrorConflictingTypes):
            model = self.get_model(tree)

    def test_conflicting_types_with_derived_type_in_definition(self):
        tree = self.get_parse_tree("""
type webapp(process): ;
type encryptedstore(datastore,webapp): encryption;

component login(encryptedstore): ;
""")
        with self.assertRaises(TmspecErrorConflictingTypes):
            model = self.get_model(tree)

    # TODO: component cannot have dataflow type

    def test_component_has_derived_type_attributes(self):
        tree = self.get_parse_tree("""
type encryptedstore(datastore): encryption;

component login(encryptedstore): ;
""")
        model = self.get_model(tree)
        self.assertEqual(model.components['login'].get_attr('encryption'), True)

    def test_component_cannot_be_flow(self):
        tree = self.get_parse_tree("""
type encryptedflow(dataflow): https;

component login(encryptedflow): ;
""")
        with self.assertRaises(TmspecErrorInvalidType):
            model = self.get_model(tree)


    def test_flow(self):
        tree = self.get_parse_tree("""
type encryptedflow(dataflow): https;

component webapp(process): ;
component database(datastore): ;

flow store_info(encryptedflow): webapp --> database, pii;
""")
        model = self.get_model(tree)
        self.assertEqual(model.flows['store_info'].get_attr('pii'), True)
        self.assertEqual(model.flows['store_info'].get_attr('https'), True)
        self.assertEqual(model.flows['store_info'].source, model.components['webapp'])
        self.assertEqual(model.flows['store_info'].target, model.components['database'])

    def test_flow_reverse(self):
        tree = self.get_parse_tree("""
type encryptedflow(dataflow): https;

component webapp(process): ;
component database(datastore): ;

flow store_info(encryptedflow): webapp <-- database, pii;
""")
        model = self.get_model(tree)
        self.assertEqual(model.flows['store_info'].source, model.components['database'])
        self.assertEqual(model.flows['store_info'].target, model.components['webapp'])


    def test_flow_error_duplicate_identifier(self):
        tree = self.get_parse_tree("""
type encryptedflow(dataflow): https;

component webapp(process): ;
component database(datastore): ;

flow webapp(encryptedflow): webapp --> database, pii;
""")
        with self.assertRaises(TmspecErrorDuplicateIdentifier):
            model = self.get_model(tree)


    def test_flow_must_be_type_flow(self):
        tree = self.get_parse_tree("""
type encryptedstore(datastore): encryption;

component webapp(process): ;
component database(datastore): ;

flow store_info(encryptedstore): webapp --> database, pii;
""")
        with self.assertRaises(TmspecErrorInvalidType):
            model = self.get_model(tree)






if __name__ == "__main__":
    unittest.main()
