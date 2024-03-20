from mussty.service import Service
from mussty.define.types import *
from pathlib import Path
from uuid import uuid4


def gen_song():
    return Song(str(uuid4()), str(uuid4()), str(uuid4()))


def gen_album():
    return Album(str(uuid4()), str(uuid4()))


def gen_playlist():
    songs = [gen_song() for _ in range(20)]
    return Playlist(str(uuid4()), str(uuid4()), songs)


class CachingService(Service):
    cachefile = Path("test_cache.json")
    pass


def test_service_caching():
    output = CachingService()
    input = CachingService()

    for _ in range(20):
        output.add_song(gen_song())
        output.add_album(gen_album())
        output.add_playlist(gen_playlist())

    output.cache_self()

    input.uncache_self()

    CachingService.cachefile.unlink()

    assert input.songs == output.songs
    assert input.albums == output.albums
    assert input.playlists == output.playlists
