import pytest
from datapi.core.runner import Runner

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
    # Mock the necessary methods and test run with specific resource
    runner._load_config = lambda: None
    runner._run_resource = lambda x: None
    
    runner.run(resource='specific_resource')
    # Add assertions based on expected behavior
