#!/usr/bin/env python3

import click
import argparse
import pathlib
import logging

from yldprolog.engine import to_python

from .tmspec_parser import *
from .ThreatAnalyzer import ThreatAnalyzer
from .ThreatLibrary import ThreatLibrary
from .graphviz_dfd_renderer import *
from .quickfix_reporter import QuickfixReporter
from .json_reporter import JsonReporter
from .console_reporter import ConsoleReporter

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
@click.option('-v', '--verbose', is_flag=True)
def main(verbose):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

@main.command()
# TODO: output results instead of showing to screen
# @click.option('-o', '--out-file', type=click.Path(exists=False, allow_dash=True), default='-')
@click.argument('infile', type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, allow_dash=True))
def visualize(infile):
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
@click.argument('properties', nargs=-1, type=str)
def property(threat_libraries, properties):
    """Show help text and values for properties."""
    a = ThreatAnalyzer()
    for tf in threat_libraries:
        t = ThreatLibrary()
        t.from_prolog_file(tf)
        a.add_threat_library(t)

    def make_component(e_type):
        tp = TmType(e_type, None)
        a.add_clause_type(tp)
        component = TmComponent(e_type, None)
        a.add_clause_element(component, tp)
        return component

    def make_flow(e_type):
        tp = TmType(e_type, None)
        a.add_clause_type(tp)
        flow = TmFlow(e_type, None, None, None)
        a.add_clause_element(flow, tp)
        a.add_clause_flow(flow)
        return flow

    def get_property_help(elt, prop):
        a_element = a.query_engine.atom(elt)
        a_property = a.query_engine.atom(prop)
        v_value = a.query_engine.variable()
        v_text = a.query_engine.variable()
        q = a.query_engine.query('prop_help', [a_element, a_property, v_value, v_text])
        return [ (to_python(v_value), to_python(v_text)) for r in q ]

    elements = [ make_component(e_type) for e_type in [ 'externalentity', 'process', 'datastore']] + [ make_flow('dataflow') ]
    for p in properties:
        click.secho(f'Property {p}:', fg='white', bold=True)
        click.secho('-' * (len(p) + 10), fg='white', bold=True)
        click.echo()

        docs = [ (elt, get_property_help(elt,p)) for elt in elements ]
        if all([d[1] == [] for d in docs]):
            click.secho('Unknown property', fg='red')
             
        for elt, hlp in docs:
            if hlp != []:
                click.secho(f'For type {elt.name}:')
                for v,t in hlp:
                    if v is not None:
                        click.secho(f'  {v}: {t}')
                    else:
                        click.secho(f'  *: {t}')
            click.echo()


@main.command()
@click.option('-t', '--threat-library', 'threat_libraries', multiple=True, type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, allow_dash=True))
@click.option('-o', '--out-file', type=click.Path(exists=False, allow_dash=True))
@click.option('-c', '--console', 'output_format', flag_value='console', default='console')
@click.option('-j', '--json', 'output_format', flag_value='json')
@click.option('-q', '--quickfix', 'output_format', flag_value='quickfix')
@click.option('--continue/--no-continue', 'mode_continue', default=False)
@click.option('--errors/--no-errors', 'report_errors', default=True)
@click.option('--questions/--no-questions', 'report_questions', default=True)
@click.option('--warnings/--no-warnings', 'report_warnings', default=True)
@click.option('--threats/--no-threats', 'report_threats', default=True)
@click.option('--errors-file', type=click.Path(exists=False, allow_dash=True))
@click.option('--questions-file', type=click.Path(exists=False, allow_dash=True))
@click.option('--warnings-file', type=click.Path(exists=False, allow_dash=True))
@click.option('--threats-file', type=click.Path(exists=False, allow_dash=True))
@click.argument('infiles', nargs=-1, type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True, allow_dash=True))
@click.pass_context
def analyze(ctx, threat_libraries, out_file, output_format, mode_continue, report_errors, report_questions, report_warnings, report_threats, errors_file, questions_file, warnings_file, threats_file, infiles):

    if output_format == 'console':
        reporter = ConsoleReporter(ctx.params)
    elif output_format == 'json':
        reporter = JsonReporter(ctx.params)
    elif output_format == 'quickfix':
        reporter = QuickfixReporter(ctx.params)

    if out_file is not None:
        outf = click.open_file(out_file, "w")
    else:
        if output_format != 'json':
            outf = sys.stderr
        else:
            outf = sys.stdout

    for infile in infiles:
        try:
            results = analyze_specfile(infile, threat_libraries)
            reporter.report(results, outf)
        except TmspecError as e:
            click.echo(e, err=True)

