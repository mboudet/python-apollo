import click
from arrow.cli import pass_context, json_loads
from arrow.decorators import apollo_exception, dict_output

@click.command('flipStrand')
@click.argument("uniquenames")


@pass_context
@bioblend_exception
@dict_output
def cli(ctx, uniquenames):
    """Warning: Undocumented Method
    """
    return ctx.gi.annotations.flipStrand(uniquenames)
