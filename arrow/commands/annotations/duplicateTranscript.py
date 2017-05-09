import click
from arrow.cli import pass_context, json_loads
from arrow.decorators import apollo_exception, dict_output

@click.command('duplicateTranscript')
@click.argument("transcriptId")


@pass_context
@apollo_exception
@dict_output
def cli(ctx, transcriptId):
    """Warning: Undocumented Method
    """
    return ctx.gi.annotations.duplicateTranscript(transcriptId)