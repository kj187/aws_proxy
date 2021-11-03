
from aws_proxy.aws import Aws as AwsClient


class Bastion:

    host: str
    port: int
    label_selector: str
    username: str
    identity_file: str
    config_file: str
    aws_client: AwsClient

    def __init__(self, host: str, port: int, label_selector: str, username: str, identity_file: str, config_file: str, aws_client: AwsClient):
        self.host = host
        self.port = port
        self.label_selector = label_selector
        self.username = username
        self.identity_file = identity_file
        self.config_file = config_file
        self.aws_client = aws_client

        if not self.host:
            self.host = self.find_bastion_host_by_label_selector()

    def find_bastion_host_by_label_selector(self) -> str:
        ec2_client = self.aws_client.session.client('ec2')
        name, value = self.label_selector.split("=")
        bastion = ec2_client.describe_instances(Filters=[
            {
                'Name': name,
                'Values': [value]
            },
        ])

        if not bastion['Reservations']:
            raise Exception("Bastion host not defined, bastion label selector does not find any bastion host")

        for instance in bastion['Reservations'][0]['Instances']:
            if instance['State']['Name'] == "running":
                return instance['PublicIpAddress']

        raise Exception("No bastion instance are in running state")
