from . import secrets
import requests as r
import base64
from .auth_server import PlaylistrAuthCallbackHandler
from .service import Service, Artist, Song, Playlist


class Spotify(Service):
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

        try:
            self.access_token = secrets.get()["spotify"]["access_token"]
        except KeyError:
            print("No pre-existing access token available for Spotify.")

        try:
            self.refresh_token = secrets.get()["spotify"]["refresh_token"]
        except KeyError:
            print("No pre-existing refresh token available for Spotify.")

        handler = PlaylistrAuthCallbackHandler(self.auth_url())
        self.auth_code = handler.get_auth_params()["code"]
        self.get_token()

    def auth_url(self):
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri(),
            "scope": " ".join(self.scope),
        }
        headers = {}
        req = r.Request(
            "GET",
            self.auth_url_base(),
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
        auth = base64.b64encode(auth.encode("ascii")).decode("ascii")
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        res = r.post(self.token_url_base(), params=params, headers=headers)
        res = res.json()

        self.access_token = res["access_token"]
        self.refresh_token = res["refresh_token"]

    def get_tracks(self):
        api_url = self.api_url_base() + "/me/tracks"

        offset = 0

        def get_tracks_page():
            body = None
            params = {"limit": 50, "offset": offset}
            res = r.get(url=api_url, params=params, headers=self.auth_headers())
            body = res.json()
            for item in body["items"]:

                track = item["track"]
                id = track["id"]
                title = track["name"]
                artist_json = track["artists"][0]
                artist: Artist = Artist(artist_json["id"], artist_json["name"])

                self.add_song(Song(id, title, artist))
            return body["next"]

        while get_tracks_page():
            pass

    def get_user_content(self):
        self.get_tracks()

    def auth_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    @staticmethod
    def api_url_base():
        return "https://api.spotify.com/v1"

    @staticmethod
    def redirect_uri():
        return "http://localhost:8005/spotify-callback"

    @staticmethod
    def auth_url_base():
        return "https://accounts.spotify.com/authorize"

    @staticmethod
    def accounts_api_url_base():
        return "https://accounts.spotify.com/api"

    @staticmethod
    def token_url_base():
        return Spotify.accounts_api_url_base() + "/token"
