import yaml
import re
import os
from typing import List, Dict, Optional, Any



class ResourceConfig:
    REQUIRED_FIELDS = {
        "resource_name": {"required": True},
        "type": {"required": True, "expected_value": "REST"},
        "local_engine": {"required": True, "expected_value": "DUCKDB"},
        "deploy": {"required": True, "type": bool},
    }

    OPTIONAL_FIELDS = {
        "depends_on": {"type": list},
        # Add other optional fields here if necessary
    }

    def __init__(self, yaml_file: str):
        with open(yaml_file, "r") as file:
            data = yaml.safe_load(file)

        self.resource_name = data.get("resource_name")
        self.type = data.get("type")
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
                if "table" in item:
                    self.depends_on_table = item["table"]
       

        self.filters = data.get("filters")
        self.aggregate = data.get("aggregate")
        self.group_by = data.get("group_by")

        self._validate_config()
        self._malloy_source, self._malloy_query = self._generate_malloy_query()

    def __str__(self):
        return f"ResourceConfig: {self.resource_name}"

    def get_malloy_source(self):
        return self._malloy_source

    def get_malloy_query(self):
        return self._malloy_query

    def _validate_config(self):
        """
        Validates the configuration for ResourceConfig.
        Raises:
            KeyError: If a required key is missing.
            ValueError: If a key has an unexpected value or type.
        """
        for key, criteria in self.REQUIRED_FIELDS.items():
            if criteria.get("required") and key not in self.__dict__:
                raise KeyError(f"Missing required key: '{key}' in the YAML file")
            
            value = getattr(self, key, None)
            if "expected_value" in criteria and value != criteria["expected_value"]:
                raise ValueError(
                    f"Invalid value for '{key}': Expected '{criteria['expected_value']}', got '{value}'"
                )
            if "type" in criteria and not isinstance(value, criteria["type"]):
                raise ValueError(
                    f"Invalid type for '{key}': Expected '{criteria['type'].__name__}', got '{type(value).__name__}'"
                )

        # Validate optional fields
        if self.depends_on:
            if not isinstance(self.depends_on, list):
                raise ValueError(f"'depends_on' should be a list, got '{type(self.depends_on).__name__}'")
            for index, item in enumerate(self.depends_on):
                if not isinstance(item, dict):
                    raise ValueError(f"Each item in 'depends_on' should be a dict, got '{type(item).__name__}' at index {index}")
                if "namespace" not in item or "table" not in item:
                    raise KeyError(
                        f"Each item in 'depends_on' must contain both 'namespace' and 'table' keys. Missing in item at index {index}"
                    )

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
