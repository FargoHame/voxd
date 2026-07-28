from importlib import metadata, util
from pathlib import Path

import httpx
import typer
import uvicorn

from voxd import __version__
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

    typer.echo(f"Voxd Runtime {__version__}")


@cli.command()
def doctor():
    """Show local runtime diagnostics."""

    typer.echo("Voxd doctor")
    typer.echo("Python support: >=3.11,<3.14")
    typer.echo(f"API base URL: {base_url()}")
    typer.echo(f"Database: {settings.database_path}")
    typer.echo(f"Models: {settings.models_dir}")

    for package in ["fastapi", "uvicorn", "typer", "voicehub", "kokoro", "piper"]:
        spec = util.find_spec(package)
        status = "installed" if spec is not None else "missing"
        location = spec.origin if spec is not None else ""
        version_text = _package_version(package)
        typer.echo(f"{package:<10} {status:<9} {version_text} {location}".rstrip())

    try:
        response = httpx.get(f"{base_url()}/health", timeout=2)
        response.raise_for_status()
        typer.echo("server     reachable")
    except httpx.HTTPError:
        typer.echo("server     not reachable")


@cli.command()
def ps():
    """Show the currently loaded model."""

    response = _request("GET", "/runtime")

    data = response.json()

    if data["loaded"]:
        typer.echo(f"Loaded: {data['model']} ({data['engine']})")
    else:
        typer.echo("No model loaded.")


@cli.command()
def load(model: str):
    """Load a model."""

    response = _request(
        "POST",
        "/runtime/load",
        json={
            "model": model,
        },
    )

    data = response.json()

    typer.echo(f"Loaded model '{data['model']}' using engine '{data['engine']}'.")


@cli.command()
def unload():
    """Unload the current model."""

    _request("POST", "/runtime/unload")

    typer.echo("Runtime unloaded.")


@cli.command()
def run(
    model: str,
    text: str,
    output: Path = typer.Option(
        Path("speech.wav"),
        "--output",
        "-o",
        help="Path to write the generated audio.",
    ),
    voice: str | None = typer.Option(
        None,
        "--voice",
        help="Voice name or voice reference supported by the selected model.",
    ),
    speed: float | None = typer.Option(
        None,
        "--speed",
        help="Speech speed supported by the selected model.",
    ),
):
    """Generate speech with a local runtime server."""

    payload = {
        "model": model,
        "input": text,
    }

    if voice is not None:
        payload["voice"] = voice
    if speed is not None:
        payload["speed"] = speed

    response = _request(
        "POST",
        "/audio/speech",
        json=payload,
        timeout=None,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(response.content)

    typer.echo(f"Wrote {output}")


@cli.command()
def pull(model: str):
    """Download and install a model from the catalog."""

    mgr = ModelManager()
    mgr.install(model)
    typer.echo(f"Model '{model}' installed.")


@cli.command()
def list():
    """List available models and install status."""

    mgr = ModelManager()
    available = mgr.available_models()
    installed = {m.model_name: m for m in mgr.installed_models()}

    if not available:
        typer.echo("No models available.")
        return

    for model in available:
        marker = "*" if model.name in installed else " "
        size = (
            installed[model.name].size_bytes
            if model.name in installed
            else model.size_bytes
        )
        typer.echo(f"{marker} {model.name:<20} {model.engine:<10} {size:>10,} bytes")


@cli.command()
def rm(model: str):
    """Remove an installed model and its files."""

    mgr = ModelManager()
    mgr.remove(model)
    typer.echo(f"Model '{model}' removed.")


def _package_version(package: str) -> str:
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return ""


def _request(method: str, path: str, **kwargs) -> httpx.Response:
    try:
        response = httpx.request(method, f"{base_url()}{path}", **kwargs)
        response.raise_for_status()
        return response
    except httpx.ConnectError as exc:
        typer.echo(
            "Voxd server is not reachable. Start it with `voxd serve`.", err=True
        )
        raise typer.Exit(1) from exc
    except httpx.HTTPStatusError as exc:
        detail = _error_detail(exc.response)
        typer.echo(f"Request failed: {detail}", err=True)
        raise typer.Exit(1) from exc


def _error_detail(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text

    return data.get("detail", response.text)


if __name__ == "__main__":
    cli()
