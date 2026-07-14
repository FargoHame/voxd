import typer
import uvicorn

from voxd.core.settings import settings
from voxd.main import app

cli = typer.Typer(
    help="Voxd Runtime CLI",
    no_args_is_help=True,
)


@cli.command()
def serve(
    reload: bool = typer.Option(
        False,
        "--reload",
        help="Enable auto reload.",
    ),
):
    """Start the Voxd runtime."""

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=reload,
    )


@cli.command()
def version():
    """Print runtime version."""

    typer.echo("Voxd Runtime 0.1.0")


if __name__ == "__main__":
    cli()