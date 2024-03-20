from dataclasses import dataclass


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
    def from_dict(song_json: dict) -> "Song":
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
    def from_dict(album_json: dict) -> "Album":
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
    def from_dict(playlist_json: dict) -> "Playlist":
        songs_json = playlist_json["songs"]
        songs = [Song.from_dict(song) for song in songs_json]

        return Playlist(
            playlist_json["id"],
            playlist_json["title"],
            songs,
        )
