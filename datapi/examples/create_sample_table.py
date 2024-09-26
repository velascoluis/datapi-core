import argparse
from pyiceberg.catalog.rest import RestCatalog
import pyarrow as pa
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, IntegerType, BooleanType, LongType

def _get_pyiceberg_catalog(polaris_uri, credentials, catalog_name):
    return RestCatalog(
        name="polaris",
        uri=polaris_uri,
        warehouse=catalog_name,
        credential=credentials,
        scope="PRINCIPAL_ROLE:ALL",
    )

def _create_demo_namespace_and_table(catalog, namespace, table_name):
    if namespace in catalog.list_namespaces():
        catalog.drop_namespace(namespace)
    catalog.create_namespace_if_not_exists(namespace)

    df = pa.Table.from_pylist(
        [
            {
                "q": "Q1",
                "product": "Widget",
                "region": "EMEA",
                "sales": 1000,
                "units": 100,
            },
            {
                "q": "Q2",
                "product": "Gadget",
                "region": "EMEA",
                "sales": 1500,
                "units": 150,
            },
            {
                "q": "Q3",
                "product": "Widget",
                "region": "EMEA",
                "sales": 1200,
                "units": 120,
            },
            {
                "q": "Q4",
                "product": "Gadget",
                "region": "EMEA",
                "sales": 2000,
                "units": 200,
            },
        ]
    )

    schema = Schema(
        NestedField(1, "q", StringType(), required=False),
        NestedField(2, "product", StringType(), required=False),
        NestedField(3, "region", StringType(), required=False),
        NestedField(4, "sales", LongType(), required=False),
        NestedField(5, "units", LongType(), required=False),
    )

    if catalog.table_exists(f"{namespace}.{table_name}"):
        catalog.drop_table(f"{namespace}.{table_name}")
    tbl = catalog.create_table_if_not_exists(
        identifier=f"{namespace}.{table_name}",
        schema=schema,
    )
    tbl.append(df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a sample table in PyIceberg.")
    parser.add_argument("--namespace", required=True, help="Namespace for the table")
    parser.add_argument("--table_name", required=True, help="Name of the table")
    parser.add_argument("--polaris_uri", required=True, help="Polaris URI")
    parser.add_argument("--credentials", required=True, help="Credentials for Polaris")
    parser.add_argument("--catalog_name", required=True, help="Catalog name")

    args = parser.parse_args()

    catalog = _get_pyiceberg_catalog(
        polaris_uri=args.polaris_uri,
        credentials=args.credentials,
        catalog_name=args.catalog_name,
    )
    _create_demo_namespace_and_table(catalog, args.namespace, args.table_name)

    table = catalog.load_table(f"{args.namespace}.{args.table_name}")
    con = table.scan().to_arrow()
