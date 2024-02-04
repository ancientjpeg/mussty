from dataclasses import dataclass


@dataclass
class Artist:
    id: str
    name: str


@dataclass
class Song:
    id: str
    title: str
    artist: Artist


@dataclass
class Playlist:
    id: str
    url: str
    songs: list[Song]


class Service:
    # id -> record dicts
    songs: dict[str, Song]
    playlists: dict[str, Playlist]

    def __init__(self):
        self.songs = {}
        self.playlists = {}

    def get_user_content(self):
        # @todo this should be considered "pure virtual" - look into @abstractmethod
        assert False

    def add_song(self, song: Song):
        if song.id in self.songs:
            assert song == self.songs[song.id]
            return

        self.songs[song.id] = song

    def add_playlist(self, playlist: Playlist):

        if playlist.id in self.playlists:
            assert playlist == self.playlists[playlist.id]
            return

        self.playlists[playlist.id] = playlist
