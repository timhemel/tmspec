import unittest
import sys
sys.path.insert(0, '..')
from TmspecParser import *
from GraphvizDFDRenderer import *

class TestGraphvizDfd(unittest.TestCase):
    pass

    def test_component_in_zone(self):
        model = parseString("""
version 0.0;
zone outside;
component webapp(process): zone=outside, cookies;
""")

    def test_complete_graph(self):
        model = parseString("""
version 0.0;
zone outside;
zone inside;
component webapp(process): zone=inside, cookies;
component database(datastore): zone=inside;
component user(externalentity): zone=outside;
component browser(process): zone=outside;
flow read: webapp --> database, label='2. check credentials ';
flow read_r: webapp <-- database;
flow login: browser --> webapp, label='1. authenticate';
flow login_r: browser <-- webapp, label='3. send session token';
flow browse: user --> browser;
flow browse_r: user <-- browser;
""")
        dot = GraphvizDFDRenderer(model).get_dot()

    def test_complete_graph_default_zone(self):
        model = parseString("""
version 0.0;
zone outside: default;
zone inside;
component webapp(process): zone=inside, cookies;
component database(datastore): zone=inside;
component user(externalentity): zone=outside;
component browser(process): zone=outside;
flow read: webapp --> database, label='2. check credentials ';
flow read_r: webapp <-- database;
flow login: browser --> webapp, label='1. authenticate';
flow login_r: browser <-- webapp, label='3. send session token';
flow browse: user --> browser;
flow browse_r: user <-- browser;
""")
        dot = GraphvizDFDRenderer(model).get_dot()


if __name__ == "__main__":
    unittest.main()
