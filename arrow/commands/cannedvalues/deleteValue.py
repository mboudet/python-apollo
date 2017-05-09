import click
from arrow.cli import pass_context, json_loads
from arrow.decorators import apollo_exception, dict_output

@click.command('deleteValue')
@click.argument("id_number")


@pass_context
@bioblend_exception
@dict_output
def cli(ctx, id_number):
    """Warning: Undocumented Method
    """
    return ctx.gi.cannedvalues.deleteValue(id_number)
