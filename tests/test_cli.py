import pytest
from click.testing import CliRunner
from datapi.cli import cli
import os
import shutil

@pytest.fixture
def temp_project_dir(tmp_path):
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    yield project_dir
    shutil.rmtree(project_dir)

def test_init_command(temp_project_dir):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['init', 'test_project'])
        assert result.exit_code == 0
        assert 'Initialized new datapi project in' in result.output

def test_run_command(temp_project_dir):
    runner = CliRunner()
    # Create a mock resource file
    resources_dir = temp_project_dir / "resources"
    resources_dir.mkdir()
    (resources_dir / "test_resource.yml").write_text("# Test resource")
    
    # Create a mock config file
    (temp_project_dir / "config.yml").write_text("project_name: test_project")
    
    with runner.isolated_filesystem():
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['run', '--all'])
        assert result.exit_code == 0

def test_docs_generate_command(temp_project_dir):
    runner = CliRunner()
    # Create a mock resource file
    resources_dir = temp_project_dir / "resources"
    resources_dir.mkdir()
    (resources_dir / "test_resource.yml").write_text("# Test resource")
    
    # Create a mock config file
    (temp_project_dir / "config.yml").write_text("project_name: test_project")
    
    with runner.isolated_filesystem():
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['docs', 'generate', '--all'])
        assert result.exit_code == 0

def test_run_specific_resource(temp_project_dir):
    runner = CliRunner()
    # Create a mock resource file
    resources_dir = temp_project_dir / "resources"
    resources_dir.mkdir()
    (resources_dir / "specific_resource.yml").write_text("# Specific resource")
    
    # Create a mock config file
    (temp_project_dir / "config.yml").write_text("project_name: test_project")
    
    with runner.isolated_filesystem():
        os.chdir(temp_project_dir)
        result = runner.invoke(cli, ['run', 'specific_resource'])
        assert result.exit_code == 0
