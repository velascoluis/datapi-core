# datapi/cli.py

import click
from datapi.core.runner import Runner
from datapi.core.documentation import Documentation
from datapi.core.initializer import Initializer


@click.group()
def cli():
    pass


@cli.command()
@click.argument("project_name", required=False, default="datapi_project")
def init(project_name):
    """Initialize a new datapi project"""
    initializer = Initializer(project_name)
    initializer.initialize_project()


@cli.command()
@click.option("--all", "run_all", is_flag=True, help="Run all resources")
@click.option("--resource", "resource_name", help="Run a specific resource")
def run(run_all, resource_name):
    """Run resources"""
    runner = Runner()
    runner.run(all=run_all, resource=resource_name)


@cli.group()
def docs():
    """Documentation related commands"""
    pass


@cli.command()
@click.option("--all", "run_all", is_flag=True, help="Run all resources")
@click.option("--resource", "resource_name", help="Run a specific resource")
def run(run_all, resource_name):
    """Run resources"""
    runner = Runner()
    runner.run(all=run_all, resource=resource_name)


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
def generate(generate_all, resource_name):
    """Generate documentation"""
    documentation = Documentation()
    if generate_all and resource_name:
        click.echo(
            "Error: Cannot use both --all and --resource options simultaneously."
        )
        return
    if generate_all:
        documentation.generate()  # This will generate docs for all resources
    elif resource_name:
        documentation.generate(resource_name=resource_name)
    else:
        click.echo("Error: Please specify either --all or --resource option.")


@docs.command()
@click.option("--port", default=8000, help="Port to serve documentation")
def serve(port):
    """Serve documentation"""
    documentation = Documentation()
    documentation.serve(port=port)


@cli.command()
@click.argument("project_name", required=False, default="datapi_project")
def init(project_name):
    """Initialize a new datapi project"""
    initializer = Initializer(project_name)
    initializer.initialize_project()


@cli.command()
@click.option("--all", "run_all", is_flag=True, help="Run all resources")
@click.option("--resource", "resource_name", help="Run a specific resource")
def run(run_all, resource_name):
    """Run resources"""
    runner = Runner()
    runner.run(all=run_all, resource=resource_name)


@cli.command()
def show():
    """Show all resources and their status"""
    runner = Runner()
    status = runner.show_all()
    if not status['resources']:
        click.echo("No resources found.")
    else:
        click.echo("Resources:")
        for resource, info in status['resources'].items():
            click.echo(f"  {resource}:")
            click.echo(f"    Container: {info['container_status']}")
            click.echo(f"    Service: {info['service_status']}")


@cli.group()
def docs():
    """Documentation related commands"""
    pass


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
def generate(generate_all, resource_name):
    """Generate documentation"""
    documentation = Documentation()
    if generate_all and resource_name:
        click.echo(
            "Error: Cannot use both --all and --resource options simultaneously."
        )
        return
    if generate_all:
        documentation.generate()  # This will generate docs for all resources
    elif resource_name:
        documentation.generate(resource_name=resource_name)
    else:
        click.echo("Error: Please specify either --all or --resource option.")


@docs.command()
@click.option("--port", default=8000, help="Port to serve documentation")
def serve(port):
    """Serve documentation"""
    documentation = Documentation()
    documentation.serve(port=port)


if __name__ == "__main__":
    cli()
