
import click

from aws_proxy.rabbitmq.proxy import RabbitMqProxy


@click.command()
@click.option('-p', '--local-bind-port', default=6952, help='Define local port to bind')
@click.option('-n', '--broker-name', help='Instead of get a list of all available brokers, just choose a pre-defined one')
@click.pass_obj
def rabbitmq(ctx, local_bind_port: int, broker_name: str):
    """Proxy with AWS MQ RabbitMQ service"""

    kwargs = {
        "logger": ctx.get('logger'),
        "pre_defined_name": broker_name,
        "local_bind_port": local_bind_port,
        "aws_client": ctx.get('aws_client'),
        "bastion": ctx.get('bastion'),
    }

    RabbitMqProxy(**kwargs).start()
