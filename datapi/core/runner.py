import asyncio
import time
import click
import glob
import os
import shutil
import logging
import traceback
from datapi.core.resource import ResourceConfig
from datapi.core.utils import (
    copy_datapi_package,
    check_container_images,
    check_cloud_run_services,
)
from datapi.core.config import Config

from jinja2 import Environment, FileSystemLoader, ChoiceLoader, PackageLoader

import dataclasses
import importlib.util
import subprocess
from google.cloud import run_v2
from google.cloud.devtools import cloudbuild_v1
from google.protobuf import duration_pb2

APP_TEMPLATE_NAME = "app.py.jinja2"
DOCKERFILE_TEMPLATE_NAME = "Dockerfile.jinja2"
REQUIREMENTS_TEMPLATE_NAME = "requirements.txt.jinja2"

APP_NAME = "app.py"
DOCKERFILE_NAME = "Dockerfile"
REQUIREMENTS_NAME = "requirements.txt"
CONFIG_FILE = "config.yml"


class Runner:
    def __init__(self, project_name=None):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.project_path = os.getcwd()
        self.project_name = project_name or self._find_project_name()
        self.config = Config(self.project_path)  # Initialize Config
        self.config_data = self.config.config_data  # Access config data
        self.resources_path = os.path.join(self.project_path, "resources")
        self.deployments_path = os.path.join(self.project_path, "deployments")

        package_loader = PackageLoader("datapi.core", "templates")
        file_loader = FileSystemLoader(
            os.path.join(os.path.dirname(__file__), "templates")
        )
        self.jinja_env = Environment(loader=ChoiceLoader([package_loader, file_loader]))

        os.makedirs(self.deployments_path, exist_ok=True)

    def _find_project_name(self):

        if os.path.exists(CONFIG_FILE):
            return os.path.basename(self.project_path)

        # Look for a subdirectory with config.yml
        for item in os.listdir(self.project_path):
            if os.path.isdir(item) and os.path.exists(
                os.path.join(self.project_path, item, CONFIG_FILE)
            ):
                self.project_path = os.path.join(self.project_path, item)
                return item

        raise FileNotFoundError(
            "No datapi project found in the current directory or its subdirectories."
        )

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
                error_message = f"{idx} of {total} FAILED endpoint for {resource_name}"
                error_details = f"Error type: {type(e).__name__}"
                error_traceback = traceback.format_exc()
                
                click.echo(
                    f"{error_message}\n{error_details}\n"
                    f"Error message: {str(e)}\n\n"
                    f"Traceback:\n{error_traceback}"
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
        self.logger.debug(f"Starting to process resource file: {resource_file}")
        try:
            config = ResourceConfig(resource_file)
            self.logger.debug(f"ResourceConfig created: {config}")

            # Extract necessary information from the resource config
            source = config.get_malloy_source()
            query = config.get_malloy_query()
            connection = config.local_engine
            resource_name = config.resource_name

            self.logger.debug(f"Extracted info: source={source}, query={query}, connection={connection}, resource_name={resource_name}")

            depends_on = config.depends_on[0] if config.depends_on else {}
            namespace = depends_on.get("namespace")
            table = depends_on.get("table")

            if not query or not connection:
                raise ValueError(
                    f"Invalid resource configuration in {resource_file}. 'query' and 'connection' are required."
                )

            resource_deploy_path = os.path.join(self.deployments_path, resource_name)
            os.makedirs(resource_deploy_path, exist_ok=True)

            self._generate_fastapi_app(
                source,
                query,
                resource_name,
                resource_deploy_path,
            )

            self._generate_dockerfile(resource_deploy_path)

            self._generate_requirements(resource_deploy_path)

            self._copy_datapi_package(resource_deploy_path)

            deployment_config = self.config.get_deployment_config()
            registry_url = deployment_config.get("registry_url", "gcr.io/your-project-id")
            image_name = f"{registry_url}/{resource_name}:latest"

            try:
                await self._build_and_push_container(image_name, resource_deploy_path)
                click.echo(f"Successfully built and pushed image: {image_name}")
            except Exception as e:
                click.echo(f"Error building and pushing container: {str(e)}")
                return

            if config.deploy:
                await self._deploy_container(image_name, resource_name)

        except Exception as e:
            self.logger.exception(f"Error processing resource file {resource_file}")
            raise

    def _generate_fastapi_app(
        self, source, query, resource_name, deploy_path
    ):
        template = self.jinja_env.get_template(APP_TEMPLATE_NAME)
        
        deployment_config = self.config.get_deployment_config()

        # Get the ResourceConfig for this resource
        resource_config = ResourceConfig(os.path.join(self.resources_path, f"{resource_name}.yml"))

        if resource_config.depends_on_namespace and resource_config.depends_on_table:
            # Case: Depends on namespace and table
            app_content = template.render(
                polaris_uri=self.config.get("metastore_uri", ""),
                credentials=self.config.get("metastore_credentials", ""),
                catalog_name=self.config.get("metastore_catalog", ""),
                namespace_name=resource_config.depends_on_namespace,
                table_name=resource_config.depends_on_table,
                source=source,
                query=query,
                depends_on_type="table"
            )
        elif resource_config.depends_on_resource:
            # Case: Depends on another resource
            service_info = check_cloud_run_services(resource_config.depends_on_resource, deployment_config)
            service_url = service_info['url']
            
            if not service_url:
                raise ValueError(f"Could not find URL for dependent resource: {resource_config.depends_on_resource}")
            
            app_content = template.render(
                polaris_uri=self.config.get("metastore_uri", ""),
                credentials=self.config.get("metastore_credentials", ""),
                catalog_name=self.config.get("metastore_catalog", ""),
                depends_on_resource=service_url,
                source=source,
                query=query,
                depends_on_type="resource"
            )
        else:
            raise ValueError("Invalid dependency configuration")

        app_file_path = os.path.join(deploy_path, APP_NAME)
        with open(app_file_path, "w") as app_file:
            app_file.write(app_content)

    def _generate_dockerfile(self, deploy_path):
        template = self.jinja_env.get_template(DOCKERFILE_TEMPLATE_NAME)
        dockerfile_content = template.render()

        dockerfile_path = os.path.join(deploy_path, DOCKERFILE_NAME)
        with open(dockerfile_path, "w") as dockerfile:
            dockerfile.write(dockerfile_content)

    def _generate_requirements(self, deploy_path):
        template = self.jinja_env.get_template(REQUIREMENTS_TEMPLATE_NAME)
        requirements_content = template.render()

        requirements_path = os.path.join(deploy_path, REQUIREMENTS_NAME)
        with open(requirements_path, "w") as req_file:
            req_file.write(requirements_content)

    async def _build_and_push_container(self, image_name, deploy_path):
        click.echo(f"Building data pod: {image_name}")
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
        deployment_config = self.config.get_deployment_config()
        service_name = deployment_config.get("service_name", f"{resource_name}-service")
        region = deployment_config.get("region")
        click.echo(f"Deploying data pod: {service_name}")
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
        deployment_config = self.config.get_deployment_config()
        return check_container_images(resource_name, deployment_config)

    def _check_cloud_run_services(self, resource_name):
        deployment_config = self.config.get_deployment_config()
        return check_cloud_run_services(resource_name, deployment_config)

    def _copy_datapi_package(self, deploy_path):
        copy_datapi_package(deploy_path)