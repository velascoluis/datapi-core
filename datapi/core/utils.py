import importlib.util
import os
import shutil
import click
import subprocess
from google.cloud import run_v2

from malloy import runtime
from malloy.data.duckdb import DuckDbConnection


def find_datapi_package():
    """Find the location of the datapi package."""
    spec = importlib.util.find_spec("datapi")
    if spec is None:
        raise ImportError("datapi package not found in the Python path")
    return os.path.dirname(spec.origin)


def copy_datapi_package(deploy_path):
    try:
        datapi_source = find_datapi_package()
        datapi_dest = os.path.join(deploy_path, "datapi")
        shutil.copytree(datapi_source, datapi_dest, dirs_exist_ok=True)
        click.echo(f"Copied datapi package from {datapi_source} to {datapi_dest}")
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
    status = "Not deployed"
    client = run_v2.ServicesClient()
    project_id = deployment_config.get("project_id")
    region = deployment_config.get("region")
    service_name = f"{resource_name}-service"

    try:
        request = run_v2.GetServiceRequest(
            name=f"projects/{project_id}/locations/{region}/services/{service_name}"
        )
        _ = client.get_service(request=request)
        status = f" {service_name} deployed"
    except Exception:
        status = f" {service_name} not deployed"

    return status


async def run_malloy_query(connection, source, query):
    rt = runtime.Runtime()
    rt.add_connection(DuckDbConnection(connection=connection))
    data = await rt.load_source(source).run(query=query)
    return data.to_dataframe()
