from .apple_music import AppleMusic
from .resolver import Resolver
from .spotify import Spotify

if __name__ == "__main__":
    resolver = Resolver((AppleMusic, Spotify))
    resolver.resolve()
