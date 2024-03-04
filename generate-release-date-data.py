#!/usr/bin/env python3
from flask import Flask, session, url_for, request, redirect

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

import os
import json
import argparse
import time
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)

config = json.loads(open("config.json", "r").read())
MAX_ALBUM_GET_NUMBER = 50


cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=config["client_id"],
    client_secret=config["client_secret"],
    redirect_uri=config["redirect_uri"],
    scope=config["scope"],
    cache_handler=cache_handler,
    show_dialog=False
)

sp = Spotify(auth_manager=sp_oauth)

def get_album_data(artist, spotify_id):
    offset = 0
    items = []

    while True:
        albums = sp.artist_albums(spotify_id, album_type="album,single", limit=MAX_ALBUM_GET_NUMBER, offset=offset)
        if len(albums["items"]) == 0:
            break
        items += [{ "name": f"{artist} - {item['name']}", "release_date": item["release_date"] } for item in albums["items"] if item["total_tracks"] > 2]
        offset += MAX_ALBUM_GET_NUMBER

    return items

@app.route("/")
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for("artists"))

@app.route("/callback")
def callback():
    sp_oauth.get_access_token(request.args["code"])
    return redirect(url_for("artists"))

@app.route("/artists")
def artists():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    parser = argparse.ArgumentParser("generate-release-date-data.py")
    parser.add_argument("location", help="The location of the CSV file containing the IDs for every artist.", type=argparse.FileType("r", encoding="UTF-8"))
    args = parser.parse_args()

    f = open(args.location.name, "r")
    lines = f.readlines()

    items = []
    for i, line in enumerate(lines):
        line = line.replace("\n", "")
        components = line.split(",")

        if len(components) > 2:
            # [0] - Artist name, [1] - Primary artist ID, Optional: [2...n-1] - Secondary artist IDs, Optional: [n] - Listener percentage to be added. Not used here
            for identifier in components[1:-1]:
                items += get_album_data(components[0], identifier)
        else:
            items += get_album_data(components[0], components[1])

        sleepTime = random.randint(200, 700)
        time.sleep(sleepTime / 100)

    return items

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
