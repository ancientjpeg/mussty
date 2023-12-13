import json


class Secrets:
    secrets: dict = None

    @classmethod
    def get(cls):
        if cls.secrets == None:
            with open("secrets.json") as f:
                cls.secrets = json.load(f)
        return cls.secrets


def get():
    return Secrets.get()
