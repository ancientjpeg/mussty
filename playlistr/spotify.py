from . import service_base
import requests as r
from requests_oauthlib import OAuth2Session


class Spotify(service_base.ServiceBase):
    ready: bool = False
    client_id: str
    client_secret: str
    auth_code: str
    session: OAuth2Session

    def __init__(self) -> None:
        super().__init__()
        self.client_id = self.secrets["spotify"]["client_id"]
        self.client_secret = self.secrets["spotify"]["client_secret"]

    @staticmethod
    def spotify_auth_url_base():
        return "https://accounts.spotify.com/authorize"

    @staticmethod
    def spotify_api_url_base():
        return "https://accounts.spotify.com/api"

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
