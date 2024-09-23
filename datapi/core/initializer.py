# datapi/core/initializer.py

import os
import click
from jinja2 import Environment, FileSystemLoader, ChoiceLoader, PackageLoader

CONFIG_TEMPLATE_NAME = "config.yml.jinja2"
CONFIG_NAME = "config.yml"
SAMPLE_RESOURCE_TEMPLATE_NAME = "sample-resource.yml.jinja2"
SAMPLE_RESOURCE_NAME = "sample-resource.yml"


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

        click.echo(f"Initialized new datapi project in '{self.project_name}'.")

    def _create_config_file(self):
        template = self.jinja_env.get_template(CONFIG_TEMPLATE_NAME)
        config_content = template.render()

        config_path = os.path.join(self.project_name, CONFIG_NAME)
        with open(config_path, "w") as config_file:
            config_file.write(config_content)

    def _create_sample_resource_file(self):
        template = self.jinja_env.get_template(SAMPLE_RESOURCE_TEMPLATE_NAME)
        sample_resource_content = template.render()

        sample_resource_path = os.path.join(
            self.project_name, "resources", SAMPLE_RESOURCE_NAME
        )
        with open(sample_resource_path, "w") as resource_file:
            resource_file.write(sample_resource_content)
