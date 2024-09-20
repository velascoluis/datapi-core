import yaml
import re
import os

class ResourceConfig:
    def __init__(self, yaml_file, project_path):
        with open(yaml_file, "r") as file:
            data = yaml.safe_load(file)

        self.resource_name = data.get("resource_name")
        self.type = data.get("type")
        self.metastore_uri = data.get("metastore_uri")
        self.local_engine = data.get("local_engine")
        self.short_description = data.get("short_description")
        self.long_description = data.get("long_description")
        self.deploy = data.get("deploy")
        # Update depends_on handling
        depends_on = data.get("depends_on", [])
        self.depends_on_table = None
        self.depends_on_location = None

        for item in depends_on:

            if isinstance(item, dict):
                if "table" in item:
                    self.depends_on_table = item["table"]
                elif "location" in item:
                    self.depends_on_location = item["location"]
      
        self.filters = data.get("filters")
        self.aggregate = data.get("aggregate")
        self.group_by = data.get("group_by")

        # Load metastore_uri from config.yml if not specified
        if not self.metastore_uri:
            project_config_path = os.path.join(project_path, 'config.yml')
            with open(project_config_path, 'r') as config_file:
                project_config = yaml.safe_load(config_file)
            self.metastore_uri = project_config.get('metastore_uri')

        self._malloy_source, self._malloy_query = self._generate_malloy_query()

    def __str__(self):
        return f"ResourceConfig: {self.resource_name}"

    def get_malloy_source(self):
        return self._malloy_source

    def get_malloy_query(self):
        return self._malloy_query

    def _generate_malloy_query(self):
        source = f"""source: {self.depends_on_table} is {self.local_engine}.table('{self.depends_on_table}')"""

        query_parts = []
        if self.aggregate:
            match = re.match(r"([\w\.]+)\((.*?)\)", self.aggregate)
            if match:
                agg_function = match.group(1).split(".")[-1].lower()
                agg_field = match.group(2)

                if agg_field:  # Check if a field is provided
                    alias = f"{agg_field.replace('.', '_')}_{agg_function}"
                elif '.' in match.group(1):  # Check for qualified calls like math.sum 
                    alias = f"{match.group(1).replace('.', '_')}"
                else:  # count(*) cases
                    alias = f"{agg_function}"

                query_parts.append(f"  aggregate: {alias} is {self.aggregate}")

        if self.group_by:
            query_parts.append(f"  group_by: {self.group_by}")
        if self.filters:
            query_parts.append(f"  where: {self.filters}")

        query = f"""
run: {self.depends_on_table} -> {{
{" ".join(query_parts)}
}}""" if query_parts else ""

        return source, query
