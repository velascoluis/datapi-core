from malloy import runtime
from malloy.data.duckdb import DuckDbConnection


async def run_malloy_query(connection, source, query):
    rt = runtime.Runtime()
    rt.add_connection(DuckDbConnection(connection=connection))
    data = await rt.load_source(source).run(query=query)
    return data.to_dataframe()
