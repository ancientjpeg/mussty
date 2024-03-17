import json


class Secrets:
    secrets: dict = None
    secrets_file = "secrets.json"

    @classmethod
    def get(cls):
        if cls.secrets == None:
            with open(cls.secrets_file) as f:
                cls.secrets = json.load(f)
        return cls.secrets

    @classmethod
    def set(cls, secrets_output):
        with open(cls.secrets_file, "w") as f:
            json.dump(secrets_output, f)


def get():
    return Secrets.get()


def set(secrets_output):
    Secrets.set(secrets_output)
