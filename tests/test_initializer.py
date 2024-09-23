import os
import shutil
import pytest
from datapi.core.initializer import Initializer

def test_initialize_project():
    project_name = 'new_project'
    
    # Ensure the project directory does not exist before the test
    if os.path.exists(project_name):
        shutil.rmtree(project_name)
    
    initializer = Initializer(project_name)
    initializer.initialize_project()
    
    assert os.path.exists(project_name)
    assert os.path.exists(os.path.join(project_name, 'resources'))
    assert os.path.exists(os.path.join(project_name, 'docs'))
    assert os.path.exists(os.path.join(project_name, 'config.yml'))
    assert os.path.exists(os.path.join(project_name, 'resources', 'sample-resource.yml'))
    
    # Cleanup after test
    shutil.rmtree(project_name)
