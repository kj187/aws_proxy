
import click

from aws_proxy.opensearch.proxy import OpenSearchProxy


@click.command()
@click.option('-p', '--local-bind-port', default=6951, help='Define local port to bind')
@click.option('-n', '--domain-name', help='Instead of get a list of all available OpenSearch domains, just choose a pre-defined one')
@click.pass_obj
def opensearch(ctx, local_bind_port: int, domain_name: str):
    """Proxy with AWS OpenSearch (Elasticsearch) service"""

    kwargs = {
        "logger": ctx.get('logger'),
        "pre_defined_name": domain_name,
        "local_bind_port": local_bind_port,
        "aws_client": ctx.get('aws_client'),
        "bastion": ctx.get('bastion'),
    }

    OpenSearchProxy(**kwargs).start()
