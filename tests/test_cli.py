import pytest
from click.testing import CliRunner
from datapi.cli import cli

def test_init_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['init', 'test_project'])
        assert result.exit_code == 0
        assert 'Initialized new datapi project in' in result.output

def test_run_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['run', '--all'])
    assert result.exit_code == 0

def test_docs_generate_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['docs', 'generate', '--all'])
    assert result.exit_code == 0
