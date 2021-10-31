
from boto3.session import Session


class Aws:  # TODO provide also possibility to use AWS Credentials instead of just a profile

    profile_name: str
    session: Session

    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        self.session = Session(profile_name=self.profile_name)
