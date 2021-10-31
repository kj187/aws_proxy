
import click

from aws_proxy.elasticache.proxy import ElastiCacheProxy


@click.command()
@click.option('-p', '--local-bind-port', default=6953, help='Define local port to bind')
@click.option('-n', '--cluster-name', help='Instead of get a list of all available ElastiCache clusters, just choose a pre-defined one')
@click.pass_obj
def elasticache(ctx, local_bind_port: int, cluster_name: str):
    """Proxy to Amazon ElastiCache (in-memory cache services)"""

    kwargs = {
        "logger": ctx.get('logger'),
        "pre_defined_name": cluster_name,
        "local_bind_port": local_bind_port,
        "aws_client": ctx.get('aws_client'),
        "bastion": ctx.get('bastion'),
    }

    ElastiCacheProxy(**kwargs).start()
