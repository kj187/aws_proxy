
from logging import Logger
from rich.prompt import Prompt
from aws_proxy.aws import Aws as AwsClient
from aws_proxy.bastion import Bastion
from aws_proxy.proxy import SshProxy


class RdsProxy(SshProxy):

    pre_defined_name: str
    aws_client: AwsClient

    def __init__(self, logger: Logger, pre_defined_name: str, local_bind_port: int, aws_client: AwsClient, bastion: Bastion):
        super().__init__(logger, local_bind_port, bastion)
        self.pre_defined_name = pre_defined_name
        self.aws_client = aws_client

    def get_instance(self, name: str = "") -> {}:
        instances = self.aws_client.session.client('rds').describe_db_instances()
        if 'DBInstances' not in instances or len(instances['DBInstances']) <= 0:
            self.logger.error('No RDS instances available')
            raise

        _get_instance = lambda _name, _instances: list(filter(lambda _instance: _instance['DBInstanceIdentifier'] == _name, _instances['DBInstances']))
        if name:
            instance = _get_instance(name, instances)
        else:
            choices = list(map(lambda _name: _name['DBInstanceIdentifier'], instances['DBInstances']))
            name = Prompt.ask("Choose an instance", choices=choices, default=choices[0])
            instance = _get_instance(name, instances)
        if not instance:
            self.logger.error(f"An instance with the name '{name}' is not available, please check the name")
            raise

        instance = instance[0]
        if instance['DBInstanceStatus'] != "available":
            self.logger.error(f"The instance status is '{instance['DBInstanceStatus']}', should be 'available'")
            raise

        return instance

    @staticmethod
    def get_broker_port(broker_port: str) -> int:
        port = Prompt.ask(f"Proxy to Management Console (port 443) or to the MQ instance (port {broker_port})", choices=["443", broker_port], default="443")
        return int(port)

    def start(self):
        instance = self.get_instance(self.pre_defined_name)

        remote_host: str = instance['Endpoint']['Address']
        remote_port: int = instance['Endpoint']['Port']

        table = self.get_table("AWS RDS")
        table.add_row("Instance ARN", f"{instance['DBInstanceArn']}")
        table.add_row("Instance Identifier", f"{instance['DBInstanceIdentifier']}")
        table.add_row("Instance DBName", f"{instance['DBName']}")
        table.add_row("Instance Engine", f"{instance['Engine']}")
        table.add_row("Instance Engine Version", f"{instance['EngineVersion']}")
        table.add_row("Instance MasterUsername", f"{instance['MasterUsername']}")
        table.add_row("Instance Host", f"{remote_host}")
        table.add_row("Instance Port", f"{remote_port}")
        table.add_row("", "")
        table.add_row("Examples", "")
        table.add_row("MySQL Client", f"mysql --host {self.local_bind_host} --user {instance['MasterUsername']} --port {self.local_bind_port} -p {instance['DBName']}")

        self._start(remote_host=remote_host, remote_port=remote_port)
