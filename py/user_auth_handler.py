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

    auth_server: UserAuthHTTPServer  # annotate the pre-existing server var

    # use this to decorate handler methods
    # be sure to do server.event.set() when you're totally done. @todo that's stupid, do nested decorators or something
    # @todo name this something that isn't stupid
    @staticmethod
    def do_GET_decorator(func):
        def self_wrapper(self: UserAuthHTTPRequestHandlerBase):
            self.auth_server.parsed_path = parse.urlparse(self.path)
            self.auth_server.query_dict = dict(
                parse.parse_qsl(self.auth_server.parsed_path.query)
            )
            func(self)

        return self_wrapper

    def return_successfully(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        print(self.auth_server.query_dict)
        self.end_headers()
        with open("html/success.html") as f:
            self.wfile.write(f.read().encode())
        self.auth_server.event.set()


class UserAuthHandler:

    auth_server: UserAuthHTTPServer

    # constructor is non-blocking.
    def __init__(self, auth_url: str, request_handler_type) -> None:
        self.auth_server  = UserAuthHTTPServer(
            ("localhost", 8005), request_handler_type
        )
        self.auth_server.event = threading.Event()
        self.server_thread: threading.Thread = threading.Thread(
            None, target=self.auth_server.serve_forever, daemon=True
        )
        self.server_thread.start()

        webbrowser.open(auth_url)

    # this method is blocking, and will not return until the user has authed
    def get_auth_params(self):
        # wait for auth to finish
        self.auth_server.event.wait()

        # shut down server, kill server thread
        self.auth_server.shutdown()
        self.server_thread.join()

        # return params
        return self.auth_server.query_dict
