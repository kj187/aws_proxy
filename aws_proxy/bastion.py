
class Bastion:

    host: str
    port: int
    username: str
    identity_file: str
    config_file: str

    def __init__(self, host: str, port: int, username: str, identity_file: str, config_file: str):
        self.host = host
        self.port = port
        self.username = username
        self.identity_file = identity_file
        self.config_file = config_file
