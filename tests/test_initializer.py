import os
import pytest
from datapi.core.initializer import Initializer

def test_initialize_project():
    with pytest.raises(FileExistsError):
        initializer = Initializer('existing_project')
        os.makedirs('existing_project')
        initializer.initialize_project()

    initializer = Initializer('new_project')
    initializer.initialize_project()
    assert os.path.exists('new_project')
    assert os.path.exists('new_project/resources')
    assert os.path.exists('new_project/docs')
    assert os.path.exists('new_project/config.yml')
    assert os.path.exists('new_project/resources/sample-resource.yml')
