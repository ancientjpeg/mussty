from dataclasses import dataclass
from pathlib import Path
import json


class LocalLibraryContentError(Exception):
    """Raise this error if the record being parsed is local (i.e., user) content."""


@dataclass
class Artist:
    id: str
    name: str


@dataclass
class Song:
    isrc: str
    title: str
    album_upc: str

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_json(song_json: dict) -> "Song":
        return Song(
            song_json["isrc"],
            song_json["title"],
            song_json["album_upc"],
        )


@dataclass
class Album:
    upc: str
    title: str

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_json(album_json: dict) -> "Album":
        return Album(
            album_json["upc"],
            album_json["title"],
        )


@dataclass
class Playlist:
    id: str
    title: str
    songs: list[Song]

    def to_dict(self):
        data = self.__dict__.copy()
        data["songs"] = [song.to_dict() for song in data["songs"]]
        return data

    @staticmethod
    def from_json(playlist_json: dict) -> "Playlist":
        songs_json = playlist_json["songs"]
        songs = [Song.from_json(song) for song in songs_json]

        return Playlist(
            playlist_json["id"],
            playlist_json["title"],
            songs,
        )


class Service:
    # id -> record dicts
    songs: dict[str, Song]
    albums: dict[str, Album]
    playlists: dict[str, Playlist]
    json_tagname: str
    cachefile: Path = Path("./cache.json")

    def __init__(self):
        self.songs = {}
        self.playlists = {}
        self.albums = {}

        try:
            self.json_tagname = self.get_json_tagname()
        except AttributeError:
            self.json_tagname = self.__class__.__name__.lower()

    def get_user_content(self):
        # @todo just calling these and hoping they're implemented is horrifically stupid, look into @abstractmethod
        self.get_tracks()
        self.get_albums()
        self.get_playlists()
        self.cache_self()

    def add_album(self, album: Album):
        self.add_generic(album, self.albums)

    def add_song(self, song: Song):
        self.add_generic(song, self.songs)

    def add_playlist(self, playlist: Playlist):
        self.add_generic(playlist, self.playlists)

    def add_generic(self, record, list):
        try:
            id = record.isrc
        except:
            id = record.id

        if id in list:
            # print(f"duplicate records: {record.title} --- {list[record.isrc].title}")
            return

        list[id] = record

    def uncache_self(self):
        with open(self.cachefile) as f:
            data = json.load(f)

    def cache_self(self):
        cached_self = {}
        cached_self["songs"] = self.songs
        cached_self["albums"] = self.albums

        with open(self.cachefile, "r+") as f:
            data = json.load(f)

            f.seek(0)
            f.truncate(0)

            json.dump(data, f)
