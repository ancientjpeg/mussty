from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from urllib import parse


class PlaylistrCallbackServer(HTTPServer):
    event: threading.Event
    session: dict

    def initialize(self):
        event = threading.Event()
        session = {}

    def server_bind(self):
        HTTPServer.server_bind(self)


class PlaylistrCallbackRequestHandler(BaseHTTPRequestHandler):

    event: threading.Event() = threading.Event()
    server: PlaylistrCallbackServer  # annotate the pre-existing server var (?)

    def do_GET(self):
        # annotate server

        parsed_path = parse.urlparse(self.path)
        self.server.session = dict(parse.parse_qsl(parsed_path.query))
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(
            '{"message":"success. please close your fucking browser now :)"}'.encode()
        )
        self.server.event.set()


class PlaylistrAuthCallbackHandler:
    # constructor is non-blocking.
    def __init__(self, auth_url: str) -> None:
        self.session: dict = {}
        self.server: PlaylistrCallbackServer = PlaylistrCallbackServer(
            ("localhost", 8005), PlaylistrCallbackRequestHandler
        )
        self.server.event: threading.Event = threading.Event()
        self.server_thread: threading.Thread = threading.Thread(
            None, target=self.server.serve_forever, daemon=True
        )
        self.server_thread.start()

        # @todo make this generic
        print(f"\nAuthorize spotify: {auth_url}\n\n")

    # this method is blocking, and will not return until the user has authed
    def get_auth_params(self):
        # wait for auth to finish
        self.server.event.wait()

        # shut down server, kill server thread
        self.server.shutdown()
        self.server_thread.join()

        # return params
        return self.server.session
