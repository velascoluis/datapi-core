import pytest
from pathlib import Path
from datapi.core.documentation import Documentation


@pytest.fixture
def documentation():
    project_path = 'new_project'
    return Documentation(project_path=project_path)


@pytest.fixture(autouse=True)
def clean_up(documentation):
    yield
    if documentation.docs_path.exists():
        for file in documentation.docs_path.glob('*'):
            file.unlink()
        documentation.docs_path.rmdir()
    if documentation.resources_path.exists():
        for file in documentation.resources_path.glob('*'):
            file.unlink()
        documentation.resources_path.rmdir()


def test_generate_all(documentation):
    # Create mock resource files
    resources_path = documentation.resources_path
    resources_path.mkdir(parents=True, exist_ok=True)

    (resources_path / "test-resource-1.yml").write_text(
        "# Test resource\nresource_name: test-resource-1\nshort_description: This a sample query\nlong_description: This a sample query"
    )

    (resources_path / "test-resource-2.yml").write_text(
        "# Test resource\nresource_name: test-resource-2\nshort_description: This a sample query\nlong_description: This a sample query"
    )

    documentation.generate()

    assert (documentation.docs_path / "test-resource-1.html").exists()
    assert (documentation.docs_path / "test-resource-2.html").exists()
    assert (documentation.docs_path / "index.html").exists()

    # Check content of generated files
    assert "test-resource-1" in (documentation.docs_path / "test-resource-1.html").read_text()
    assert "test-resource-2" in (documentation.docs_path / "test-resource-2.html").read_text()
    assert "test-resource-1" in (documentation.docs_path / "index.html").read_text()
    assert "test-resource-2" in (documentation.docs_path / "index.html").read_text()


def test_generate_specific_resource(documentation):
    # Create mock resource file
    resources_path = documentation.resources_path
    resources_path.mkdir(parents=True, exist_ok=True)

    (resources_path / "specific-resource.yml").write_text(
        "# Test resource\nresource_name: specific-resource\nshort_description: This a specific query\nlong_description: This a specific query"
    )

    documentation.generate(resource_name="specific-resource")

    assert (documentation.docs_path / "specific-resource.html").exists()
    assert (documentation.docs_path / "index.html").exists()

    # Check content of generated files
    assert "specific-resource" in (documentation.docs_path / "specific-resource.html").read_text()
    assert "specific-resource" in (documentation.docs_path / "index.html").read_text()
