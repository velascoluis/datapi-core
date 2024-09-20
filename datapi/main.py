import click
from datapi.core.runner import Runner

@click.group()
def cli():
    pass

@cli.command()
@click.option('--all', is_flag=True, help='Run all resources')
@click.option('--resource', help='Run a specific resource')
def run(all, resource):
    runner = Runner()
    runner.run(all=all, resource=resource)

if __name__ == '__main__':
    cli()
