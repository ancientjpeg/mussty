from playlistr.service import Service
from playlistr.spotify import Spotify
from playlistr.apple_music import AppleMusic


def test_typing():
    assert issubclass(Spotify, Service)
    assert issubclass(AppleMusic, Service)
