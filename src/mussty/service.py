from dataclasses import dataclass


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
    ean: str = ""
    upc: str = ""


@dataclass
class Album:
    upc: str
    title: str
    ean: str = ""


@dataclass
class Playlist:
    id: str
    title: str
    songs: list[Song]


class Service:
    # id -> record dicts
    songs: dict[str, Song]
    albums: dict[str, Album]
    playlists: dict[str, Playlist]
    json_tagname: str

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
