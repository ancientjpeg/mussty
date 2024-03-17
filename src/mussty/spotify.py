from . import secrets
from .service import Service, Album, Song, Playlist
from .user_auth_handler import (
    UserAuthHandler,
    UserAuthHTTPRequestHandlerBase,
)
import base64
import requests as r
from .helpers.paginator import Paginator


class SpotifyUserAuthHTTPRequestHandler(UserAuthHTTPRequestHandlerBase):
    @UserAuthHTTPRequestHandlerBase.do_GET_decorator
    def do_GET(self):
        self.return_successfully()


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
        self.access_token: str = ""
        self.refresh_token: str = ""
        self.user_id: str = ""

        has_tokens = True
        try:
            self.access_token = secrets.get()["spotify"]["access_token"]
            self.refresh_token = secrets.get()["spotify"]["refresh_token"]
        except KeyError:
            print("Missing access or refresh tokens in secrets.json")
            has_tokens = False

        # # if we can get the user id successfully with our cached tokens, we're set.
        if has_tokens and self.get_user_id():
            return

        if has_tokens:
            self.refresh_access_token()
        else:
            self.get_token()

        got_id = self.get_user_id()
        assert got_id

    def get_user_id(self):
        res = r.get(self.api_url_base() + "/me", headers=self.auth_headers())
        if res.status_code != 200:
            return False

        self.user_id = res.json()["id"]

        return True

    def update_tokens(self, access_token: str, refresh_token: str):
        self.access_token = access_token
        self.refresh_token = refresh_token
        secrets_json = secrets.get()
        secrets_json["spotify"]["access_token"] = self.access_token
        secrets_json["spotify"]["refresh_token"] = self.refresh_token
        secrets.set(secrets_json)

    def get_token(self):
        handler = UserAuthHandler(self.auth_url(), SpotifyUserAuthHTTPRequestHandler)
        auth_code = handler.get_auth_params()["code"]

        params = {
            "grant_type": "authorization_code",
            "code": auth_code,
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

        self.update_tokens(res["access_token"], res["refresh_token"])

    def refresh_access_token(self):
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        auth = f"{self.client_id}:{self.client_secret}"
        auth = base64.b64encode(auth.encode("ascii")).decode("ascii")
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        res = r.post(self.token_url_base(), params=params, headers=headers)
        res = res.json()

        self.update_tokens(res["access_token"], self.refresh_token)

    def get_tracks(self):
        api_url = self.api_url_base() + "/me/tracks"

        res = r.get(api_url, headers=self.auth_headers())
        limit = 50
        total = res.json()["total"]

        async def get_tracks_page(offset: int, paginator: Paginator):
            params = {
                "offset": offset,
                "limit": limit,
            }

            tracks = []

            async with paginator.session.get(
                api_url, headers=self.auth_headers(), params=params
            ) as res:
                try:
                    body = await res.json()
                except Exception as e:
                    if res.status_code == 429:
                        raise RuntimeError("Encountered rate limits. Aborting")
                    raise e

                for item in body["items"]:
                    track = item["track"]
                    isrc = track["external_ids"]["isrc"]
                    title = track["name"]

                    tracks.append(Song(isrc, title))

            return tracks

        tracks = Paginator(get_tracks_page, limit, total)

        for track in tracks:
            self.add_song(track)

    def get_albums(self):
        api_url = self.api_url_base() + "/me/albums"

        res = r.get(api_url, headers=self.auth_headers())
        limit = 50
        total = res.json()["total"]

        async def get_albums_page(offset: int, paginator: Paginator):
            albums = []
            params = {"limit": limit, "offset": offset}
            async with paginator.session.get(
                api_url, headers=self.auth_headers(), params=params
            ) as res:
                body = await res.json()
                for item in body["items"]:
                    album = item["album"]

                    upc = album["external_ids"]["upc"]

                    title = album["name"]

                    albums.append(Album(upc, title))

                return albums

        albums = Paginator(get_albums_page, limit, total)

        for album in albums:
            self.add_album(album)

    def get_playlists(self):
        api_url = self.api_url_base() + "/me/playlists"

        res = r.get(api_url, headers=self.auth_headers())
        total = res.json()["total"]

        limit = 50

        async def get_playlist_page(offset: int, paginator: Paginator):
            playlists = []
            params = {"limit": limit, "offset": offset}
            async with paginator.session.get(
                api_url, headers=self.auth_headers(), params=params
            ) as res:
                body = await res.json()
                for playlist in body["items"]:
                    if playlist["owner"]["id"] != self.user_id:
                        continue

                    id = playlist["id"]
                    title = playlist["name"]

                    playlists.append(Playlist(id, title, []))

                return playlists

        playlists = Paginator(get_playlist_page, limit, total)
        print(playlists.records)

        for playlist in playlists:
            self.add_playlist(playlist)

    def auth_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

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
