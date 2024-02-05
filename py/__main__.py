from .playlistr_singleton import Playlistr
from .spotify import Spotify
from .apple_music import AppleMusic
from time import sleep

if __name__ == "__main__":
    apple_music = AppleMusic()

    # spotify = Spotify()
    # spotify.get_user_content()
