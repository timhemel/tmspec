#!/usr/bin/env python3

import argparse
import pathlib

from TmspecParser import *
from ThreatAnalyzer import ThreatAnalyzer
from ThreatLibrary import ThreatLibrary
from GraphvizDFDRenderer import *

class TmToolApp:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Threat modelling tool')
        parser.add_argument('-d', '--dfd', dest='mode',
            action='store_const', const='dfd',
            help='draw DFD with Graphviz')
        parser.add_argument('-a', '--analyze', dest='mode',
            action='store_const', const='analyze',
            help='analyze DFD against threat library')
        parser.add_argument('-i', '--input', action='store',
            help='load threatmodel from INPUT')
        parser.add_argument('-t', '--threats', action='append',
            help='load threats from THREATS')

        self.args = parser.parse_args()
        print(self.args)
    def run(self):
        if self.args.mode == 'dfd':
            self._makeDFD()
        elif self.args.mode == 'analyze':
            self._analyze_dfd()
    def _makeDFD(self):
        # --dfd -i <input> -o <output>
        try:
            model = parseFile(self.args.input)
            dot = GraphvizDFDRenderer(model).get_dot()
        except TmspecError as e:
            print(e)

    def _analyze_dfd(self):
        # --analyze -t threats1 -t threats2 -i <input>
        try:
            model = parseFile(self.args.input)
            print(model)
            a = ThreatAnalyzer()
            a.set_model(model)
            for tfn in self.args.threats:
                # convert t to prolog file path
                p = pathlib.Path(tfn)
                t = ThreatLibrary()
                t.from_prolog_file(p)
                a.add_threat_library(t)
            results = a.analyze()
        except TmspecError as e:
            print(e)

if __name__ == "__main__":
    TmToolApp().run()
