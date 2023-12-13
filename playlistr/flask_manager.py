from flask import Flask, request, redirect, session
from .playlistr_singleton import playlistr


# playlistr_app = Flask(__name__)


# @playlistr_app.route("/", methods=["GET"])
# def index():
#     return redirect("/spotify-app")


# @playlistr_app.route("/spotify-app", methods=["GET"])
# def spotify_app():
#     assert playlistr != None
#     return redirect(playlistr.spotify.spotify_auth_url())


# @playlistr_app.route("/spotify-callback", methods=["GET"])
# def spotify_callback():
#     code = request.args.get("code")
#     if code:
#         playlistr.session["spotify_auth_code"] = code
#         return "please close this tab :)"
#     return "something went very wrong..."
