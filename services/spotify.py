from . import service_base
import requests as r
from requests_oauthlib import OAuth2Session


class SpotifyService(service_base.ServiceBase):
    ready: bool = False
    client_id: str
    client_secret: str
    session: OAuth2Session

    def __init__(self) -> None:
        super().__init__()
        self.client_id = self.secrets["spotify"]["client_id"]
        self.client_secret = self.secrets["spotify"]["client_secret"]

    def spotify_auth_url(self):
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": "http://localhost:8005/spotify",
        }
        headers = {}
        req = r.Request(
            "GET",
            "https://accounts.spotify.com/authorize",
            params=params,
            headers=headers,
        )
        return req.prepare().url
