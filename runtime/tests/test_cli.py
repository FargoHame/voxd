from typer.testing import CliRunner

from voxd.cli import cli


def test_doctor_runs_without_voicehub():
    result = CliRunner().invoke(cli, ["doctor"])

    assert result.exit_code == 0
    assert "Voxd doctor" in result.output
    assert "voicehub" in result.output
