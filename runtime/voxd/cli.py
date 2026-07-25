import httpx
import typer
import uvicorn

from voxd.core.settings import settings
from voxd.services.model_manager import ModelManager

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


@cli.command()
def pull(model: str):
    """Download and install a model from the catalog."""

    mgr = ModelManager()
    mgr.prepare_install("voicehub", model)
    typer.echo(f"Model '{model}' installed.")


@cli.command()
def list():
    """List installed models."""

    mgr = ModelManager()
    models = mgr.installed_models()

    if not models:
        typer.echo("No models installed.")
        return

    for m in models:
        typer.echo(
            f"  {m.model_name:<20} {m.engine:<10} {m.size_bytes:>10,} bytes"
        )


@cli.command()
def rm(model: str):
    """Remove an installed model and its files."""

    mgr = ModelManager()
    mgr.remove(model)
    typer.echo(f"Model '{model}' removed.")


if __name__ == "__main__":
    cli()