import httpx
import typer
import uvicorn

from voxd.core.settings import settings

cli = typer.Typer(
    help="Voxd Runtime CLI",
    no_args_is_help=True,
)


def base_url() -> str:
    return f"http://{settings.host}:{settings.port}/{settings.api_version}"


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
        "voxd.main:app",
        host=settings.host,
        port=settings.port,
        reload=reload,
    )


@cli.command()
def version():
    """Print runtime version."""

    typer.echo("Voxd Runtime 0.1.0")


@cli.command()
def ps():
    """Show the currently loaded model."""

    response = httpx.get(f"{base_url()}/runtime")
    response.raise_for_status()

    data = response.json()

    if data["loaded"]:
        typer.echo(
            f"Loaded: {data['model']} ({data['engine']})"
        )
    else:
        typer.echo("No model loaded.")


@cli.command()
def load(model: str):
    """Load a model."""

    response = httpx.post(
        f"{base_url()}/runtime/load",
        json={
            "model": model,
        },
    )
    response.raise_for_status()

    data = response.json()

    typer.echo(
        f"Loaded model '{data['model']}' using engine '{data['engine']}'."
    )


@cli.command()
def unload():
    """Unload the current model."""

    response = httpx.post(f"{base_url()}/runtime/unload")
    response.raise_for_status()

    typer.echo("Runtime unloaded.")


if __name__ == "__main__":
    cli()