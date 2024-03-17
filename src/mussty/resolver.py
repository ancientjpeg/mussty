from .service import Album, Playlist, Service, Song


class Resolver:
    service_a: Service
    service_b: Service

    target_songs: list[Song]
    target_albums: list[Album]
    target_playlists: list[Playlist]

    def __init__(self, types: tuple[type, type], config: dict = {}) -> None:
        if not issubclass(types[0], Service) or not issubclass(types[1], Service):
            raise TypeError("Services must be derived from mussty.service")

        print(
            f"Converting content from service {types[0].__name__} to service {types[1].__name__}"
        )

        service_a = types[0]()
        service_b = types[1]()

        service_a.get_user_content()
        service_b.get_user_content()

    def resolve_songs(self):
        target_song_ids = set(self.service_a.songs.keys()) - set(
            self.service_b.songs.keys()
        )
        target_songs = [
            song for id, song in self.service_a.songs.items() if id in target_song_ids
        ]

        for song in target_songs:
            print(song.title)
