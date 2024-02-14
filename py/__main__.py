from .spotify import Spotify
from .apple_music import AppleMusic
from time import sleep

if __name__ == "__main__":
    apple_music = AppleMusic()
    apple_music.get_user_content()

    spotify = Spotify()
    spotify.get_user_content()
