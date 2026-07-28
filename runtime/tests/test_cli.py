from typer.testing import CliRunner

from voxd.cli import cli


def test_doctor_runs_without_voicehub():
    result = CliRunner().invoke(cli, ["doctor"])

    assert result.exit_code == 0
    assert "Voxd doctor" in result.output
    assert "voicehub" in result.output


def test_version_uses_runtime_version():
    result = CliRunner().invoke(cli, ["version"])

    assert result.exit_code == 0
    assert "Voxd Runtime 1.1.0" in result.output


def test_list_shows_available_models():
    result = CliRunner().invoke(cli, ["list"])

    assert result.exit_code == 0
    assert "kokoro" in result.output
    assert "kokoro-british" in result.output
