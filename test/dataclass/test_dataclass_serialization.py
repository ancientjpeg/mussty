import dataclasses
from playlistr.service import *
from playlistr.resolver import *


def test_song_serialization():
    song = Song("test_isrc", "test_title", "test_album_upc")
    song_data = song.to_dict()

    assert song_data["isrc"] == "test_isrc"

    song_deserialized = Song.from_json(song_data)

    assert song_deserialized.album_upc == "test_album_upc"
    assert song_deserialized.album_upc == song_data["album_upc"]


def test_album_serialization():
    album = Album("test_upc", "test_title")
    album_data = album.to_dict()

    assert album_data["upc"] == "test_upc"

    album_deserialized = Album.from_json(album_data)

    assert album_deserialized.upc == "test_upc"
    assert album_deserialized.upc == album_data["upc"]


def test_playlist_serialization():
    songs = [
        Song("test_isrc0", "test_title0", "test_album_upc0"),
        Song("test_isrc1", "test_title1", "test_album_upc1"),
        Song("test_isrc2", "test_title2", "test_album_upc2"),
    ]

    playlist = Playlist("test_id", "test_title", songs)

    playlist_data = playlist.to_dict()

    assert playlist_data["title"] == "test_title"

    playlist_deserialized = Playlist.from_json(playlist_data)

    assert playlist_deserialized.title == "test_title"
    assert playlist_deserialized.title == playlist_data["title"]

    for i in range(len(songs)):
        assert playlist_deserialized.songs[i] == playlist.songs[i]
