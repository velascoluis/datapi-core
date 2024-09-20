import yaml
import re
import os
from typing import List, Dict, Optional


class ResourceConfig:
    def __init__(self, yaml_file: str, project_path: str):
        with open(yaml_file, "r") as file:
            data = yaml.safe_load(file)

        self.resource_name = data.get("resource_name")
        self.type = data.get("type")
        self.metastore_uri = data.get("metastore_uri")
        self.local_engine = data.get("local_engine")
        self.short_description = data.get("short_description")
        self.long_description = data.get("long_description")
        self.deploy = data.get("deploy")
        
        self.depends_on: List[Dict[str, str]] = data.get("depends_on", [])
        self.depends_on_namespace: Optional[str] = None
        self.depends_on_table: Optional[str] = None
        self.depends_on_location: Optional[str] = None

        for item in self.depends_on:
            if isinstance(item, dict):
                if "namespace" in item:
                    self.depends_on_namespace = item["namespace"]
                elif "table" in item:
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

    def _generate_malloy_query(self) -> tuple[str, str]:
        if not self.depends_on_table:
            raise ValueError("depends_on_table is required for generating Malloy query")

        source = self._generate_malloy_source()
        query = self._generate_malloy_run_query()

        return source, query

    def _generate_malloy_source(self) -> str:
        return f"""source: {self.depends_on_table} is {self.local_engine}.table('{self.depends_on_table}')"""

    def _generate_malloy_run_query(self) -> str:
        query_parts: List[str] = []
        if self.aggregate:
            query_parts.append(self._generate_aggregate_part())

        if self.group_by:
            query_parts.append(f"  group_by: {self.group_by}")
        if self.filters:
            query_parts.append(f"  where: {self.filters}")

        if not query_parts:
            return ""

        return f"""
run: {self.depends_on_table} -> {{
{" ".join(query_parts)}
}}"""

    def _generate_aggregate_part(self) -> str:
        match = re.match(r"([\w\.]+)\((.*?)\)", self.aggregate)
        if not match:
            raise ValueError(f"Invalid aggregate format: {self.aggregate}")

        agg_function = match.group(1).split(".")[-1].lower()
        agg_field = match.group(2)

        if agg_field:
            alias = f"{agg_field.replace('.', '_')}_{agg_function}"
        elif '.' in match.group(1):
            alias = f"{match.group(1).replace('.', '_')}"
        else:
            alias = f"{agg_function}"

        return f"  aggregate: {alias} is {self.aggregate}"
