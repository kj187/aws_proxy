
from logging import Logger
from rich.prompt import Prompt
from aws_proxy.aws import Aws as AwsClient
from aws_proxy.bastion import Bastion
from aws_proxy.proxy import SshProxy


class ElastiCacheProxy(SshProxy):

    pre_defined_name: str
    aws_client: AwsClient

    def __init__(self, logger: Logger, pre_defined_name: str, local_bind_port: int, aws_client: AwsClient, bastion: Bastion):
        super().__init__(logger, local_bind_port, bastion)
        self.pre_defined_name = pre_defined_name
        self.aws_client = aws_client

    def get_cluster(self, name: str = "") -> {}:
        clusters = self.aws_client.session.client('elasticache').describe_cache_clusters(ShowCacheNodeInfo=True)
        if 'CacheClusters' not in clusters or len(clusters['CacheClusters']) <= 0:
            self.logger.error('No Cache clusters available')
            raise

        # if len(clusters['CacheClusters']) == 1:
        #     return clusters['CacheClusters'][0]

        _get_cluster = lambda _name, _cluster: list(filter(lambda _cluster: _cluster['CacheClusterId'] == _name, clusters['CacheClusters']))
        if name:
            cluster = _get_cluster(name, clusters)
        else:
            choices = list(map(lambda _name: _name['CacheClusterId'], clusters['CacheClusters']))
            name = Prompt.ask("Choose a cluster", choices=choices, default=choices[0])
            cluster = _get_cluster(name, clusters)
        if not cluster:
            self.logger.error(f"An ElastiCache cluster with the name '{name}' is not available, please check the name")
            raise

        cluster = cluster[0]
        return cluster

    def start(self):
        cluster = self.get_cluster(self.pre_defined_name)

        remote_host: str = cluster['CacheNodes'][0]['Endpoint']['Address']
        remote_port: int = cluster['CacheNodes'][0]['Endpoint']['Port']

        table = self.get_table("AWS OpenSearch")
        table.add_row("Cluster ARN", f"{cluster['ARN']}")
        table.add_row("Cluster ID", f"{cluster['CacheClusterId']}")
        table.add_row("Cluster Node Type", f"{cluster['CacheNodeType']}")
        table.add_row("Cluster Engine", f"{cluster['Engine']}")
        table.add_row("Cluster Engine Version", f"{cluster['EngineVersion']}")

        table.add_row("Cluster Host", f"{remote_host}")
        table.add_row("Cluster Port", f"{remote_port}")
        table.add_row("", "")
        table.add_row("Examples", "")
        table.add_row("Client", f"redis-cli -h {self.local_bind_host} -p {self.local_bind_port}")

        self._start(remote_host=remote_host, remote_port=remote_port)
