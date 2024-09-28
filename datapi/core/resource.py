import yaml
from typing import List, Dict, Optional
from .query_parser import QueryParser

class ResourceConfig:
    REQUIRED_FIELDS = {
        "resource_name": {"required": True},
        "type": {"required": True, "expected_value": "REST"},
        "local_engine": {"required": True, "expected_value": "duckdb"},
        "deploy": {"required": True, "type": bool},
        "operation_type": {"required": True, "allowed_values": ["PROJECTION", "REDUCTION"]},
    }

    OPTIONAL_FIELDS = {
        "depends_on": {"type": list},
        "select": {"type": list},
        "filters": {"type": list},
        "aggregate": {"type": list},
        "group_by": {"type": list},
    }

    def __init__(self, yaml_file: str):
        with open(yaml_file, "r") as file:
            data = yaml.safe_load(file)

        # Initialize required fields
        for field, config in self.REQUIRED_FIELDS.items():
            setattr(self, field, data[field])

        # Initialize optional fields
        for field, config in self.OPTIONAL_FIELDS.items():
            setattr(self, field, data.get(field))

        # Special handling for depends_on
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

        self._validate_config()
        self._validate_operation_type()
        self._malloy_source, self._malloy_query = self._generate_malloy_query()

    def __str__(self):
        return f"ResourceConfig: {self.resource_name}"

    def get_malloy_source(self):
        return self._malloy_source

    def get_malloy_query(self):
        return self._malloy_query

    def _validate_config(self):
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

        # Validate operation_type
        if self.operation_type not in self.REQUIRED_FIELDS["operation_type"]["allowed_values"]:
            raise ValueError(f"Invalid operation_type: {self.operation_type}. Must be either 'PROJECTION' or 'REDUCTION'")

        # Validate optional fields
        if self.depends_on:
            if not isinstance(self.depends_on, list):
                raise ValueError(
                    f"'depends_on' should be a list, got '{type(self.depends_on).__name__}'"
                )
            for index, item in enumerate(self.depends_on):
                if not isinstance(item, dict):
                    raise ValueError(
                        f"Each item in 'depends_on' should be a dict, got '{type(item).__name__}' at index {index}"
                    )
                if "namespace" not in item or "table" not in item:
                    raise KeyError(
                        f"Each item in 'depends_on' must contain both 'namespace' and 'table' keys. Missing in item at index {index}"
                    )

    def _validate_operation_type(self):
        if self.operation_type == "PROJECTION":
            if not self.select:
                raise ValueError("'select' field is required for PROJECTION operation")
            if self.aggregate or self.group_by:
                raise ValueError("'aggregate' and 'group_by' are not allowed for PROJECTION operation")
        elif self.operation_type == "REDUCTION":
            if not self.aggregate or not self.group_by:
                raise ValueError("Both 'aggregate' and 'group_by' are required for REDUCTION operation")
            if self.select:
                raise ValueError("'select' field is not allowed for REDUCTION operation")

    def _generate_malloy_query(self) -> tuple[str, str]:
        if not self.depends_on_table:
            raise ValueError("depends_on_table is required for generating Malloy query")

        query_parser = QueryParser(
            depends_on_table=self.depends_on_table,
            local_engine=self.local_engine,
            operation_type=self.operation_type,
            select=self.select,
            aggregate=self.aggregate,
            group_by=self.group_by,
            filters=self.filters
        )
        return query_parser.generate_malloy_query()
