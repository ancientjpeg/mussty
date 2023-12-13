from .playlistr_singleton import Playlistr
from time import sleep

if __name__ == "__main__":
    playlistr = Playlistr()
    playlistr.run()
    playlistr.perform_spotify_auth()
    print(playlistr.session)
    playlistr.exit()
