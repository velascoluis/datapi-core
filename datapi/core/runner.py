import asyncio
import time
import click
import glob
import os
import yaml
import shutil
from datapi.core.resource import ResourceConfig
from datapi.core.utils import run_malloy_query
import importlib.util
import sys
import subprocess
from google.cloud import run_v2


class Runner:
    def __init__(self, project_name=None):
        self.project_path = os.getcwd()
        self.project_name = project_name or self._find_project_name()
        self.config = self._load_config()
        self.resources_path = os.path.join(self.project_path, "resources")
        self.deployments_path = os.path.join(self.project_path, "deployments")

        # Create deployments folder if it doesn't exist
        os.makedirs(self.deployments_path, exist_ok=True)

    def _find_project_name(self):
        # Check if we're already in a project directory
        if os.path.exists("config.yml"):
            return os.path.basename(self.project_path)

        # Look for a subdirectory with config.yml
        for item in os.listdir(self.project_path):
            if os.path.isdir(item) and os.path.exists(
                os.path.join(self.project_path, item, "config.yml")
            ):
                self.project_path = os.path.join(self.project_path, item)
                return item

        raise FileNotFoundError(
            "No datapi project found in the current directory or its subdirectories."
        )

    def _load_config(self):
        config_path = os.path.join(self.project_path, "config.yml")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"config.yml not found in the project directory.")
        with open(config_path, "r") as config_file:
            return yaml.safe_load(config_file)

    def run(self, all=False, resource=None):
        if all and resource:
            raise ValueError("Cannot specify both 'all' and 'resource' options.")
        if all:
            self.run_all()
        elif resource:
            self.run_single(resource)
        else:
            raise ValueError("Must specify either 'all' or 'resource' option.")

    def run_all(self):
        resources = self._get_all_resources()
        total = len(resources)
        click.echo(f"Running {total} resources...")
        for idx, resource_file in enumerate(resources, start=1):
            start_time = time.time()
            resource_name = os.path.basename(resource_file)
            click.echo(
                f"{idx} of {total} START create endpoint for {resource_name}[RUN]"
            )
            try:
                asyncio.run(self._run_resource(resource_file))
                duration = time.time() - start_time
                click.echo(
                    f"{idx} of {total} OK endpoint for {resource_name} [OK in {duration:.2f}s]"
                )
            except Exception as e:
                click.echo(
                    f"{idx} of {total} FAILED endpoint for {resource_name} [ERROR: {e}]"
                )
                continue

    def run_single(self, resource_name):
        resource_file = os.path.join(self.resources_path, f"{resource_name}.yml")
        if not os.path.exists(resource_file):
            raise FileNotFoundError(f"Resource file not found: {resource_file}")
        start_time = time.time()
        click.echo(f"START create endpoint for {resource_name}[RUN]")
        try:
            asyncio.run(self._run_resource(resource_file))
            duration = time.time() - start_time
            click.echo(f"OK endpoint for {resource_name} [OK in {duration:.2f}s]")
        except Exception as e:
            click.echo(f"FAILED endpoint for {resource_name} [ERROR: {e}]")

    async def _run_resource(self, resource_file):
        config = ResourceConfig(resource_file, self.project_path)

        # Extract necessary information from the resource config
        source = config.get_malloy_source()
        query = config.get_malloy_query()
        connection = config.local_engine
        resource_name = config.resource_name

        if not query or not connection:
            raise ValueError(
                f"Invalid resource configuration in {resource_file}. 'query' and 'connection' are required."
            )

        # Create resource-specific deployment folder
        resource_deploy_path = os.path.join(self.deployments_path, resource_name)
        os.makedirs(resource_deploy_path, exist_ok=True)

        # Generate FastAPI app
        self._generate_fastapi_app(
            source, query, connection, resource_name, resource_deploy_path
        )

        # Generate Dockerfile
        self._generate_dockerfile(resource_deploy_path)

        # Generate requirements.txt
        self._generate_requirements(resource_deploy_path)

        # Copy datapi package to deployment folder
        self._copy_datapi_package(resource_deploy_path)

        # Build and push container image
        deployment_config = self.config.get("deployment", {})
        registry_url = deployment_config.get("registry_url", "gcr.io/your-project-id")
        image_name = f"{registry_url}/{resource_name}:latest"

        try:
            await self._build_and_push_container(image_name, resource_deploy_path)
            click.echo(f"Successfully built and pushed image: {image_name}")
        except Exception as e:
            click.echo(f"Error building and pushing container: {str(e)}")
            return

        # Deploy the container if specified in the resource config
        if config.deploy:
            await self._deploy_container(image_name, resource_name)

    def _generate_fastapi_app(
        self, source, query, connection, resource_name, deploy_path
    ):
        app_code = f'''
import sys
import asyncio

# Prevent uvloop from being imported
sys.modules['uvloop'] = None

# Ensure we're using the default event loop policy
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Prevent IPython from being imported
sys.modules['IPython'] = None

from fastapi import FastAPI
from datapi.core.utils import run_malloy_query
import os

app = FastAPI()

@app.get("/get_data")
async def get_data():
    source = r"""{source}"""
    query = r"""{query}"""
    connection = {connection!r}
    result = await run_malloy_query(connection, source, query)
    return result

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
'''
        # Write the app code to a file in the deployment folder
        app_file_path = os.path.join(deploy_path, "app.py")
        with open(app_file_path, "w") as app_file:
            app_file.write(app_code)

    def _generate_dockerfile(self, deploy_path):
        dockerfile_content = """
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Clone and set up malloy-py
RUN git clone https://github.com/velascoluis/malloy-py.git && \
    cd malloy-py && \
    git submodule update --init && \
    pip install -r requirements.dev.txt && \
    npm install && \
    scripts/gen-services.sh && \
    cd .. && \
    rm -rf malloy-py/.git

# Copy the rest of the application
COPY . /app

# Ensure datapi package is in the Python path
ENV PYTHONPATH=/app:$PYTHONPATH

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
"""
        dockerfile_path = os.path.join(deploy_path, "Dockerfile")
        with open(dockerfile_path, "w") as dockerfile:
            dockerfile.write(dockerfile_content)

    def _generate_requirements(self, deploy_path):
        requirements_content = """
fastapi
uvicorn[standard]
duckdb
google-cloud-bigquery
pandas
"""
        requirements_path = os.path.join(deploy_path, "requirements.txt")
        with open(requirements_path, "w") as req_file:
            req_file.write(requirements_content)

    async def _build_and_push_container(self, image_name, deploy_path):
        # Use Google Cloud Build to build and push the container
        build_command = f"gcloud builds submit --tag {image_name} ."

        # Build and push the container image using Google Cloud Build
        build_process = await asyncio.create_subprocess_shell(
            build_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=deploy_path,
        )
        stdout, stderr = await build_process.communicate()

        if build_process.returncode != 0:
            raise Exception(f"Build failed: {stderr.decode()}")

        click.echo(stdout.decode())

    async def _deploy_container(self, image_name, resource_name):
        deployment_config = self.config.get("deployment", {})
        service_name = deployment_config.get("service_name", f"{resource_name}-service")
        region = deployment_config.get("region", "us-central1")

        # Deploy to Cloud Run (example using gcloud command)
        deploy_command = f"""
        gcloud run deploy {service_name} \\
            --image {image_name} \\
            --platform managed \\
            --region {region} \\
            --allow-unauthenticated
        """
        deploy_process = await asyncio.create_subprocess_shell(
            deploy_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.project_path,
        )
        stdout, stderr = await deploy_process.communicate()

        if deploy_process.returncode != 0:
            click.echo(f"Deployment failed: {stderr.decode()}")
        else:
            click.echo(stdout.decode())

    def _get_all_resources(self):
        return glob.glob(os.path.join(self.resources_path, "*.yml"))

    def show_all(self):
        resources = self._get_all_resources()
        status = {"resources": {}}
        for resource in resources:
            resource_name = os.path.basename(resource).split(".")[0]
            status["resources"][resource_name] = {
                "container_status": self._check_container_images(resource_name),
                "service_status": self._check_cloud_run_services(resource_name),
            }
        return status

    def _get_resources(self):
        resource_files = glob.glob(os.path.join(self.resources_path, "*.yml"))
        return [os.path.basename(f) for f in resource_files]

    def _check_container_images(self, resource_name):
        status = "Not found"
        deployment_config = self.config.get("deployment", {})
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

    def _check_cloud_run_services(self, resource_name):
        status = "Not deployed"
        client = run_v2.ServicesClient()
        deployment_config = self.config.get("deployment", {})
        project_id = deployment_config.get("project_id")
        region = deployment_config.get("region", "us-central1")
        service_name = f"{resource_name}-service"

        try:
            request = run_v2.GetServiceRequest(
                name=f"projects/{project_id}/locations/{region}/services/{service_name}"
            )
            service = client.get_service(request=request)
            status = "Deployed"
        except Exception:
            status = "Not deployed"

        return status

    def _find_datapi_package(self):
        """Find the location of the datapi package."""
        spec = importlib.util.find_spec("datapi")
        if spec is None:
            raise ImportError("datapi package not found in the Python path")
        return os.path.dirname(spec.origin)

    def _copy_datapi_package(self, deploy_path):
        try:
            datapi_source = self._find_datapi_package()
            datapi_dest = os.path.join(deploy_path, "datapi")
            shutil.copytree(datapi_source, datapi_dest, dirs_exist_ok=True)
            click.echo(f"Copied datapi package from {datapi_source} to {datapi_dest}")
        except ImportError as e:
            click.echo(
                f"Warning: {str(e)}. Make sure datapi is installed or in your Python path."
            )
        except Exception as e:
            click.echo(f"Error copying datapi package: {str(e)}")
