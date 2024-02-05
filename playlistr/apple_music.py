from .service import Service
from . import secrets
import jwt
from datetime import datetime, timedelta
import requests as r


class AppleMusic(Service):

    private_key: str
    auth_jwt: str

    def __init__(self):
        super().__init__()

        apple_secrets = secrets.get()["apple"]

        creation_time = datetime.today()
        expiry_time = creation_time + timedelta(weeks=1)

        headers = {"alg": "ES256", "kid": apple_secrets["private_key_id"]}
        payload = {
            "iss": apple_secrets["team_id"],
            "iat": int(creation_time.timestamp()),
            "exp": int(expiry_time.timestamp()),
        }

        encoded_jwt = jwt.encode(
            headers=headers,
            payload=payload,
            key=apple_secrets["private_key"],
            algorithm="ES256",
        )

        self.auth_jwt = encoded_jwt
        print(self.auth_jwt)

        # res = r.get(
        #     "https://api.music.apple.com/v1/catalog/us/albums/1616728060",
        #     headers={"Authorization": f"Bearer {self.auth_jwt}"},
        # )
        # print(res.json())
