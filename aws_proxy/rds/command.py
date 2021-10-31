
import click

from aws_proxy.rds.proxy import RdsProxy


@click.command()
@click.option('-p', '--local-bind-port', default=6950, help='Define local port to bind')
@click.option('-n', '--instance-name', help='Instead of get a list of all available RDS instances, just choose a pre-defined one')
@click.pass_obj
def rds(ctx, local_bind_port: int, instance_name: str):
    """Proxy with AWS RDS service"""

    kwargs = {
        "logger": ctx.get('logger'),
        "pre_defined_name": instance_name,
        "local_bind_port": local_bind_port,
        "aws_client": ctx.get('aws_client'),
        "bastion": ctx.get('bastion'),
    }

    RdsProxy(**kwargs).start()
