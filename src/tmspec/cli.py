#!/usr/bin/env python3

import click
import argparse
import pathlib
from yldprolog.engine import to_python

from .TmspecParser import *
from .ThreatAnalyzer import ThreatAnalyzer
from .ThreatLibrary import ThreatLibrary
from .GraphvizDFDRenderer import *
from . import quickfix_reporter
from . import json_reporter
from . import console_reporter

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

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass

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
@click.option('-c', '--console', 'output_format', flag_value='console', default='console')
@click.option('-j', '--json', 'output_format', flag_value='json')
@click.option('-q', '--quickfix', 'output_format', flag_value='quickfix')
@click.argument('infiles', nargs=-1, type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, allow_dash=True))
def analyze(threat_libraries, out_file, output_format, infiles):

    if output_format == 'console':
        reporter = console_reporter.report
    elif output_format == 'json':
        reporter = json_reporter.report
    elif output_format == 'quickfix':
        reporter = quickfix_reporter.report

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
            quickfix_reporter.report(results, outf, threats=report_threats)
        except TmspecError as e:
            click.echo(e, err=True)

