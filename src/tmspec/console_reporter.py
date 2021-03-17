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

def report_question_item(i):
    click.secho('QUESTION:', fg='yellow', bold=True)
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
        if self.params['report_errors']:
            for i in results.get_errors():
                report_error_item(i)
        if self.params['report_questions']:
            for i in results.get_questions():
                report_question_item(i)
        if self.params['report_threats']:
            for i in results.get_threats():
                report_threat_item(i)
        # click.secho('Errors', fg='red')
        # click.secho('Questions', fg='bright_yellow')
        # click.secho('Threats', fg='magenta')
        # click.secho('TODO: Warnings', fg='yellow')

