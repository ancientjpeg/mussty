import json


class ServiceBase:
    secrets: dict

    def __init__(self) -> None:
        self.secrets = self.get_secrets()

    def get_secrets():
        with open("secrets.json") as f:
            secrets = json.load(f)
        return secrets
