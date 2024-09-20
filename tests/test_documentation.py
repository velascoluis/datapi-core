import pytest
from pathlib import Path
from datapi.core.documentation import Documentation

@pytest.fixture
def documentation(tmp_path):
    return Documentation(project_path=tmp_path)

def test_generate_all(documentation):
    # Create mock resource files
    resources_path = documentation.resources_path
    resources_path.mkdir(parents=True)
    (resources_path / 'resource1.yml').touch()
    (resources_path / 'resource2.yml').touch()

    documentation.generate()

    assert (documentation.docs_path / 'resource1.html').exists()
    assert (documentation.docs_path / 'resource2.html').exists()
    assert (documentation.docs_path / 'index.html').exists()

def test_generate_specific_resource(documentation):
    # Create mock resource file
    resources_path = documentation.resources_path
    resources_path.mkdir(parents=True)
    (resources_path / 'specific_resource.yml').touch()

    documentation.generate(resource_name='specific_resource')

    assert (documentation.docs_path / 'specific_resource.html').exists()
    assert (documentation.docs_path / 'index.html').exists()
