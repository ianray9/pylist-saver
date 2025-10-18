import os
import sys

from dotenv import load_dotenv

from src.playlist_saver import (
    auth_spotipy,
    print_menu,
    save_all,
    save_ids,
    save_playlist,
)


def main():
    load_dotenv()
    user_id = os.getenv("USER_ID")
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

    ENV_VARS = (user_id, client_id, client_secret, redirect_uri)

    # Make sure all env vars are loaded
    if not all(ENV_VARS):
        print(
            "[ERROR]: .env file was not able to be loaded\n"
            "Please make sure you created a .env file and entered the ALL the following:\n"
            "\tSPOTIPY_CLIENT_ID=your-id\n"
            "\tSPOTIPY_CLIENT_SECRET=your-secret\n"
            "\tSPOTIPY_REDIRECT_URL=your-url\n"
        )

        sys.exit(1)

    sp = auth_spotipy(ENV_VARS)

    while True:
        print_menu()

        match input("> ").strip():
            case "1":
                print("Saving all playlists...")
                save_all(sp, ENV_VARS)

            case "2":
                print("Enter Playlist ID", end="")
                print(" (or enter 'list' to get your playlist IDs)")
                id = input("> ").strip()

                if id.lower() == "list":
                    save_ids(sp, ENV_VARS)
                else:
                    save_playlist(sp, id)

            case "3":
                save_ids(sp, ENV_VARS)

            case "4":
                print("Goodbye!")
                exit(0)

            case _:
                print("Unknow command, please try again")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
