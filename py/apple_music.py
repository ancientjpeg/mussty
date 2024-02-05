from .service import Service
from . import secrets
import jwt
from datetime import datetime, timedelta
from .user_auth_handler import (
    UserAuthHandler,
    UserAuthHTTPRequestHandlerBase,
)
import requests as r
import webbrowser


class AppleMusicUserAuthHTTPRequestHandlerBase(UserAuthHTTPRequestHandlerBase):

    @UserAuthHTTPRequestHandlerBase.do_GET_decorator
    def do_GET(self):
        path = self.server.parsed_path.path
        match path:
            case "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                with open("html/index.html") as f:
                    self.wfile.write(f.read().encode())

            case "/authorize":
                self.return_successfully()
            case _:
                self.send_response(400)
                self.server.event.set()
                raise RuntimeError("Unexpected callback path used.")


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

        handler = UserAuthHandler(
            "http://localhost:8005", AppleMusicUserAuthHTTPRequestHandlerBase
        )
        token = handler.get_auth_params()["music-user-token"]
        print(token)

        # res = r.get(
        #     "https://api.music.apple.com/v1/catalog/us/albums/1616728060",
        #     headers={"Authorization": f"Bearer {self.auth_jwt}"},
        # )
        # print(res.json())
