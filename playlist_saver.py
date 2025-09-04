import os
import sys

import pandas as pd
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


def get_playlist(sp: spotipy.Spotify, playlist_id: str) -> pd.DataFrame:
    column_list = [
        "track_id",
        "track_name",
        "artist(s)",
        "album_name",
        "added_at",
        "duration_ms",
        "popularity",
    ]
    df = pd.DataFrame(columns=column_list)

    results = sp.playlist_items(playlist_id)
    tracks = results["items"]

    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])

    for i, song in enumerate(tracks):  # type: ignore
        track = song.get("track")
        if not track:
            continue

        df.loc[i] = [
            track.get("id"),
            track.get("name"),
            ", ".join(artist["name"] for artist in track.get("artists")),
            track.get("album").get("name"),
            song.get("added_at"),
            track.get("duration_ms"),
            track.get("popularity"),
        ]

    return df


def auth_spotipy() -> spotipy.Spotify:
    load_dotenv()

    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
    scope = "playlist-read-private playlist-read-collaborative"

    # Make sure all env vars are loaded
    if not all([client_id, client_secret, redirect_uri]):
        print(
            "[ERROR]: .env file was not able to be loaded\n"
            "Please make sure you created a .env file and entered the ALL the following:\n"
            "\tSPOTIPY_CLIENT_ID=your-id\n"
            "\tSPOTIPY_CLIENT_SECRET=your-secret\n"
            "\tSPOTIPY_REDIRECT_URL=your-url\n"
        )

        sys.exit(1)

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            open_browser=True,
        )
    )
