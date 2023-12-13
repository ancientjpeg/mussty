from . import secrets
import requests as r
from requests_oauthlib import OAuth2Session
import base64


class Spotify:
    def __init__(self) -> None:
        super().__init__()
        self.client_id: str = secrets.get()["spotify"]["client_id"]
        self.client_secret: str = secrets.get()["spotify"]["client_secret"]
        self.scope = [
            "user-library-read",
            "user-library-modify",
            "playlist-read-private",
            "playlist-read-collaborative",
            "playlist-modify-private",
            "playlist-modify-public ",
        ]
        self.ready: bool = False
        self.auth_code: str = ""
        self.access_token: str = ""
        self.refresh_token: str = ""

        # self.redirect_uri
        # self.session: OAuth2Session = OAuth2Session(self.client_id, scope=self.scope, redirect_uri=

    @staticmethod
    def spotify_api_url_base():
        return "https://api.spotify.com/v1"

    @staticmethod
    def redirect_uri():
        return "http://localhost:8005/spotify-callback"

    @staticmethod
    def spotify_auth_url_base():
        return "https://accounts.spotify.com/authorize"

    @staticmethod
    def spotify_accounts_api_url_base():
        return "https://accounts.spotify.com/api"

    @staticmethod
    def spotify_token_url_base():
        return Spotify.spotify_accounts_api_url_base() + "/token"

    def spotify_auth_url(self):
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri(),
        }
        headers = {}
        req = r.Request(
            "GET",
            self.spotify_auth_url_base(),
            params=params,
            headers=headers,
        )

        return req.prepare().url

    def get_token(self):
        params = {
            "grant_type": "authorization_code",
            "code": self.auth_code,
            "redirect_uri": self.redirect_uri(),
        }
        auth = f"{self.client_id}:{self.client_secret}"
        print(auth)
        auth = base64.b64encode(auth.encode("ascii")).decode("ascii")
        print(auth)
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        res = r.post(self.spotify_token_url_base(), params=params, headers=headers)
        res = res.json()

        self.access_token = res["access_token"]
        self.refresh_token = res["refresh_token"]
        print(f"spotify access token: {self.access_token}")

    def get_tracks(self):
        url = self.spotify_api_url_base() + "/me/tracks"
        res = r.Request(url=url, headers=self.auth_headers())
        res = res.json()

    def auth_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}
