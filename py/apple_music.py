from . import secrets
from .service import *
from .helpers.paginator import Paginator
from .user_auth_handler import (
    UserAuthHandler,
    UserAuthHTTPRequestHandlerBase,
)
from datetime import datetime, timedelta
import json
import jwt
import re
import requests as r


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
    music_user_token: str

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

        has_music_user_token = True
        try:
            self.music_user_token = apple_secrets["music_user_token"]
        except:
            has_music_user_token = False

        if has_music_user_token:
            res = r.get(
                self.api_url_base() + "/me/library/playlists",
                headers=self.auth_headers(),
            )
            has_music_user_token = res.ok

        if not has_music_user_token:
            handler = UserAuthHandler(
                "http://localhost:8005", AppleMusicUserAuthHTTPRequestHandlerBase
            )
            self.set_music_user_token(handler.get_auth_params()["music-user-token"])

    def set_music_user_token(self, token):
        self.music_user_token = token
        secrets_json = secrets.get()
        secrets_json["apple"]["music_user_token"] = self.music_user_token
        secrets.set(secrets_json)

    def get_tracks(self):
        def get_tracks_page(offset):
            api_url = self.api_url_base() + "/me/library/songs"
            params = {
                "offset": offset,
                "include": "catalog",
                "extend": ["isrc", "name"],
            }
            res = r.get(api_url, headers=self.auth_headers(), params=params)

            new_offset = self.offset_from_response(res.json())

            offset = new_offset if new_offset != offset else -1

            return (res.json()["data"], offset)

        def get_track(track_json):
            data = track_json["relationships"]["catalog"]["data"]
            if len(data) == 0:
                raise LocalLibraryContentError("Song is not in Apple Music's Catalog")
            attrs = data[0]["attributes"]
            return Song(attrs["isrc"], attrs["name"])

        tracks = Paginator(get_tracks_page, get_track)
        for track in tracks:
            self.add_song(track)

        return tracks

    def get_albums(self):
        pass

    # @todo unimplemented
    def get_playlists(self):
        pass

    def auth_headers(self):
        return {
            "Authorization": f"Bearer {self.auth_jwt}",
            "Music-User-Token": self.music_user_token,
        }

    @staticmethod
    def api_url_base():
        return "https://api.music.apple.com/v1"

    @staticmethod
    def offset_from_response(res):
        path = res["next"]
        find = re.findall("(offset)=(\\d+)", path)
        assert len(find) == 1
        return int(find[0][1])
