from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from .spotify import Spotify
from urllib import parse

session = {}


class PlaylistrCallbackServer(HTTPServer):
    def server_bind(self):
        self.event: threading.Event = threading.Event()
        HTTPServer.server_bind(self)


class PlaylistrCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # annotate server
        self.server: PlaylistrCallbackServer

        parsed_path = parse.urlparse(self.path)
        parsed_qs = dict(parse.parse_qsl(parsed_path.query))

        path = parsed_path.path

        if path == "/spotify-callback":
            session["spotify_auth_code"] = parsed_qs["code"]
            self.send_response(200)
            self.server.event.set()
        else:
            self.send_response(400)


class Playlistr:
    exists: bool = False
    session: dict = None
    spotify: Spotify
    server: PlaylistrCallbackServer = None
    server_thread: threading.Thread
    event: threading.Event

    def __new__(cls):
        if cls.exists:
            raise RuntimeError("Don't make more than one Playlistr object.")

        cls.exists = True

        cls.session = session
        cls.spotify = Spotify()
        cls.server = PlaylistrCallbackServer(
            ("localhost", 8005), PlaylistrCallbackHandler
        )
        cls.event = cls.server.event

        instance = super().__new__(cls)
        return instance

    def perform_spotify_auth(self):
        print(f"\nAuthorize spotify: {self.spotify.spotify_auth_url()}\n\n")
        self.event.wait()
        self.spotify.auth_code = self.session["spotify_auth_code"]
        self.spotify.get_token()
        self.spotify.get_tracks()

    def perform_apple_auth(self):
        ...

    def run(self):
        self.server_thread = threading.Thread(
            None, target=self.server.serve_forever, daemon=True
        )
        self.server_thread.start()

    def exit(self):
        self.server.shutdown()
        self.server_thread.join()
