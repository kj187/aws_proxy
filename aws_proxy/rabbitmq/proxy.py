
from logging import Logger
from rich.prompt import Prompt
from aws_proxy.aws import Aws as AwsClient
from aws_proxy.bastion import Bastion
from aws_proxy.proxy import SshProxy


class RabbitMqProxy(SshProxy):

    pre_defined_name: str
    aws_client: AwsClient

    def __init__(self, logger: Logger, pre_defined_name: str, local_bind_port: int, aws_client: AwsClient, bastion: Bastion):
        super().__init__(logger, local_bind_port, bastion)
        self.pre_defined_name = pre_defined_name
        self.aws_client = aws_client

    def get_broker(self, name: str = "") -> {}:
        brokers = self.aws_client.session.client('mq').list_brokers()
        if 'BrokerSummaries' not in brokers or len(brokers['BrokerSummaries']) <= 0:
            self.logger.error('No RabbitMQ brokers available')
            raise

        _get_broker = lambda _name, _brokers: list(filter(lambda _broker: _broker['BrokerName'] == _name, _brokers['BrokerSummaries']))
        if name:
            broker = _get_broker(name, brokers)
        else:
            choices = list(map(lambda _name: _name['BrokerName'], brokers['BrokerSummaries']))
            name = Prompt.ask("Choose a broker", choices=choices, default=choices[0])
            broker = _get_broker(name, brokers)
        if not broker:
            self.logger.error(f"A broker with the name '{name}' is not available, please check the name")
            raise

        broker = broker[0]
        if broker['BrokerState'] != "RUNNING":
            self.logger.error(f"The broker state is '{broker['BrokerState']}', should be 'RUNNING'")
            raise

        return self.aws_client.session.client('mq').describe_broker(BrokerId=broker['BrokerId'])

    @staticmethod
    def get_broker_port(broker_port: str) -> int:
        port = Prompt.ask(f"Proxy to Management Console (port 443) or to the MQ instance (port {broker_port})", choices=["443", broker_port], default="443")
        return int(port)

    def start(self):
        broker = self.get_broker(self.pre_defined_name)
        address: str = broker['BrokerInstances'][0]['Endpoints'][0].replace('amqps://', '').split(':')
        remote_host: str = address[0]
        remote_port: int = self.get_broker_port(address[1])

        table = self.get_table("AWS RabbitMQ")
        table.add_row("Broker ARN", f"{broker['BrokerArn']}")
        table.add_row("Broker ID", f"{broker['BrokerId']}")
        table.add_row("Broker Name", f"{broker['BrokerName']}")
        table.add_row("Broker Deployment Mode", f"{broker['DeploymentMode']}")
        table.add_row("Broker Engine Version", f"{broker['EngineVersion']}")
        table.add_row("Broker Host", f"{remote_host}")
        table.add_row("Broker Port", f"{remote_port}")

        if remote_port == 443:
            table.add_row("Management Console", f"https://{self.local_bind_host}:{self.local_bind_port}")

        self._start(remote_host=remote_host, remote_port=remote_port)
