import re
from typing import List, Optional

class QueryParser:
    def __init__(self, depends_on_table: Optional[str], depends_on_resource: Optional[str], local_engine: str, operation_type: str, select: Optional[List[str]], aggregate: Optional[List[str]], group_by: Optional[List[str]], filters: Optional[str]):
        self.depends_on_table = depends_on_table
        self.depends_on_resource = depends_on_resource
        self.local_engine = local_engine
        self.operation_type = operation_type
        self.select = select
        self.aggregate = aggregate
        self.group_by = group_by
        self.filters = filters

    def generate_malloy_query(self) -> tuple[str, str]:
        source = self._generate_malloy_source()
        query = self._generate_malloy_run_query()
        return source, query

    def _generate_malloy_source(self) -> str:
        if self.depends_on_table:
            return f"""source: {self.depends_on_table} is {self.local_engine}.table('{self.depends_on_table}')"""
        elif self.depends_on_resource:
            return f"""source: resource_data is {self.local_engine}.table('resource_data')"""
        else:
            raise ValueError("Either depends_on_table or depends_on_resource must be provided")

    def _generate_malloy_run_query(self) -> str:
        query_parts: List[str] = []
        if self.operation_type == "PROJECTION" and self.select:
            query_parts.append(self._generate_select_part())
        elif self.operation_type == "REDUCTION":
            if self.aggregate:
                query_parts.append(self._generate_aggregate_part())
            if self.group_by:
                query_parts.append(self._generate_group_by_part())
        if self.filters:
            query_parts.append(self._generate_where_part())

        if not query_parts:
            return ""

        if self.depends_on_table:
            source_name = self.depends_on_table
        elif self.depends_on_resource:
            source_name = "resource_data"
        else:
            raise ValueError("Either depends_on_table or depends_on_resource must be provided")

        return f"""
run: {source_name} -> {{
{' '.join(query_parts)}
}}"""

    def _generate_select_part(self) -> str:
        return f"  select: {self.select}\n"

    def _generate_aggregate_part(self) -> str:
        match = re.match(r"([\w\.]+)\((.*?)\)", self.aggregate)
        if not match:
            raise ValueError(f"Invalid aggregate format: {self.aggregate}")

        agg_function = match.group(1).split(".")[-1].lower()
        agg_field = match.group(2)

        if agg_field:
            alias = f"{agg_field.replace('.', '_')}_{agg_function}"
        elif "." in match.group(1):
            alias = f"{match.group(1).replace('.', '_')}"
        else:
            alias = f"{agg_function}"

        return f"  aggregate: {alias} is {self.aggregate}\n"

    def _generate_group_by_part(self) -> str:
        return f"  group_by: {self.group_by}\n"

    def _generate_where_part(self) -> str:
        return f"  where: {self.filters}\n"
