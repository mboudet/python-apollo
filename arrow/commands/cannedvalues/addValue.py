import click
from arrow.cli import pass_context, json_loads
from arrow.decorators import apollo_exception, dict_output

@click.command('addValue')
@click.argument("value")

@click.option(
    "--metadata",
    help=""
)

@pass_context
@bioblend_exception
@dict_output
def cli(ctx, value, metadata=""):
    """Warning: Undocumented Method
    """
    return ctx.gi.cannedvalues.addValue(value, metadata=metadata)
