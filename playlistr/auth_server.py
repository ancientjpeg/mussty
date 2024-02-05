from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from urllib import parse


class PlaylistrCallbackServer(HTTPServer):
    event: threading.Event
    parsed_path: parse.ParseResult
    query_dict: dict

    def initialize(self):
        self.event = threading.Event()

    def server_bind(self):
        HTTPServer.server_bind(self)


class PlaylistrCallbackRequestHandlerBase(BaseHTTPRequestHandler):

    event: threading.Event() = threading.Event()
    server: PlaylistrCallbackServer  # annotate the pre-existing server var

    # use this to decorate handler methods
    # @todo name this something that isn't stupid
    @staticmethod
    def do_GET_decorator(func):
        def self_wrapper(self: PlaylistrCallbackRequestHandlerBase):
            self.server.parsed_path = parse.urlparse(self.path)
            self.server.query_dict = dict(
                parse.parse_qsl(self.server.parsed_path.query)
            )
            func(self)
            self.server.event.set()

        return self_wrapper


class PlaylistrAuthCallbackHandler:
    # constructor is non-blocking.
    def __init__(self, auth_url: str, handler_type) -> None:
        self.server: PlaylistrCallbackServer = PlaylistrCallbackServer(
            ("localhost", 8005), handler_type
        )
        self.server.event: threading.Event = threading.Event()
        self.server_thread: threading.Thread = threading.Thread(
            None, target=self.server.serve_forever, daemon=True
        )
        self.server_thread.start()

    # this method is blocking, and will not return until the user has authed
    def get_auth_params(self):
        # wait for auth to finish
        self.server.event.wait()

        # shut down server, kill server thread
        self.server.shutdown()
        self.server_thread.join()

        # return params
        return self.server.query_dict
