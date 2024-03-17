import dataclasses
from playlistr.service import *
from playlistr.resolver import *


def test_song_serialization():
    song = Song("test_isrc", "test_title", "test_album_upc")
    song_data = song.__dict__

    assert song_data["isrc"] == "test_isrc"


def test_album_serialization():
    pass


def test_playlist_serialization():
    pass
