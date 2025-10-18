import os
import re
import sys
import textwrap
from pathlib import Path

import pandas as pd
import spotipy
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

from src.colors import Colors


def save_all(sp: spotipy.Spotify, ENV_VARS: tuple) -> None:
    save_meta(sp, ENV_VARS)
    save_all_playlists(sp, ENV_VARS)


def save_all_playlists(sp: spotipy.Spotify, ENV_VARS: tuple) -> None:
    playlists = sp.user_playlists(user=ENV_VARS[0])

    # Save all user playlists
    while playlists:
        for playlist in playlists["items"]:
            save_playlist(sp, playlist["id"])
        if playlists["next"]:
            playlists = sp.next(playlists)
        else:
            playlists = None

    c = Colors()
    print("\n" + c.set_color("Done!", "green"))
    print("All playlist track data saved in playlists directory")


def get_created_date(sp: spotipy.Spotify, id: str) -> str:
    track_dates = []
    results = sp.playlist_items(id)
    tracks = results["items"]

    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])

    for song in tracks:  # type: ignore
        track = song.get("track")
        track_dates.append(song.get("added_at"))

        if not track:
            continue

    # Sort list to get earliest date that a song was added
    track_dates.sort()
    return track_dates[0]


def save_meta(sp: spotipy.Spotify, ENV_VARS: tuple) -> None:
    playlists = sp.user_playlists(user=ENV_VARS[0])

    column_list = [
        "playlist_id",
        "name",
        "owner",
        "track_count",
        "created_on",
        "public",
        "collaborative",
        "description",
        "image_url",
    ]
    df = pd.DataFrame(columns=column_list)

    c = Colors()
    while playlists:
        for playlist in playlists["items"]:
            df.loc[len(df)] = {
                "playlist_id": playlist.get("id"),
                "name": playlist.get("name"),
                "owner": playlist.get("owner"),
                "track_count": playlist.get("tracks")["total"],
                "created_on": get_created_date(sp, playlist["id"]),
                "public": playlist.get("public"),
                "collaborative": playlist.get("collaborative"),
                "description": playlist.get("description"),
                "image_url": playlist.get("images")[0]["url"],
            }

            print(
                f"Saved playlist meta data: {c.set_color(f"{playlist["name"]}", "yellow")}"
            )

        if playlists["next"]:
            playlists = sp.next(playlists)
        else:
            playlists = None

    csv_name = "playlist_meta_info.csv"
    df.to_csv(csv_name)
    print(f"{c.set_color("User playlist ", "green")} saved to:\n\t{csv_name}")


def save_playlist(sp: spotipy.Spotify, playlist_id: str) -> None:
    column_list = [
        "track_number",
        "track_id",
        "track_name",
        "artist(s)",
        "album_name",
        "added_at",
        "duration_ms",
        "popularity",
    ]
    df = pd.DataFrame(columns=column_list)

    # Try to get playlist with playlist_id
    playlist_meta = get_playlist_meta(sp, playlist_id)

    playlist_name = playlist_meta.get("name", "unknown_playlist")

    # Get playlist tracks
    results = sp.playlist_items(playlist_id)
    tracks = results["items"]

    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])

    for song in tracks:  # type: ignore
        track = song.get("track")
        if not track:
            continue

        df.loc[len(df)] = [
            len(df) + 1,
            track.get("id"),
            track.get("name"),
            ", ".join(artist["name"] for artist in track.get("artists")),
            track.get("album").get("name"),
            song.get("added_at"),
            track.get("duration_ms"),
            track.get("popularity"),
        ]

    # Make sure playlist dir is created
    Path("./playlists/").mkdir(parents=True, exist_ok=True)

    # Create safe file name
    safe_name = re.sub(r'[\\/*?:"<>|]', "-", playlist_name)
    safe_name = re.sub(r"[\s+/]", "-", playlist_name)
    csv_name = f"{safe_name}_tracks_{playlist_id}.csv"
    csv_path = f"playlists/{csv_name}"

    c = Colors()
    df.to_csv(csv_path, index=False)
    print(f"{c.set_color(playlist_name, "yellow")} saved to:\n\t{csv_path}")


def save_ids(sp: spotipy.Spotify, ENV_VARS: tuple) -> None:
    playlists = []

    results = sp.user_playlists(user=ENV_VARS[0])

    # Append all playlist info to df
    while results:
        for item in results["items"]:
            playlists.append({"name": item.get("name"), "id": item.get("id")})

        if results.get("next"):
            results = sp.next(results)
        else:
            break

    id_df = pd.DataFrame(playlists)
    id_df.to_csv("playlist_ids.csv", index=False)
    print("Playlist names and ids are in playlist_ids.csv.")


def get_playlist_meta(sp: spotipy.Spotify, id: str):
    try:
        playlist_meta = sp.playlist(id)
    except SpotifyException as e:
        if e.http_status == 400 and e.code == -1 and "Unsupported URL / URI" in str(e):
            print("Unable to find playlist with that id :(")
            return
        else:
            raise
    return playlist_meta


def auth_spotipy(ENV_VARS: tuple) -> spotipy.Spotify:
    client_id = ENV_VARS[1]
    client_secret = ENV_VARS[2]
    redirect_uri = ENV_VARS[3]

    scope = "playlist-read-private playlist-read-collaborative"

    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=scope,
                open_browser=True,
            )
        )
    except SpotifyException as e:
        print(
            "[ERROR] SPOTIFY AUTHENTICATION FAILED!\n"
            "Please make sure the .env info is correct.\n"
            "Hint: A common mistake is that the ngrok URL is not correct.\n"
            "      - Run 'ngrok http 8888'\n"
            "      - Open the listed URL\n"
            "      - Copy the HTTPS IRL into the redirect URI in \n"
        )
        print(f"Exception: {e}")
        sys.exit(1)

    return sp


def print_menu():
    cli_header = textwrap.dedent(
        """\
██████╗ ██╗   ██╗██╗     ██╗███████╗████████╗
██╔══██╗╚██╗ ██╔╝██║     ██║██╔════╝╚══██╔══╝
██████╔╝ ╚████╔╝ ██║     ██║███████╗   ██║   
██╔═══╝   ╚██╔╝  ██║     ██║╚════██║   ██║   
██║        ██║   ███████╗██║███████║   ██║   
╚═╝        ╚═╝   ╚══════╝╚═╝╚══════╝   ╚═╝   
███████╗ █████╗ ██╗   ██╗███████╗██████╗     
██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗    
███████╗███████║██║   ██║█████╗  ██████╔╝    
╚════██║██╔══██║╚██╗ ██╔╝██╔══╝  ██╔══██╗    
███████║██║  ██║ ╚████╔╝ ███████╗██║  ██║    
╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝    """
    )

    # Clear CLI
    os.system("cls" if os.name == "nt" else "clear")

    c = Colors()
    print(c.set_color(cli_header.rstrip("\n"), "bold_green"), end="")

    options = [
        "Choose one of the following",
        f"{c.set_color("[1]", "green")} Save all playlists",
        f"{c.set_color("[2]", "green")} Save one playlist",
        f"{c.set_color("[3]", "green")} Get playlist ids",
        f"{c.set_color("[4]", "red")} Exit",
    ]
    print("\n".join(options))
