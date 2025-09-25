import os
import re
import sys
import textwrap
from pathlib import Path

import pandas as pd
import spotipy
from dotenv import load_dotenv
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

from colors import Colors


def save_all(sp: spotipy.Spotify) -> None:
    save_all_tracks(sp)


def save_all_tracks(sp: spotipy.Spotify) -> None:
    load_dotenv()
    playlists = sp.user_playlists(user=os.getenv("USER_ID"))

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

    # Get try to get playlist with playlist_id
    try:
        playlist_meta = sp.playlist(playlist_id)
    except SpotifyException as e:
        if e.http_status == 400 and e.code == -1 and "Unsupported URL / URI" in str(e):
            print("Unable to find playlist with that id :(")
            return
        else:
            raise

    playlist_name = playlist_meta.get("name", "unknown_playlist")

    # Get playlist tracks
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
            i + 1,
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


def save_ids(sp: spotipy.Spotify) -> None:
    playlists = []

    # Load all playlists from user
    load_dotenv()
    results = sp.user_playlists(user=os.getenv("USER_ID"))

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
