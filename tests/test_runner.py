import pytest
from datapi.core.runner import Runner
import os

@pytest.fixture
def runner():
    return Runner()

def test_run_all(runner, mocker):
    # Mock the necessary methods and test run_all
    mocker.patch.object(runner, '_load_config', return_value=None)
    mocker.patch.object(runner, '_run_resource', return_value=None)
    mocker.patch.object(runner, '_get_all_resources', return_value=['test-resource-1.yml', 'test-resource-2.yml'])
    
    runner.run(all=True)
    
    # Add assertions based on expected behavior
    runner._run_resource.assert_any_call('test-resource-1.yml')
    runner._run_resource.assert_any_call('test-resource-2.yml')
    assert runner._run_resource.call_count == 2

def test_run_specific_resource(runner, mocker):
    # Create a mock resource file
    os.makedirs(runner.resources_path, exist_ok=True)
    resource_file = os.path.join(runner.resources_path, "specific-resource.yml")
    with open(resource_file, "w") as f:
        f.write("# Mock resource file")

    # Mock the necessary methods and test run with specific resource
    mocker.patch.object(runner, '_load_config', return_value=None)
    mocker.patch.object(runner, '_run_resource', return_value=None)

    runner.run(resource='specific-resource')
    
    # Add assertions based on expected behavior
    runner._run_resource.assert_called_once_with(resource_file)
