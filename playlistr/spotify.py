from . import secrets
import requests as r
from requests_oauthlib import OAuth2Session


class Spotify:
    def __init__(self) -> None:
        super().__init__()
        self.client_id: str = secrets.get()["spotify"]["client_id"]
        self.client_secret: str = secrets.get()["spotify"]["client_secret"]
        self.scope = ["user-read-email"]
        self.ready: bool = False
        self.auth_code: str
        # self.redirect_uri
        # self.session: OAuth2Session = OAuth2Session(self.client_id, scope=self.scope, redirect_uri=

    @staticmethod
    def spotify_auth_url_base():
        return "https://accounts.spotify.com/authorize"

    @staticmethod
    def spotify_api_url_base():
        return "https://accounts.spotify.com/api"

    @staticmethod
    def spotify_token_url_base():
        return Spotify.spotify_api_url_base() + "/token"

    def spotify_auth_url(self):
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": "http://localhost:8005/spotify-callback",
        }
        headers = {}
        req = r.Request(
            "GET",
            self.spotify_auth_url_base(),
            params=params,
            headers=headers,
        )

        return req.prepare().url
