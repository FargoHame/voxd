from typer.testing import CliRunner

from hubaks.cli import cli


def test_doctor_runs_without_voicehub():
    result = CliRunner().invoke(cli, ["doctor"])

    assert result.exit_code == 0
    assert "Hubaks doctor" in result.output
    assert "voicehub" in result.output


def test_version_uses_runtime_version():
    result = CliRunner().invoke(cli, ["version"])

    assert result.exit_code == 0
    assert "Hubaks Runtime 1.5.1" in result.output


def test_web_command_is_registered():
    result = CliRunner().invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "web" in result.output


def test_list_shows_available_models():
    result = CliRunner().invoke(cli, ["list"])

    assert result.exit_code == 0
    assert "kokoro" in result.output
    assert "kokoro-british" in result.output
    assert "piper-lessac-low" in result.output
    assert "piper-amy-low" in result.output
