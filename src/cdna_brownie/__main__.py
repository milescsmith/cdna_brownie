# type: ignore[attr-defined]
import typer
from chain import chain_app
from rich.console import Console

from cdna_brownie import __version__

app = typer.Typer(
    name="cdna-brownie",
    help="Utilities for processing PacBio long-read RNAseq data",
    add_completion=False,
)

console = Console()
app.add_typer(chain_app, name="chain", help="Chain together multiple IsoSeq samples, reconciliing the differing PBIDs.")


def version_callback(value: bool):
    """Prints the version of the package."""
    if value:
        console.print(
            f"[yellow]cdna-brownie[/] version: [bold blue]{__version__}[/]"
        )
        raise typer.Exit()


@app.command(name="")
def main(
    version: bool = typer.Option(
    None,
    "-v", "--version",
    callback=version_callback,
    is_eager=True,
    help="Prints the version of the cdna-brownie package.",
),
):
    return None

if __name__ == "__main__":
    app()