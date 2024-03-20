from mussty.service import Service
from mussty.spotify import Spotify
from mussty.apple_music import AppleMusic


def test_typing():
    assert issubclass(Spotify, Service)
    assert issubclass(AppleMusic, Service)
