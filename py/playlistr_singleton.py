from .spotify import Spotify


class Playlistr:
    exists: bool = False
    spotify: Spotify

    def __new__(cls):
        if cls.exists:
            raise RuntimeError("Don't make more than one Playlistr object.")

        cls.exists = True

        cls.spotify = Spotify()

        instance = super().__new__(cls)
        return instance
