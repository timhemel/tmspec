#!/usr/bin/env python3

import click
import argparse
import pathlib
from yldprolog.engine import to_python

from .TmspecParser import *
from .ThreatAnalyzer import ThreatAnalyzer
from .ThreatLibrary import ThreatLibrary
from .GraphvizDFDRenderer import *
from .JSONThreatsReporter import JSONThreatsReporter
from . import ErrorsAndQuestionsReporter

def obj_to_prolog(obj):
    if isinstance(obj, TmType):
        s = "t_%s" % obj.name
    elif isinstance(obj, TmElement):
        s = obj.name
    else:
        s = str(obj)
    return repr(s)

def convert_specfile_to_prolog(infile, outf):
    model = parseFile(infile)
    a = ThreatAnalyzer()
    a.set_model(model)
    outf.write("%% DFD prolog code, generated from:\n")
    outf.write(f"%% {infile}\n\n")
    for predicate, answers in a.query_engine._predicates_store.items():
        outf.write("%% %s/%d:\n" % predicate)
        for answer in answers:
            values = ",".join(obj_to_prolog(to_python(x)) for x in answer.values)
            outf.write("%s(%s).\n" % (predicate[0], values))
        outf.write("\n")

def analyze_specfile(infile, threat_libraries):
    model = parseFile(infile)
    a = ThreatAnalyzer()
    a.set_model(model)
    for tfn in threat_libraries:
        p = pathlib.Path(tfn)
        t = ThreatLibrary()
        t.from_prolog_file(p)
        a.add_threat_library(t)
    results = a.analyze()
    return results

class TmToolApp:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Threat modelling tool')
        parser.add_argument('-d', '--dfd', dest='mode',
            action='store_const', const='dfd',
            help='draw DFD with Graphviz')
        parser.add_argument('-a', '--analyze', dest='mode',
            action='store_const', const='analyze',
            help='analyze DFD against threat library')
        parser.add_argument('-P', '--to-prolog', dest='mode',
            action='store_const', const='to_prolog',
            help='output Prolog for DFD and threat libraries')
        parser.add_argument('-i', '--input', action='store',
            help='load threatmodel from INPUT')
        parser.add_argument('-t', '--threats', action='append',
            default=[], help='load threats from THREATS')

        self.args = parser.parse_args()
    def run(self):
        if self.args.mode == 'dfd':
            self._makeDFD()
        elif self.args.mode == 'analyze':
            self._analyze_dfd()
        elif self.args.mode == 'to_prolog':
            self._to_prolog()
    def _makeDFD(self):
        # --dfd -i <input> -o <output>
        try:
            model = parseFile(self.args.input)
            dot = GraphvizDFDRenderer(model).get_dot()
        except TmspecError as e:
            click.echo(e, err=True)

    def _analyze_dfd(self):
        # --analyze -t threats1 -t threats2 -i <input>
        try:
            model = parseFile(self.args.input)
            a = ThreatAnalyzer()
            a.set_model(model)
            for tfn in self.args.threats:
                # convert t to prolog file path
                p = pathlib.Path(tfn)
                t = ThreatLibrary()
                t.from_prolog_file(p)
                a.add_threat_library(t)
            results = a.analyze()
            # write threats to stdout, or to file, depending on output mode
            # threat_report = JSONThreatsReporter(results).get()
            # print(threat_report+'\n', file=sys.stdout)
            report_threats = True
            # write errors & questions to stderr
            error_report = ErrorsAndQuestionsReporter(results, threats=report_threats).get()
            print(error_report, file=sys.stderr)
        except TmspecError as e:
            print(e, file=sys.stderr)
    def _to_prolog(self):
        try:
            model = parseFile(self.args.input)
            a = ThreatAnalyzer()
            a.set_model(model)
            print("%% DFD prolog code\n")
            for predicate, answers in a.query_engine._predicates_store.items():
                print("%% %s/%d:" % predicate)
                for answer in answers:
                    values = ",".join(obj_to_prolog(to_python(x)) for x in answer.values)
                    print("%s(%s)." % (predicate[0], values))
                print()
        except TmspecError as e:
            print(e, file=sys.stderr)
        for tfn in self.args.threats:
            p = pathlib.Path(tfn)
            with open(p,"r") as f:
                print("%%%% Threat library %s\n" % tfn)
                sys.stdout.write(f.read())

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass
    # TmToolApp().run()

@main.command()
# TODO: output results instead of showing to screen
# @click.option('-o', '--out-file', type=click.Path(exists=False, allow_dash=True), default='-')
@click.argument('infile', type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, allow_dash=True))
def visualize(out_file, infile):
    try:
        model = parseFile(infile)
        dot = GraphvizDFDRenderer(model).get_dot()
    except TmspecError as e:
        click.echo(e, err=True)


@main.command()
@click.option('-t', '--threat-library', 'threat_libraries', multiple=True, type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, allow_dash=True))
@click.option('-o', '--out-file', type=click.Path(exists=False, allow_dash=True), default='-')
@click.argument('infiles', nargs=-1, type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, allow_dash=True))
def prolog(threat_libraries, out_file, infiles):
    """Convert dfd spec file and threat libraries to prolog code."""
    outf = click.open_file(out_file, "w")
    # TODO: include built-in tmspec files
    for infile in infiles:
        try:
            convert_specfile_to_prolog(infile, outf)
        except TmspecError as e:
            click.echo(e, err=True)
    # TODO: include built-in libraries
    for tfn in threat_libraries:
        p = pathlib.Path(tfn)
        with open(p,"r") as f:
            outf.write(f"%%%% Threat library {tfn}\n\n")
            outf.write(f.read())


@main.command()
@click.option('-t', '--threat-library', 'threat_libraries', multiple=True, type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, allow_dash=True))
@click.option('-o', '--out-file', type=click.Path(exists=False, allow_dash=True))
@click.argument('infiles', nargs=-1, type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, allow_dash=True))
def analyze(threat_libraries, out_file, infiles):

    if out_file is not None:
        outf = click.open_file(out_file, "w")
    else:
        outf = sys.stderr

    for infile in infiles:
        try:
            results = analyze_specfile(infile, threat_libraries)
            # write threats to stdout, or to file, depending on output mode
            # threat_report = JSONThreatsReporter(results).get()
            # print(threat_report+'\n', file=sys.stdout)
            report_threats = True
            # write errors & questions to stderr
            ErrorsAndQuestionsReporter.report(results, outf, threats=report_threats)
            # outf.write(error_report)
            # outf.write('\n')
        except TmspecError as e:
            click.echo(e, err=True)

if __name__ == "__main__":
    TmToolApp().run()
