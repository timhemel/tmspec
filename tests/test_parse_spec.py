import pytest
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
import tempfile
import os

from tmspec.error import *
from tmspec.parser import *


def test_parse():
    model = parse_string("""
version 0.0;
zone outside;

component webapp(process): zone=outside, cookies;
""")
    outside_zone = model.zones['outside']
    types = [t.name for t in model.components['webapp'].types]
    assert types == ['process']
    assert model.components['webapp'].get('cookies') == True
    assert model.components['webapp'].get('zone') == outside_zone

def test_parse_comments():
    model = parse_string("""
version 0.0;
zone outside;
# one line comment
// other comment
component webapp(process): /* todo */ zone=outside, cookies;
""")
    outside_zone = model.zones['outside']
    types = [t.name for t in model.components['webapp'].types]
    assert types == ['process']
    assert model.components['webapp'].get('cookies') == True
    assert model.components['webapp'].get('zone') == outside_zone


def test_parse_attribute_types():
    model = parse_string(r"""
version 0.0;
zone outside;

component webapp(process): zone=outside, foo='bar\'s baz', https=true, team=red, lucky_number=13, cookies;
""")
    outside_zone = model.zones['outside']
    assert model.components['webapp'].get('cookies') == True
    assert model.components['webapp'].get('https') == True
    assert model.components['webapp'].get('team') == 'red'
    assert model.components['webapp'].get('lucky_number') == 13
    assert model.components['webapp'].get('foo') == 'bar\'s baz'
    assert model.components['webapp'].get('zone') == outside_zone

def test_parse_inherited_attributes():
    model = parse_string(r"""
version 0.0;
zone outside;

type tlsed(process): https = true;
type redteam(process): team = red;

component webapp(tlsed,redteam): zone=outside, foo='bar\'s baz', lucky_number=13, cookies;
""")
    outside_zone = model.zones['outside']
    assert model.components['webapp'].get('cookies') == True
    assert model.components['webapp'].get('https') == True
    assert model.components['webapp'].get('team') == 'red'
    assert model.components['webapp'].get('lucky_number') == 13
    assert model.components['webapp'].get('foo') == 'bar\'s baz'
    assert model.components['webapp'].get('zone') == outside_zone



def test_parse_zone_attributes():
    model = parse_string(r"""
version 0.0;
zone company;
zone office: zone=company, network=ethernet;

component webapp(process): zone=office;
""")
    company_zone = model.zones['company']
    assert model.zones['office'].get('zone') == company_zone
    assert model.zones['office'].get('network') == 'ethernet'


def test_parse_attribute_qstring_ends_with_backslash():
    model = parse_string(r"""
version 0.0;
zone inside;
component webapp(process): foo='bar\'s baz\\', zone=inside;
""")
    assert model.components['webapp'].get('foo') == 'bar\'s baz\\'


def test_parse_attribute_qstring_with_unicode():
    model = parse_string(r"""
version 0.0;
zone inside;
component webapp(process): foo='bar\u1234s baz', zone=inside;
""")
    assert model.components['webapp'].get('foo') == 'bar\u1234s baz'

def test_parse_attribute_qstring_with_newline():
    model = parse_string(r"""
version 0.0;
zone inside;
component webapp(process): foo='bar\ns baz', zone=inside;
""")
    assert model.components['webapp'].get('foo') == 'bar\ns baz'

def test_zone_with_attributes():
    model = parse_string(r"""
version 0.0;
zone inside : default;
""")
    zone = model.zones['inside']
    assert zone.get('default') == True

def test_element_without_attributes():
    model = parse_string(r"""
version 0.0;
zone inside;
type compinside(process): zone=inside;
component webapp(compinside);
component database(compinside);
flow store: webapp --> database;
""")
    zone = model.zones['inside']
    attrs = model.identifiers['process'].attributes
    attrs['zone'] = zone
    assert model.components['database'].attributes == attrs

def test_error_on_duplicate_zone():
    with pytest.raises(TmspecErrorDuplicateIdentifier):
        model = parse_string("""
version 0.0;
zone outside;
zone outside;

component webapp(process): zone=outside, cookies;
""")

def test_error_undefined_zone():
    with pytest.raises(TmspecErrorUnknownIdentifier):
        model = parse_string("""
version 0.0;
zone outside;

component webapp(process): zone=inside, cookies;
""")

def test_error_recursive_zone():
    with pytest.raises(TmspecErrorUnknownIdentifier):
        model = parse_string("""
version 0.0;
zone outside: zone=outside;

component webapp(process): zone=inside, cookies;
""")


def test_conflicting_base_types():
    with pytest.raises(TmspecErrorConflictingTypes):
        model = parse_string("""
version 0.0;
zone outside;
component webapp(process, datastore): zone=outside;
""")

def test_conflicting_derived_types():
    with pytest.raises(TmspecErrorConflictingTypes):
        model = parse_string("""
version 0.0;
type encryptedstore(datastore): encryption;
zone outside;
component webapp(process, encryptedstore): zone=outside;
""")

def test_ok_derived_types():
    model = parse_string("""
version 0.0;
type encryptedstore(datastore): encryption;
zone outside;
component webapp(encryptedstore, datastore): zone=outside;
""")
    assert model.components['webapp'].get('encryption') == True


def test_component_identifier_already_used():
    with pytest.raises(TmspecErrorDuplicateIdentifier):
        model = parse_string("""
version 0.0;
zone outside;
component outside(process): zone=outside ;
""")

def test_component_type_not_a_type():
    with pytest.raises(TmspecErrorNotAType):
        model = parse_string("""
version 0.0;
zone outside;
component webapp(process,outside): zone=outside;
""")

def test_component_unknown_type():
    with pytest.raises(TmspecErrorUnknownIdentifier):
        model = parse_string("""
version 0.0;
zone outside;
component webapp(yabbadabbadoo): zone=outside;
""")

def test_flow_to_type():
    with pytest.raises(TmspecErrorInvalidType):
        model = parse_string("""
version 0.0;
zone outside;
component webapp(process): zone=outside;
flow f1: webapp --> process;
""")

def test_flow_to_arrow():
    with pytest.raises(TmspecErrorInvalidType):
        model = parse_string("""
version 0.0;
zone outside;
component webapp(process): zone=outside;
component browser(process): zone=outside;
flow f0: webapp --> browser;
flow f1: webapp --> f0;
""")

 
def test_errors_report_file_context():
    with pytest.raises(TmspecErrorUnknownIdentifier) as exc_info:
        model = parse_string("""
version 0.0;
zone outside;
component webapp(yabbadabbadoo): zone=outside;
""")
    exc = exc_info.value
    assert exc.line == 4
    assert exc.column == 17

def test_parse_error_raises_exception():
    with pytest.raises(TmspecErrorParseError):
        model = parse_string("""
yabbadabbadoo
""")

def test_lexer_error_raises_exception():
    with pytest.raises(TmspecErrorParseError):
        model = parse_string("""
*#!@#yabbadabbadoo
""")

def test_conflicting_types_in_definition():
    with pytest.raises(TmspecErrorConflictingTypes):
        model = parse_string("""
version 0.0;
type encryptedstore(datastore,process): encryption;
zone outside;
component login(encryptedstore): zone=outside ;
""")

def test_conflicting_types_with_derived_type_in_definition():
    with pytest.raises(TmspecErrorConflictingTypes):
        model = parse_string("""
version 0.0;
type webapp(process);
type encryptedstore(datastore,webapp): encryption;
zone outside;
component login(encryptedstore): zone=outside;
""")

def test_component_has_derived_type_attributes():
    model = parse_string("""
version 0.0;
type encryptedstore(datastore): encryption;
zone outside;
component login(encryptedstore): zone=outside;
""")
    assert model.components['login'].get('encryption') == True

def test_component_derived_type_has_direct_parents_only():
    model = parse_string("""
version 0.0;
type encryptedstore(datastore): encryption;
type secretstore(encryptedstore): sensitive;
zone outside;
component login(secretstore): zone=outside;
""")
    types = model.components['login'].types
    assert [t.name for t in types] == ['secretstore']

def test_component_type_has_multiple_direct_parents():
    model = parse_string("""
version 0.0;
type encryptedstore(datastore): encryption;
type privatestore(datastore): pii;
zone outside;
component login(encryptedstore,privatestore): zone=outside;
""")
    types = model.components['login'].types
    assert [t.name for t in types] == ['encryptedstore', 'privatestore']

def test_component_cannot_be_flow():
    with pytest.raises(TmspecErrorInvalidType):
        model = parse_string("""
version 0.0;
type encryptedflow(dataflow): https;
zone outside;
component login(encryptedflow): zone=outside;
""")

def test_get_unzoned_components():
    model = parse_string("""
version 0.0;
type encryptedstore(datastore): encryption;
component login(encryptedstore);
""")
    assert model.get_zones() == []
    assert len(model.get_zone_components(None)) == 1

def test_flow():
    model = parse_string("""
version 0.0;
type encryptedflow(dataflow): https;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")
    assert model.flows['store_info'].get('pii') == True
    assert model.flows['store_info'].get('https') == True
    assert model.flows['store_info'].source == model.components['webapp']
    assert model.flows['store_info'].target == model.components['database']

def test_flow_reverse():
    model = parse_string("""
version 0.0;
type encryptedflow(dataflow): https;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp <-- database, pii;
""")
    assert model.flows['store_info'].source == model.components['database']
    assert model.flows['store_info'].target == model.components['webapp']


def test_flow_error_duplicate_identifier():
    with pytest.raises(TmspecErrorDuplicateIdentifier):
        model = parse_string("""
version 0.0;
type encryptedflow(dataflow): https;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow webapp(encryptedflow): webapp --> database, pii;
""")

def test_flow_must_be_type_flow():
    with pytest.raises(TmspecErrorInvalidType):
        model = parse_string("""
version 0.0;
type encryptedstore(datastore): encryption;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedstore): webapp --> database, pii;
""")

def test_flow_has_type():
    model = parse_string("""
version 0.0;
type encryptedflow(dataflow): encryption;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")
    types = [t.name for t in model.flows['store_info'].types]
    assert types == ['encryptedflow']

def test_derived_type_has_type():
    model = parse_string("""
version 0.0;
type encryptedflow(dataflow): encryption;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")
    types = [t.name for t in model.types['encryptedflow'].types]
    assert types == ['dataflow']

def test_element_has_position():
    model = parse_string("""
version 0.0;
type encryptedflow(dataflow): encryption;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")
    tmtype = model.types['encryptedflow']
    assert tmtype.position == (3, 0)

def test_element_has_filename_string():
    model = parse_string("""
version 0.0;
type encryptedflow(dataflow): encryption;
zone outside;
component webapp(process): zone=outside;
component database(datastore): zone=outside;

flow store_info(encryptedflow): webapp --> database, pii;
""")
    tmtype = model.types['encryptedflow']
    assert tmtype.filename == '<string>'

def test_element_has_filename_file():
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
        model = parse_file(f.name)
    finally:
        os.unlink(f.name)
    tmtype = model.types['encryptedflow']
    assert tmtype.filename == fn


