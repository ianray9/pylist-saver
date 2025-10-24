# PYlist Saver
A simple CLI tool to save playlist tracks and metadata to CSV files.

PYlist saves your playlist data in two types of CSV files. The first is all of your playlists' metadata in a single CSV called playlist_meta_info.csv.

Playlist track data Columns info
| Column Name | Description |
|---|---|
| playlist_id | ID of Playlist |
| name | Name of playlist |
| owner | Owner of playlist |
| track_count | Number of tracks in playlist |
| created_on | Date when the first song was added |
| public | Whether the playlist is public or not |
| collaborative | Whether the playlist is collaborative or not |
| description | Playlist description |
| image_url | Url to the cover image for the playlist |

The next type of CSV file PYlist saves is track information for a playlist. This CSV file contains track information for one playlist. PYlist will save this to a directory called playlists. The playlist CSV file will be saved to a file named in the form of {name}_tracks_{playlist_id}.csv

**NOTE** The name in the file will be stripped of unsafe file characters so that it may look a little different from the name on Spotify.

Playlist track data Columns info
| Column Name | Description |
|---|---|
| track_number | Index of the track in your playlist |
| track_id | Spotify track id |
| track_name | Track title |
| artist(s) | List of artist(s) of track |
| album_name | Name of album the track is from  |
| added_at | When the track was added to the playlist |
| duration_ms | Track length in ms |
| popularity | Spotify's popularity rating for the track |

## Quick start guide
### Requirements
- conda
- ngrok
### Environment setup
Clone repo
```
git clone https://github.com/ianray9/pylist-saver.git
cd pylist-saver
```
Create conda env
```
conda create --name pyls --file requirements.txt
conda activate pyls
```
### Spotify API setup and authentication
Create a .env file for the PYlist. You can easily do this by copying the .env example and renaming it.
```
cp example_env.txt .env
```

In another terminal or window, create an ngrok tunnel on port 8888 for Spotify authentication.

**NOTE:** PYlist should cache the authentication, so you can close this tunnel after you run PYlist once
`ngrok http 8888`

Enter the ngrok URL from the ngrok local [portal](http://127.0.0.1:4040) into the `SPOTIPY_REDIRECT_URI` field in the .env.

Sign in to your Spotify account in the [Spotify Developers Portal](https://developer.spotify.com/) and create an app in the [Spotify Developers Dashboard](https://developer.spotify.com/dashboard)
You can fill in any information for the app name and description, but make sure to enter your ngrok tunnel URL.

Enter the Client ID and Secret from your Spotify app into the .env fields `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET`.

Enter your Spotify User ID into the `USER_ID`. You can find your [Spotify Overview Portal](https://www.spotify.com/us/account/overview/) and click "Edit personal info," and your ID should be under username.

## Running
Make sure your conda environment is activated and you are in the PYlist root directory, and run "main.py".
```
conda activate pyls
python main.py
```
### How to use
When you run PYlist, you will have 4 options
1. Save all playlists - Save all your playlist meta data and all playlist track data
2. Save one playlist - Save track data for one playlist. You will need the ID of the playlist you want to save. 
3. Get playlist IDs - Save all your playlist IDs into a CSV file that you can use to find the ID of the playlist you want to save

## Common issues
Why is the authentication not working after working before?
- This happens usually because Spotify needs to reauthenticate your account, and the ngrok tunnel is not running anymore
    - To fix, just rerun the ngrok tunnel and reauthenticate your account (Also **make sure to update your .env** and Spotify App information for the new link)
