# pp_app: personal playlist application
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Replace these with your Spotify Developer credentials
SPOTIPY_CLIENT_ID = 'a96bc27e242548c88fb821581e3157de'
SPOTIPY_CLIENT_SECRET = 'cb6b0f7aa5d244658c698108b4930337'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback/'

# Scope for playlist modification and access to user's library
scope = 'playlist-modify-public'

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=scope))

# Get the current user's ID
user_id = sp.current_user()['id']

# Function to create a playlist
def create_playlist(name, description=''):
    playlist = sp.user_playlist_create(user=user_id, name=name, public=True, description=description)
    return playlist['id']

# Function to search for a track by name
def search_track(track_name):
    results = sp.search(q=track_name, limit=1, type='track')
    tracks = results['tracks']['items']
    if tracks:
        return tracks[0]['id']
    else:
        return None

# Function to add tracks to a playlist
def add_tracks_to_playlist(playlist_id, track_ids):
    sp.playlist_add_items(playlist_id, track_ids)

# Main script
if __name__ == '__main__':
    # Collect song titles from the user
    song_titles = []
    print("Enter song titles (type 'done' when finished):")
    while True:
        song_title = input("Song title: ")
        if song_title.lower() == 'done':
            break
        song_titles.append(song_title)

    # Create a new playlist
    playlist_name = input("Enter playlist name: ")
    playlist_description = input("Enter playlist description: ")
    playlist_id = create_playlist(playlist_name, playlist_description)

    # Search for each song and add to the playlist
    track_ids = []
    for title in song_titles:
        track_id = search_track(title)
        if track_id:
            track_ids.append(track_id)
        else:
            print(f"Song '{title}' not found on Spotify.")

    # Add tracks to the playlist
    if track_ids:
        add_tracks_to_playlist(playlist_id, track_ids)
        print(f"Playlist '{playlist_name}' created successfully with {len(track_ids)} tracks.")
    else:
        print("No valid songs were found to add to the playlist.")
