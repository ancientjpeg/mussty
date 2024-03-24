from . import secrets
from .service import *
from .helpers.paginator import Paginator
from .user_auth_handler import (
    UserAuthHandler,
    UserAuthHTTPRequestHandlerBase,
)
from datetime import datetime, timedelta
import jwt
import requests as r


class AppleMusicUserAuthHTTPRequestHandlerBase(UserAuthHTTPRequestHandlerBase):
    @UserAuthHTTPRequestHandlerBase.do_GET_decorator
    def do_GET(self):
        path = self.path

        # just the path, no query string
        # TODO probably a more canonical way to do this
        path = path.split("?")[0]

        match path:
            case "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                with open("../html/index.html") as f:
                    token = self.get_auth_server().apple_music_dev_token  # type:ignore
                    file_contents = f.read()
                    file_contents = file_contents.replace(
                        "$DEVELOPER_TOKEN_PLACEHOLDER", token
                    )
                    self.wfile.write(file_contents.encode())

            case "/authorize":
                self.return_successfully()
            case _:
                self.send_response(400)
                self.get_auth_server().event.set()
                raise RuntimeError(f"Unexpected callback path used: {path}")


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

            # TODO this is messy and hacky, please refactor.
            handler.auth_server.apple_music_dev_token = self.auth_jwt  # type:ignore

            self.set_music_user_token(handler.get_auth_params()["music-user-token"])

    def set_music_user_token(self, token):
        self.music_user_token = token
        secrets_json = secrets.get()
        secrets_json["apple"]["music_user_token"] = self.music_user_token
        secrets.set(secrets_json)

    def get_tracks(self):
        api_url = self.api_url_base() + "/me/library/songs"
        res = r.get(api_url, headers=self.auth_headers(), params={"limit": 1})
        total = res.json()["meta"]["total"]
        total = 100  # TEST!
        limit = 100

        async def get_tracks_page(offset: int, paginator: Paginator):
            params = {
                "offset": offset,
                "limit": 100,
                "include": ["albums,catalog"],
                "extend[songs]": ["isrc,name"],
                "include[library-albums]": ["catalog"],
                "extend[albums]": ["upc"],
            }

            tracks = []
            async with paginator.session.get(
                api_url, headers=self.auth_headers(), params=params
            ) as res:
                data = None
                try:
                    body = await res.json()
                    data = body["data"]
                except Exception as e:
                    if res.status == 429:
                        raise RuntimeError("Encountered rate limits.")
                    raise e

                for track_json in data:
                    data = track_json["relationships"]["catalog"]["data"]
                    album_data = track_json["relationships"]["albums"]["data"][0]
                    catalog_album_data = album_data["relationships"]["catalog"]["data"]

                    if len(data) == 0 or len(catalog_album_data) == 0:
                        # @todo handle out-of-catalog records
                        # print("Song is not in Apple Music's Catalog")
                        continue
                    attrs = data[0]["attributes"]
                    album_attrs = catalog_album_data[0]["attributes"]

                    tracks.append(
                        Song(attrs["isrc"], attrs["name"], album_attrs["upc"])
                    )

            return tracks

        tracks = Paginator(get_tracks_page, limit, total)
        for track in tracks:
            self.add_song(track)

    def get_albums(self):
        api_url = self.api_url_base() + "/me/library/albums"
        res = r.get(api_url, headers=self.auth_headers(), params={"limit": 1})
        total = res.json()["meta"]["total"]
        limit = 100

        async def get_albums_page(offset: int, paginator: Paginator):
            params = {
                "offset": offset,
                "limit": 100,
                "include": ["catalog"],
                "extend[albums]": ["upc"],
            }

            albums = []
            async with paginator.session.get(
                api_url, headers=self.auth_headers(), params=params
            ) as res:
                data = None
                try:
                    body = await res.json()
                    data = body["data"]
                except Exception as e:
                    if res.status == 429:
                        raise RuntimeError("Encountered rate limits.")
                    raise e

                for track_json in data:
                    data = track_json["relationships"]["catalog"]["data"]

                    if len(data) == 0:
                        # @todo handle out-of-catalog records
                        # print("Song is not in Apple Music's Catalog")
                        continue
                    attrs = data[0]["attributes"]

                    albums.append(Album(attrs["upc"], attrs["name"]))

            return albums

        albums = Paginator(get_albums_page, limit, total)
        for album in albums:
            self.add_album(album)

    def get_playlists(self):
        api_url = self.api_url_base() + "/me/library/playlists"
        res = r.get(api_url, headers=self.auth_headers(), params={"limit": 1})
        total = res.json()["meta"]["total"]
        limit = 100

        async def get_playlists_page(offset: int, paginator: Paginator):
            params = {
                "offset": offset,
                "limit": limit,
            }

            playlists: list[Playlist] = []
            async with paginator.session.get(
                api_url, headers=self.auth_headers(), params=params
            ) as res:
                if res.status == 429:
                    raise RuntimeError("Encountered rate limits.")

                body = await res.json()
                data = body["data"]

                for playlist_json in data:
                    attrs = playlist_json["attributes"]

                    id = playlist_json["id"]
                    name = attrs["name"]

                    # if attrs['hasCatalog'] == True:
                    #     print(f'Skipped library playlist {name}')
                    #     continue
                    # else:
                    #     print(f'Got library playlist {name}')

                    playlists.append(Playlist(id, name, []))

            return playlists

        def get_songs_for_playlist_by_id(playlist: Playlist):
            async def get_songs_for_playlist(offset: int, paginator: Paginator):
                tracks_api_url = (
                    self.api_url_base() + f"/me/library/playlists/{playlist.id}/tracks"
                )

                tracks_params = {
                    "offset": offset,
                    "limit": limit,
                    "include[library-songs]": "catalog",
                    "extend[songs]": "isrc,name",
                }

                playlist_songs = []

                async with paginator.session.get(
                    tracks_api_url,
                    headers=self.auth_headers(),
                    params=tracks_params,
                ) as res:
                    body = await res.json()

                    try:
                        for track in body["data"]:
                            if track["type"] == "library-music-videos":
                                continue

                            data = track["relationships"]["catalog"]["data"]

                            if len(data) == 0:
                                continue

                            attrs = data[0]["attributes"]

                            playlist_songs.append(
                                Song(attrs["isrc"], attrs["name"], "")
                            )
                    except KeyError:
                        print(body["errors"])
                        print(f"Got error response for playlist {playlist.title}")

                return playlist_songs

            return get_songs_for_playlist

        all_playlists_pag = Paginator(get_playlists_page, limit, total)
        all_playlists = all_playlists_pag.records
        for playlist in all_playlists:
            playlist_tracks_api_url = (
                self.api_url_base() + f"/me/library/playlists/{playlist.id}/tracks"
            )

            res = r.get(
                playlist_tracks_api_url,
                headers=self.auth_headers(),
                params={"limit": 1},
            )
            total = res.json()["meta"]["total"]
            limit = 100

            playlist_songs_pag = Paginator(
                get_songs_for_playlist_by_id(playlist), limit=limit, total=total
            )
            playlist.songs = playlist_songs_pag.records

        for playlist in all_playlists:
            self.add_playlist(playlist)

    def auth_headers(self):
        return {
            "Authorization": f"Bearer {self.auth_jwt}",
            "Music-User-Token": self.music_user_token,
        }

    @staticmethod
    def get_json_tagname():
        return "apple_music"

    @staticmethod
    def api_url_base():
        return "https://api.music.apple.com/v1"
