import os

from playlist_saver import auth_spotipy


def main():
    sp = auth_spotipy()

    playlists = sp.user_playlists(os.getenv("USER_ID"))

    while playlists:
        for i, playlist in enumerate(playlists["items"]):
            print(
                f"{i + 1 + playlists['offset']:4d} {playlist['uri']} {playlist['name']}"
            )
        if playlists["next"]:
            playlists = sp.next(playlists)
        else:
            playlists = None


if __name__ == "__main__":
    main()
