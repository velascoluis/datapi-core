# datapi/core/initializer.py

import os
import click
from jinja2 import Environment, FileSystemLoader, ChoiceLoader, PackageLoader

CONFIG_TEMPLATE_NAME = "config.yml.jinja2"
CONFIG_NAME = "config.yml"

SAMPLE_RESOURCE_PROJECTION_TEMPLATE_NAME = "sample-resource-projection.yml.jinja2"
SAMPLE_RESOURCE_PROJECTION_NAME = "sample-resource-projection.yml"
SAMPLE_RESOURCE_PROJECTION_DOCS_NAME = "sample-resource-projection-docs.md"

SAMPLE_RESOURCE_REDUCTION_TEMPLATE_NAME = "sample-resource-reduction.yml.jinja2"
SAMPLE_RESOURCE_REDUCTION_NAME = "sample-resource-reduction.yml"
SAMPLE_RESOURCE_REDUCTION_DOCS_NAME = "sample-resource-reduction-docs.md"

DOCS_CSS_FILE = "styles.css"


class Initializer:
    def __init__(self, project_name):
        self.project_name = project_name
        package_loader = PackageLoader("datapi.core", "templates")
        file_loader = FileSystemLoader(
            os.path.join(os.path.dirname(__file__), "templates")
        )
        self.jinja_env = Environment(loader=ChoiceLoader([package_loader, file_loader]))

    def initialize_project(self):
        if os.path.exists(self.project_name):
            raise click.ClickException(
                f"Error: Project '{self.project_name}' already exists."
            )

        os.makedirs(os.path.join(self.project_name, "resources"), exist_ok=True)
        os.makedirs(os.path.join(self.project_name, "docs"), exist_ok=True)

        self._create_config_file()
        self._create_sample_resource_file()
        self._create_css_file()  

        click.echo(f"Initialized new datapi project in '{self.project_name}'.")

    def _create_config_file(self):
        template = self.jinja_env.get_template(CONFIG_TEMPLATE_NAME)
        config_content = template.render()

        config_path = os.path.join(self.project_name, CONFIG_NAME)
        with open(config_path, "w") as config_file:
            config_file.write(config_content)

    def _create_sample_resource_file(self):
        # Create sample projection file and docs
        projection_template = self.jinja_env.get_template(SAMPLE_RESOURCE_PROJECTION_TEMPLATE_NAME)
        projection_content = projection_template.render()

        projection_path = os.path.join(
            self.project_name, "resources", SAMPLE_RESOURCE_PROJECTION_NAME
        )
        with open(projection_path, "w") as projection_file:
            projection_file.write(projection_content)

        projection_docs_template = self.jinja_env.get_template(SAMPLE_RESOURCE_PROJECTION_DOCS_NAME)
        projection_docs_content = projection_docs_template.render()

        projection_docs_path = os.path.join(
            self.project_name, "resources", SAMPLE_RESOURCE_PROJECTION_DOCS_NAME
        )
        with open(projection_docs_path, "w") as projection_docs_file:
            projection_docs_file.write(projection_docs_content)

        # Create sample reduction file and docs
        reduction_template = self.jinja_env.get_template(SAMPLE_RESOURCE_REDUCTION_TEMPLATE_NAME)
        reduction_content = reduction_template.render()

        reduction_path = os.path.join(
            self.project_name, "resources", SAMPLE_RESOURCE_REDUCTION_NAME
        )
        with open(reduction_path, "w") as reduction_file:
            reduction_file.write(reduction_content)

        reduction_docs_template = self.jinja_env.get_template(SAMPLE_RESOURCE_REDUCTION_DOCS_NAME)
        reduction_docs_content = reduction_docs_template.render()

        reduction_docs_path = os.path.join(
            self.project_name, "resources", SAMPLE_RESOURCE_REDUCTION_DOCS_NAME
        )
        with open(reduction_docs_path, "w") as reduction_docs_file:
            reduction_docs_file.write(reduction_docs_content)

    def _create_css_file(self):
        css_template = self.jinja_env.get_template(DOCS_CSS_FILE)
        css_content = css_template.render()

        css_path = os.path.join(self.project_name, "docs", DOCS_CSS_FILE)
        with open(css_path, "w") as css_file:
            css_file.write(css_content)
