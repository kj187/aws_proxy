
from logging import Logger
from rich.pretty import pprint
from rich.prompt import Prompt
from aws_proxy.aws import Aws as AwsClient
from aws_proxy.bastion import Bastion
from aws_proxy.proxy import SshProxy


class OpenSearchProxy(SshProxy):

    pre_defined_name: str
    aws_client: AwsClient

    def __init__(self, logger: Logger, pre_defined_name: str, local_bind_port: int, aws_client: AwsClient, bastion: Bastion):
        super().__init__(logger, local_bind_port, bastion)
        self.pre_defined_name = pre_defined_name
        self.aws_client = aws_client

    def get_domain(self, name: str = "") -> {}:
        domains = self.aws_client.session.client('opensearch').list_domain_names()
        if 'DomainNames' not in domains or len(domains['DomainNames']) <= 0:
            self.logger.error('No OpenSearch instances available')
            raise

        _get_domain = lambda _name, _domain: list(filter(lambda _domain: _domain['DomainName'] == _name, domains['DomainNames']))
        if name:
            domain = _get_domain(name, domains)
        else:
            choices = list(map(lambda _name: _name['DomainName'], domains['DomainNames']))
            name = Prompt.ask("Choose an instance", choices=choices, default=choices[0])
            domain = _get_domain(name, domains)
        if not domain:
            self.logger.error(f"An OpenSearch domain with the name '{name}' is not available, please check the name")
            raise

        domain = domain[0]

        return self.aws_client.session.client('opensearch').describe_domain(DomainName=domain['DomainName'])

    @staticmethod
    def get_broker_port(broker_port: str) -> int:
        port = Prompt.ask(f"Proxy to Management Console (port 443) or to the MQ instance (port {broker_port})", choices=["443", broker_port], default="443")
        return int(port)

    def start(self):
        domain = self.get_domain(self.pre_defined_name)['DomainStatus']

        remote_host: str = domain['Endpoints']['vpc']
        remote_port: int = 443

        table = self.get_table("AWS OpenSearch")
        table.add_row("Domain ARN", f"{domain['ARN']}")
        table.add_row("Domain ID", f"{domain['DomainId']}")
        table.add_row("Domain Name", f"{domain['DomainName']}")
        table.add_row("Domain Engine Version", f"{domain['EngineVersion']}")
        table.add_row("Domain Instance Type", f"{domain['ClusterConfig']['InstanceType']}")
        table.add_row("Domain Instance Count", f"{domain['ClusterConfig']['InstanceCount']}")

        table.add_row("Domain Host", f"{remote_host}")
        table.add_row("Domain Port", f"{remote_port}")
        table.add_row("", "")
        table.add_row("Examples", "")
        table.add_row("API", f"curl -ki https://{self.local_bind_host}:{self.local_bind_port}/_cat/indices")
        table.add_row("Kibana", f"https://{self.local_bind_host}:{self.local_bind_port}/_plugin/kibana")

        self._start(remote_host=remote_host, remote_port=remote_port)
