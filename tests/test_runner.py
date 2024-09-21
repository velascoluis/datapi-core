import pytest
from datapi.core.runner import Runner
import os

@pytest.fixture
def runner():
    return Runner()

def test_run_all(runner):
    # Mock the necessary methods and test run_all
    runner._load_config = lambda: None
    runner._run_resource = lambda x: None
    runner._get_resource_files = lambda: ['resource1.yml', 'resource2.yml']
    
    runner.run(all=True)
    # Add assertions based on expected behavior

def test_run_specific_resource(runner):
    # Create a mock resource file
    os.makedirs(runner.resources_path, exist_ok=True)
    resource_file = os.path.join(runner.resources_path, "specific_resource.yml")
    with open(resource_file, "w") as f:
        f.write("# Mock resource file")

    # Mock the necessary methods and test run with specific resource
    runner._load_config = lambda: None
    runner._run_resource = lambda x: None

    runner.run(resource='specific_resource')
    # Add assertions based on expected behavior
