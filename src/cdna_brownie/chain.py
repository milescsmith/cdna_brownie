from pathlib import Path
from typing import Optional

import typer
import pyranges as pr

chain_app = typer.Typer()

@chain_app.command(name="chain_app")
def chain(
    directories: str = typer.Argument(..., help="A comma-separated list of directories (absolute or relative path) corresponding to the samples to reconcile."),
    group_filename: str = typer.Option(..., "group", "g", help="Either a single name matching the transcript group filename in each sample directory or a comma-separated list of group filenames which must be the same length and in the same order as the directories given in the `directories` argument."),
    gff_filename: str = typer.Option(..., "gff", "a", help="Either a single name matching the gff annotation filename in each sample directory or a comma-separated list of group filenames which must be the same length and in the same order as the directories given in the `directories` argument."),
    count_filename: str = typer.Option(..., "count", "c", help="Either a single name matching the count file in each sample directory or a comma-separated list of group filenames which must be the same length and in the same order as the directories given in the `directories` argument."),
    fastq_filename: Optional[str] = typer.Option(None, "fastq", "f", help="Either a single name matching the fastq in each sample directory or a comma-separated list of group filenames which must be the same length and in the same order as the directories given in the `directories` argument."),
) -> None:
    return None