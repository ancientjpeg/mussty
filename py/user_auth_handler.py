from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from urllib import parse
import webbrowser


class UserAuthHTTPServer(HTTPServer):
    event: threading.Event
    parsed_path: parse.ParseResult
    query_dict: dict

    def initialize(self):
        self.event = threading.Event()

    def server_bind(self):
        HTTPServer.server_bind(self)


class UserAuthHTTPRequestHandlerBase(BaseHTTPRequestHandler):

    server: UserAuthHTTPServer  # annotate the pre-existing server var

    # use this to decorate handler methods
    # be sure to do server.event.set() when you're totally done. @todo that's stupid, do nested decorators or something
    # @todo name this something that isn't stupid
    @staticmethod
    def do_GET_decorator(func):
        def self_wrapper(self: UserAuthHTTPRequestHandlerBase):
            self.server.parsed_path = parse.urlparse(self.path)
            self.server.query_dict = dict(
                parse.parse_qsl(self.server.parsed_path.query)
            )
            func(self)

        return self_wrapper

    def return_successfully(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        print(self.server.query_dict)
        self.end_headers()
        with open("html/success.html") as f:
            self.wfile.write(f.read().encode())
        self.server.event.set()


class UserAuthHandler:
    # constructor is non-blocking.
    def __init__(self, auth_url: str, handler_type) -> None:
        self.server: UserAuthHTTPServer = UserAuthHTTPServer(
            ("localhost", 8005), handler_type
        )
        self.server.event: threading.Event = threading.Event()
        self.server_thread: threading.Thread = threading.Thread(
            None, target=self.server.serve_forever, daemon=True
        )
        self.server_thread.start()

        webbrowser.open(auth_url)

    # this method is blocking, and will not return until the user has authed
    def get_auth_params(self):
        # wait for auth to finish
        self.server.event.wait()

        # shut down server, kill server thread
        self.server.shutdown()
        self.server_thread.join()

        # return params
        return self.server.query_dict
