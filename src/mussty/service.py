from pathlib import Path
from .define.types import *
import json


class LocalLibraryContentError(Exception):
    """Raise this error if the record being parsed is local (i.e., user) content."""


class Service:
    # id -> record dicts
    songs: dict[str, Song]
    albums: dict[str, Album]
    playlists: dict[str, Playlist]
    json_tagname: str
    cachefile: Path = Path("../cache.json")
    CACHE: bool = True

    def __init__(self):
        self.songs = {}
        self.playlists = {}
        self.albums = {}

        try:
            self.json_tagname = self.get_json_tagname()
        except AttributeError:
            self.json_tagname = self.__class__.__name__.lower()

    def get_user_content(self):
        needs_content_refresh = False
        if self.CACHE:
            needs_content_refresh = not self.uncache_self()

        # @todo just calling these and hoping they're implemented is horrifically stupid, look into @abstractmethod
        if needs_content_refresh:
            self.get_tracks()
            self.get_albums()
            self.get_playlists()

        if self.CACHE and needs_content_refresh:
            self.cache_self()

    def add_album(self, album: Album):
        self.albums[album.upc] = album

    def add_song(self, song: Song):
        self.songs[song.isrc] = song

    def add_playlist(self, playlist: Playlist):
        self.playlists[playlist.id] = playlist

    def uncache_self(self):
        if not self.cachefile.exists():
            print(f"No cache exists for service of type {self.__class__.__name__}")
            return False

        with open(self.cachefile) as f:
            data = json.load(f)
            data = data[self.json_tagname]

            try:
                self.songs = {
                    song["isrc"]: Song.from_dict(song) for song in data["songs"]
                }

                self.albums = {
                    album["upc"]: Album.from_dict(album) for album in data["albums"]
                }

                self.playlists = {
                    playlist["id"]: Playlist.from_dict(playlist)
                    for playlist in data["playlists"]
                }
            except KeyError:
                print(
                    f"Failed to un-cache service instance of type {self.__class__.__name__}"
                )
                return False

        print(
            f"Successfully retrieved cache for service instance of type {self.__class__.__name__}"
        )
        return True

    def cache_self(self):
        cached_self = {}
        cached_self["songs"] = [song.to_dict() for _, song in self.songs.items()]
        cached_self["albums"] = [album.to_dict() for _, album in self.albums.items()]
        cached_self["playlists"] = [
            playlist.to_dict() for _, playlist in self.playlists.items()
        ]

        if not self.cachefile.exists():
            with self.cachefile.open("w+") as f:
                pass

        with self.cachefile.open("r+") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

            data[self.json_tagname] = cached_self

            f.seek(0)
            f.truncate(0)

            json.dump(data, f, indent=2)
