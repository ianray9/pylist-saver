import sys

from playlist_saver import auth_spotipy, print_menu, save_ids, save_playlist


def main():
    try:
        sp = auth_spotipy()
    except Exception as e:
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

    while True:
        print_menu()

        match input("> ").strip():
            case "1":
                print("Saving all playlists...")

            case "2":
                print("Enter Playlist ID", end="")
                print(" (or enter 'list' to get your playlist IDs)")
                id = input("> ").strip()

                if id.lower() == "list":
                    save_ids(sp)
                else:
                    save_playlist(sp, id)

            case "3":
                save_ids(sp)

            case "4":
                print("Goodbye!")
                exit(0)

            case _:
                print("Unknow command, please try again")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
