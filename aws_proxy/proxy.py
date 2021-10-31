
from logging import Logger
from rich.console import Console
from rich.table import Table, box
from sshtunnel import SSHTunnelForwarder
from aws_proxy.bastion import Bastion


class SshProxy:

    logger: Logger
    bastion: Bastion
    local_bind_host: str
    local_bind_port: int

    __console: Console
    __table: Table

    __server: SSHTunnelForwarder = None

    def __init__(self, logger: Logger, local_bind_port: int, bastion: Bastion):
        self.__console = Console()
        self.logger = logger
        self.bastion = bastion
        self.local_bind_host = "127.0.0.1"
        self.local_bind_port = local_bind_port

    def __del__(self):
        if isinstance(self.__server, SSHTunnelForwarder):
            self.__server.stop()

    def get_table(self, title: str) -> Table:
        self.__table = Table(box=box.MINIMAL, row_styles=['white on black', 'white'])
        self.__table.add_column("Proxy to ===>", style="", min_width=15, no_wrap=True)
        self.__table.add_column(title, no_wrap=False, style="")
        return self.__table

    def _start(self, remote_host: str, remote_port: int):

        self.__server = SSHTunnelForwarder(
            ssh_config_file=(self.bastion.config_file if self.bastion.config_file != "" else None),
            ssh_pkey=(self.bastion.identity_file if self.bastion.identity_file != "" else None),
            ssh_username=self.bastion.username,
            ssh_address_or_host=(self.bastion.host, self.bastion.port),
            remote_bind_address=(remote_host, remote_port),
            local_bind_address=(self.local_bind_host, self.local_bind_port),
            logger=self.logger,
        )
        self.__server.start()

        self.__table.add_row("", "", style="on blue")
        self.__table.add_row("Local proxy", f"{self.__server.local_bind_host}:{self.__server.local_bind_port}")
        self.__table.add_row("proxied to", f"{remote_host}:{remote_port}")
        self.__table.add_row("over bastion", f"{self.bastion.host}:{self.bastion.port} ({self.bastion.username})")
        self.__console.print(self.__table)

        while True:
            pass
