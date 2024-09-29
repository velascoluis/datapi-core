# datapi/cli.py

import os
import click
from functools import wraps
from datapi.core.runner import Runner
from datapi.core.documentation import Documentation
from datapi.core.initializer import Initializer


def ensure_datapi_project(func):
    """Decorator to ensure the command is run inside a datapi project"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        click.echo("Decorator: Checking for config.yml file...")
        if not os.path.exists('config.yml'):
            click.echo("Decorator: Error: This command must be run inside a datapi project. Please run 'datapi init' first.")
            return
        click.echo("Decorator: config.yml file found.")
        return func(*args, **kwargs)
    return wrapper


@click.group()
def cli():
    click.echo("CLI group initialized")


@cli.command()
@click.argument("project_name", required=False, default="datapi_project")
def init(project_name):
    """Initialize a new datapi project"""
    click.echo("Initializing project...")
    initializer = Initializer(project_name)
    initializer.initialize_project()
    click.echo("Project initialized")


@cli.command()
@click.option("--all", "run_all", is_flag=True, help="Run all resources")
@click.option("--resource", "resource_name", help="Run a specific resource")
@ensure_datapi_project
def run(run_all, resource_name):
    """Run resources"""
    click.echo("Running resources...")
    runner = Runner()
    try:
        if resource_name:
            # Check if the resource file exists
            resource_file = os.path.join("resources", f"{resource_name}.yml")
            if not os.path.exists(resource_file):
                raise click.ClickException(f"Resource file '{resource_name}.yml' not found in the resources directory.")
            
            # Check if the resource name in the file matches the file name
            with open(resource_file, 'r') as f:
                import yaml
                resource_data = yaml.safe_load(f)
                file_resource_name = resource_data.get('resource_name')
                if resource_name != file_resource_name:
                    raise click.ClickException(f"Resource name in file ('{file_resource_name}') does not match the file name ('{resource_name}').")

        runner.run(all=run_all, resource=resource_name)
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@cli.group()
def docs():
    """Documentation related commands"""
    click.echo("Docs group initialized")


@docs.command()
@click.option(
    "--all",
    "generate_all",
    is_flag=True,
    help="Generate documentation for all resources",
)
@click.option(
    "--resource", "resource_name", help="Generate documentation for a specific resource"
)
@ensure_datapi_project
def generate(generate_all, resource_name):
    """Generate documentation"""
    click.echo("Generate command called.")
    documentation = Documentation()
    if generate_all and resource_name:
        click.echo("Error: Cannot use both --all and --resource options simultaneously.")
        return
    if generate_all:
        documentation.generate()  # Generate docs for all resources
    elif resource_name:
        documentation.generate(resource_name=resource_name)
    else:
        click.echo("Error: Please specify either --all or --resource option.")


@docs.command()
@click.option("--port", default=8000, help="Port to serve documentation")
@ensure_datapi_project
def serve(port):
    """Serve documentation"""
    click.echo("Serving documentation...")
    documentation = Documentation()
    documentation.serve(port=port)


@cli.command()
@ensure_datapi_project
def show():
    """Show all resources and their status"""
    click.echo("Showing all resources...")
    runner = Runner()
    status = runner.show_all()
    if not status['resources']:
        click.echo("No resources found.")
    else:
        click.echo("Resources:")
        for resource, info in status['resources'].items():
            click.echo(f"  {resource}:")
            click.echo(f"    Container: {info['container_status']:<10}")
            
            # Handle service_status as a dictionary
            service_status = info['service_status']
            if isinstance(service_status, dict):
                click.echo(f"    Service:")
                for key, value in service_status.items():
                    click.echo(f"      {key}: {value}")
            else:
                click.echo(f"    Service:   {service_status:<10}")


if __name__ == "__main__":
    cli()
