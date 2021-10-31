import sys

import click
import logging

from rich.console import Console
from rich.logging import RichHandler
from aws_proxy.aws import Aws as AwsClient
from aws_proxy.bastion import Bastion
from aws_proxy.rabbitmq.command import rabbitmq
from aws_proxy.rds.command import rds
from aws_proxy.opensearch.command import opensearch
from aws_proxy.elasticache.command import elasticache

__version__ = '1.0.0'
console = Console()


@click.option('--debug', is_flag=True, help='Show debug output')
@click.option('--aws-profile', required=True, help='The AWS profile name')
@click.option('--bastion-host', required=True, default="", help='Host of ')
@click.option('--bastion-port', required=True, default=22, help='Host of ')
@click.option('--bastion-username', required=True, default="", help='Username for SSH XXXXXXX')
@click.option('--bastion-identity-file', default="", help='Path to SSH identity file')
@click.option('--bastion-config-file', default="~/.ssh/config", help='Path to SSH config file')
@click.group()
@click.pass_context
def cli(
        ctx,
        debug: True,
        aws_profile: str,
        bastion_host: str,
        bastion_port: int,
        bastion_username: str,
        bastion_identity_file: str,
        bastion_config_file: str
):
    """
    AWS Proxy
    The AWS Proxy enables you to reach AWS services which are protected due to a private VPC
    """

    logging_level = "ERROR"
    if debug:
        logging_level = "NOTSET"
    logging.basicConfig(level=logging_level, format="%(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=False)])

    ctx.obj = {
        "logger": logging.getLogger("rich"),
        "aws_client": AwsClient(profile_name=aws_profile),
        "bastion": Bastion(
            host=bastion_host,
            port=bastion_port,
            username=bastion_username,
            identity_file=bastion_identity_file,
            config_file=bastion_config_file,
        )
    }


@click.command()
def version():
    """Show version number"""
    click.echo(__version__)


if __name__ == "__main__":
    try:
        cli.add_command(version)
        cli.add_command(rabbitmq)
        cli.add_command(rds)
        cli.add_command(opensearch)
        cli.add_command(elasticache)
        cli()
    except Exception as error:
        print(f"TODO in main.py: {error}")
        sys.exit(1)
