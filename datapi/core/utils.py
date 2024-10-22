import importlib.util
import os
import shutil
import click
import subprocess
from google.cloud import run_v2

# Update these import statements
from datapi.third_party.malloy_py.src.malloy import runtime
from datapi.third_party.malloy_py.src.malloy.data.duckdb import DuckDbConnection


def find_datapi_package():
    """Find the location of the datapi package."""
    spec = importlib.util.find_spec("datapi")
    if spec is None:
        raise ImportError("datapi package not found in the Python path")
    
    if spec.origin:
        print(f"datapi origin: {spec.origin}")  # Debugging statement
        return os.path.dirname(spec.origin)
    elif spec.submodule_search_locations:
        path = next(iter(spec.submodule_search_locations))
        print(f"datapi submodule search location: {path}")  # Debugging statement
        return path
    else:
        raise ImportError("Cannot determine the location of the datapi package.")


def copy_datapi_package(deploy_path):
    try:
        datapi_source = find_datapi_package()
        print(f"datapi_source: {datapi_source}")  # Debugging statement
        datapi_dest = os.path.join(deploy_path, "datapi")
        print(f"datapi_dest: {datapi_dest}")  # Debugging statement
        shutil.copytree(datapi_source, datapi_dest, dirs_exist_ok=True)
    except ImportError as e:
        click.echo(
            f"Warning: {str(e)}. Make sure datapi is installed or in your Python path."
        )
    except Exception as e:
        click.echo(f"Error copying datapi package: {str(e)}")


def check_container_images(resource_name, deployment_config):
    status = "Not found"
    registry_url = deployment_config.get("registry_url", "gcr.io/your-project-id")
    image_name = f"{registry_url}/{resource_name}:latest"

    try:
        result = subprocess.run(
            ["gcloud", "container", "images", "describe", image_name],
            capture_output=True,
            text=True,
            check=True,
        )
        status = "Available"
    except subprocess.CalledProcessError:
        status = "Not found"

    return status


def check_cloud_run_services(resource_name, deployment_config):
    client = run_v2.ServicesClient()
    project_id = deployment_config.get("project_id")
    region = deployment_config.get("region")
    service_name = f"{resource_name}-service"

    try:
        request = run_v2.GetServiceRequest(
            name=f"projects/{project_id}/locations/{region}/services/{service_name}"
        )
        response = client.get_service(request=request)
        
        # Extract the status from the terminal_condition
        status = response.terminal_condition.type_
        
        # Extract the URL from the uri field
        url = response.uri if status == "Ready" else None
        
        return {"status": status, "url": url}
    except Exception as e:
        print(f"Error checking Cloud Run service: {str(e)}")
        return {"status": "NOT_FOUND", "url": None}


async def run_malloy_query(connection, source, query):
    rt = runtime.Runtime()
    rt.add_connection(DuckDbConnection(connection=connection))
    data = await rt.load_source(source).run(query=query)
    return data.to_dataframe()
