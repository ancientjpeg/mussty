import requests as r
import json
from flask import Flask, request as fr


app = Flask(__name__)


class spotify_state:
    auth_code: str
    auth_token: str


spotify_st: spotify_state = spotify_state()


def spotify_auth_url():
    secrets = get_secrets()
    params = {
        "client_id": secrets["spotify"]["client_id"],
        "response_type": "code",
        "redirect_uri": "http://localhost:8005/spotify",
    }
    headers = {}
    req = r.Request(
        "GET", "https://accounts.spotify.com/authorize", params=params, headers=headers
    )
    return req.prepare().url


@app.route("/spotify", methods=["GET"])
def spotify_st():
    code = fr.args.get("code")
    if code:
        spotify_st.auth_code = code
        return "please close this tab :)"
    return "something went very wrong..."


if __name__ == "__main__":
    print(f"Login to spotify here: {spotify_auth_url()}")
    app.run("localhost", 8005)
