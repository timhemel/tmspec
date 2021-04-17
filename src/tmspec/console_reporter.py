import click

def report_header():
    click.secho('TmSpec report', fg='white', bold=True)
    click.secho('-------------', fg='white', bold=True)
    click.echo()
    # showing = [ "errors" ]
    # click.secho('Showing:')

def report_error_item(i):
    click.secho('ERROR:', fg='red', bold=True)
    click.secho(f"   {i.get_short_description()}", fg='white', bold=True)
    lines = "\n".join(["   " + x for x in i.get_long_description().split('\r\n')])
    click.secho(f"\n{lines}")
    click.echo()

def report_warning_item(i):
    click.secho('WARNING:', fg='yellow', bold=True)
    click.secho(f"   {i.get_short_description()}", fg='white', bold=True)
    lines = "\n".join(["   " + x for x in i.get_long_description().split('\r\n')])
    click.secho(f"\n{lines}")
    click.echo()

def report_question_item(i):
    click.secho('QUESTION:', fg='cyan', bold=True)
    click.secho(f"   {i.get_short_description()}", fg='white', bold=True)
    lines = "\n".join(["   " + x for x in i.get_long_description().split('\r\n')])
    click.secho(f"\n{lines}")
    click.echo()

def report_threat_item(i):
    click.secho('THREAT:', fg='magenta', bold=True)
    click.secho(f"   {i.get_short_description()}", fg='white', bold=True)
    lines = "\n".join(["   " + x for x in i.get_long_description().split('\r\n')])
    click.secho(f"\n{lines}")
    click.echo()

class ConsoleReporter:
    def __init__(self, params):
        self.params = params

    def report(self, results, out_file):
        report_header()
        report_items = [
            (self.params['report_errors'], results.get_errors(), report_error_item),
            (self.params['report_questions'], results.get_questions(), report_question_item),
            (self.params['report_warnings'], results.get_warnings(), report_warning_item),
            (self.params['report_threats'], results.get_threats(), report_threat_item),
        ]
        for report, items, report_func in report_items:
            if report:
                for i in items:
                    report_func(i)
            if items != [] and self.params['mode_continue'] == False:
                break

        # click.secho('Errors', fg='red')
        # click.secho('Questions', fg='bright_yellow')
        # click.secho('Threats', fg='magenta')
        # click.secho('TODO: Warnings', fg='yellow')

