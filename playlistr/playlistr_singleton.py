import multiprocessing
from .spotify import Spotify


class Playlistr:
    session: dict = None
    spotify: Spotify

    def __new__(cls):
        print("NEW PLAYLISTR")
        if cls.session != None:
            raise RuntimeError("Don't make more than one Playlistr object.")

        cls.session = {}
        cls.spotify = Spotify()


playlistr = Playlistr()
print("NEW PLAYLISTR MADE")
