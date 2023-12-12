import requests as r
import json
from flask import Flask, request as fr
from services.spotify import SpotifyService


app = Flask(__name__)

spotify_service = SpotifyService()


@app.route("/spotify", methods=["GET"])
def spotify_st():
    code = fr.args.get("code")
    if code:
        spotify_st.auth_code = code
        return "please close this tab :)"
    return "something went very wrong..."


if __name__ == "__main__":
    print(f"Login to spotify here: {spotify_service.spotify_auth_url()}")
    app.run("localhost", 8005)
