import unittest
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
import tempfile
import os

from TmspecError import *
from TmspecParser import *

class TestParseSpec(unittest.TestCase):

    def test_parse(self):
        model = parseString("""
version 0.0;
zone outside;

component webapp(process): zone=outside, cookies;
""")
        outside_zone = list(model.zones)[0]
        types = [t.name for t in model.components['webapp'].get_types()]
        self.assertEqual(types, ['process'])
        self.assertEqual(model.components['webapp'].get_attr('cookies'), True)
        self.assertEqual(model.components['webapp'].get_attr('zone'), outside_zone)

    def test_parse_comments(self):
        model = parseString("""
version 0.0;
zone outside;
# one line comment
// other comment
component webapp(process): /* todo */ zone=outside, cookies;
""")
        outside_zone = list(model.zones)[0]
        types = [t.name for t in model.components['webapp'].get_types()]
        self.assertEqual(types, ['process'])
        self.assertEqual(model.components['webapp'].get_attr('cookies'), True)
        self.assertEqual(model.components['webapp'].get_attr('zone'), outside_zone)


    def test_parse_attribute_types(self):
        model = parseString(r"""
version 0.0;
zone outside;

component webapp(process): zone=outside, foo='bar\'s baz', https=true, lucky_number=13, cookies;
""")
        outside_zone = list(model.zones)[0]
        self.assertEqual(model.components['webapp'].get_attr('cookies'), True)
        self.assertEqual(model.components['webapp'].get_attr('https'), True)
        self.assertEqual(model.components['webapp'].get_attr('lucky_number'), 13)
        self.assertEqual(model.components['webapp'].get_attr('foo'), 'bar\'s baz')
        self.assertEqual(model.components['webapp'].get_attr('zone'), outside_zone)

    def test_parse_attribute_qstring_ends_with_backslash(self):
        model = parseString(r"""
version 0.0;
zone inside;
component webapp(process): foo='bar\'s baz\\', zone=inside;
""")
        self.assertEqual(model.components['webapp'].get_attr('foo'), 'bar\'s baz\\')

    def test_parse_attribute_qstring_with_unicode(self):
        model = parseString(r"""
version 0.0;
zone inside;
component webapp(process): foo='bar\u1234s baz', zone=inside;
""")
        self.assertEqual(model.components['webapp'].get_attr('foo'), 'bar\u1234s baz')

    def test_parse_attribute_qstring_with_newline(self):
        model = parseString(r"""
version 0.0;
zone inside;
component webapp(process): foo='bar\ns baz', zone=inside;
""")
        self.assertEqual(model.components['webapp'].get_attr('foo'), 'bar\ns baz')

    def test_zone_with_attributes(self):
        model = parseString(r"""
version 0.0;
zone inside : default;
""")
        zone = list(model.zones)[0]
        self.assertEqual(zone.get_attr('default'), True)

    def test_element_without_attributes(self):
        model = parseString(r"""
version 0.0;
zone inside;
type compinside(process): zone=inside;
component webapp(compinside);
component database(compinside);
flow store: webapp --> database;
""")
        zone = list(model.zones)[0]
        attrs = model.identifiers['process'].get_attributes()
        attrs['zone'] = zone
        self.assertEqual(model.components['database'].get_attributes(), attrs)



    def test_error_on_duplicate_zone(self):
        with self.assertRaises(TmspecErrorDuplicateIdentifier):
            model = parseString("""
version 0.0;
zone outside;
zone outside;

component webapp(process): zone=outside, cookies;
""")

    def test_error_undefined_zone(self):
        with self.assertRaises(TmspecErrorUnknownIdentifier):
            model = parseString("""
version 0.0;
zone outside;

component webapp(process): zone=inside, cookies;
""")

    def test_conflicting_base_types(self):
        with self.assertRaises(TmspecErrorConflictingTypes):
            model = parseString("""
version 0.0;
zone outside;
component webapp(process, datastore): zone=outside;
""")

    def test_conflicting_derived_types(self):
        with self.assertRaises(TmspecErrorConflictingTypes):
            model = parseString("""
version 0.0;
type encryptedstore(datastore): encryption;
zone outside;
component webapp(process, encryptedstore): zone=outside;
""")

    def test_component_identifier_already_used(self):
        with self.assertRaises(TmspecErrorDuplicateIdentifier):
            model = parseString("""
version 0.0;
zone outside;
component outside(process): zone=outside ;
""")

    def test_component_type_not_a_type(self):
        with self.assertRaises(TmspecErrorNotAType):
            model = parseString("""
version 0.0;
zone outside;
component webapp(process,outside): zone=outside;
""")

    def test_component_unknown_type(self):
        with self.assertRaises(TmspecErrorUnknownIdentifier):
            model = parseString("""
version 0.0;
zone outside;
component webapp(yabbadabbadoo): zone=outside;
""")

    def test_flow_to_type(self):
        with self.assertRaises(TmspecErrorInvalidType):
            model = parseString("""
version 0.0;
zone outside;
component webapp(process): zone=outside;
flow f1: webapp --> process;
""")

    def test_flow_to_arrow(self):
        with self.assertRaises(TmspecErrorInvalidType):
            model = parseString("""
version 0.0;
zone outside;
component webapp(process): zone=outside;
component browser(process): zone=outside;
flow f0: webapp --> browser;
flow f1: webapp --> f0;
""")
 
    def test_errors_report_file_context(self):
        with self.assertRaises(TmspecErrorUnknownIdentifier) as cm:
            model = parseString("""
version 0.0;
zone outside;
component webapp(yabbadabbadoo): zone=outside;
""")
        exc = cm.exception
        self.assertEqual(exc.get_line(), 4)
        self.assertEqual(exc.get_column(), 17)

    def test_parse_error_raises_exception(self):
        with self.assertRaises(TmspecErrorParseError):
            model = parseString("""
yabbadabbadoo
""")

    def test_lexer_error_raises_exception(self):
        with self.assertRaises(TmspecErrorParseError):
            model = parseString("""
*#!@#yabbadabbadoo
""")

    def test_conflicting_types_in_definition(self):
        with self.assertRaises(TmspecErrorConflictingTypes):
            model = parseString("""
version 0.0;
type encryptedstore(datastore,process): encryption;
zone outside;
component login(encryptedstore): zone=outside ;
""")

    def test_conflicting_types_with_derived_type_in_definition(self):
        with self.assertRaises(TmspecErrorConflictingTypes):
            model = parseString("""
version 0.0;
type webapp(process);
type encryptedstore(datastore,webapp): encryption;
zone outside;
component login(encryptedstore): zone=outside;
""")

    def test_component_has_derived_type_attributes(self):
        model = parseString("""
version 0.0;
type encryptedstore(datastore): encryption;
zone outside;
component login(encryptedstore): zone=outside;
""")
        self.assertEqual(model.components['login'].get_attr('encryption'), True)

    def test_component_derived_type_has_direct_parents_only(self):
        model = parseString("""
version 0.0;
type encryptedstore(datastore): encryption;
type secretstore(encryptedstore): sensitive;
zone outside;
component login(secretstore): zone=outside;
""")
        types = model.components['login'].get_types()
        self.assertEqual([t.name for t in types], ['secretstore'])

    def test_component_type_has_multiple_direct_parents(self):
        model = parseString("""
version 0.0;
type encryptedstore(datastore): encryption;
type privatestore(datastore): pii;
zone outside;
component login(encryptedstore,privatestore): zone=outside;
""")
        types = model.components['login'].get_types()
        self.assertEqual([t.name for t in types], ['encryptedstore', 'privatestore'])



    def test_component_cannot_be_flow(self):
        with self.assertRaises(TmspecErrorInvalidType):
            model = parseString("""
version 0.0;
type encryptedflow(dataflow): https;
zone outside;
component login(encryptedflow): zone=outside;
""")

    def test_component_must_have_zone(self):
        with self.assertRaises(TmspecErrorComponentWithoutZone):
            model = parseString("""
version 0.0;
type encryptedstore(datastore): encryption;
zone outside;
component login(encryptedstore);
""")
 

    def test_flow(self):
        model = parseString("""
version 0.0;
type encryptedflow(dataflow): https;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")
        self.assertEqual(model.flows['store_info'].get_attr('pii'), True)
        self.assertEqual(model.flows['store_info'].get_attr('https'), True)
        self.assertEqual(model.flows['store_info'].source, model.components['webapp'])
        self.assertEqual(model.flows['store_info'].target, model.components['database'])

    def test_flow_reverse(self):
        model = parseString("""
version 0.0;
type encryptedflow(dataflow): https;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp <-- database, pii;
""")
        self.assertEqual(model.flows['store_info'].source, model.components['database'])
        self.assertEqual(model.flows['store_info'].target, model.components['webapp'])


    def test_flow_error_duplicate_identifier(self):
        with self.assertRaises(TmspecErrorDuplicateIdentifier):
            model = parseString("""
version 0.0;
type encryptedflow(dataflow): https;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow webapp(encryptedflow): webapp --> database, pii;
""")

    def test_flow_must_be_type_flow(self):
        with self.assertRaises(TmspecErrorInvalidType):
            model = parseString("""
version 0.0;
type encryptedstore(datastore): encryption;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedstore): webapp --> database, pii;
""")

    def test_flow_has_type(self):
        model = parseString("""
version 0.0;
type encryptedflow(dataflow): encryption;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")
        types = [t.name for t in model.flows['store_info'].get_types()]
        self.assertEqual(types, ['encryptedflow'])

    def test_derived_type_has_type(self):
        model = parseString("""
version 0.0;
type encryptedflow(dataflow): encryption;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")
        types = [t.name for t in model.types['encryptedflow'].get_types()]
        self.assertEqual(types, ['dataflow'])

    def test_element_has_position(self):
        model = parseString("""
version 0.0;
type encryptedflow(dataflow): encryption;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")
        tmtype = model.types['encryptedflow']
        self.assertEqual(tmtype.get_position(), (3, 0))

    def test_element_has_filename_string(self):
        model = parseString("""
version 0.0;
type encryptedflow(dataflow): encryption;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")
        tmtype = model.types['encryptedflow']
        self.assertEqual(tmtype.get_filename(), '<string>')

    def test_element_has_filename_file(self):
        s = """
version 0.0;
type encryptedflow(dataflow): encryption;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
"""
        # write s to a file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            print(s, file=f)
            fn = f.name
        try:
            model = parseFile(f.name)
        finally:
            os.unlink(f.name)
        tmtype = model.types['encryptedflow']
        self.assertEqual(tmtype.get_filename(), fn)



if __name__ == "__main__":
    unittest.main()
