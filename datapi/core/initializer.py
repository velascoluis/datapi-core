# datapi/core/initializer.py

import os
import click


class Initializer:
    def __init__(self, project_name):
        self.project_name = project_name

    def initialize_project(self):
        if os.path.exists(self.project_name):
            click.echo(f"Error: Project '{self.project_name}' already exists.")
            return

        os.makedirs(os.path.join(self.project_name, "resources"), exist_ok=True)
        os.makedirs(os.path.join(self.project_name, "docs"), exist_ok=True)

        # Create default config.yml
        config_content = """# datapi configuration file

# Metastore URI
metastore_type: polaris
metastore_uri: 'your-metastore-uri'
metastore_credentials: 'your-metastore-credentials'
metastore_catalog: 'your-metastore-catalog'

# Deployment settings
deployment:
  registry_url: 'gcr.io/velascoluis-dev-sandbox' 
  region: 'us-central1'
  
"""

        config_path = os.path.join(self.project_name, "config.yml")
        with open(config_path, "w") as config_file:
            config_file.write(config_content)

        # Create a sample resource file
        sample_resource_content = """resource_name: sample-resource
type: rest
depends_on:
    - table: sample_dataset.sample_table
    - location: bigquery
local_engine: duckdb
short_description: This a sample query
long_description: This a sample query
aggregate: sales.sum()
group_by: quarter
filters: region = 'EMEA'
deploy: True 
"""

        sample_resource_path = os.path.join(
            self.project_name, "resources", "sample_resource.yml"
        )
        with open(sample_resource_path, "w") as resource_file:
            resource_file.write(sample_resource_content)

        click.echo(f"Initialized new datapi project in '{self.project_name}'.")
