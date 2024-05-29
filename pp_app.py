# pp_app: personal playlist application
# import spotipy
# from spotipy.oauth2 import SpotifyOAuth

# # Replace these with your Spotify Developer credentials
# SPOTIPY_CLIENT_ID = 'a96bc27e242548c88fb821581e3157de'
# SPOTIPY_CLIENT_SECRET = 'cb6b0f7aa5d244658c698108b4930337'
# SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback/'

# # Scope for playlist modification and access to user's library
# scope = 'playlist-modify-public'

# # Authenticate with Spotify
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
#                                                client_secret=SPOTIPY_CLIENT_SECRET,
#                                                redirect_uri=SPOTIPY_REDIRECT_URI,
#                                                scope=scope))

# # Get the current user's ID
# user_id = sp.current_user()['id']

# # Function to create a playlist
# def create_playlist(name, description=''):
#     playlist = sp.user_playlist_create(user=user_id, name=name, public=True, description=description)
#     return playlist['id']

# # Function to search for a track by name
# def search_track(track_name):
#     results = sp.search(q=track_name, limit=1, type='track')
#     tracks = results['tracks']['items']
#     if tracks:
#         return tracks[0]['id']
#     else:
#         return None

# # Function to add tracks to a playlist
# def add_tracks_to_playlist(playlist_id, track_ids):
#     sp.playlist_add_items(playlist_id, track_ids)

# # Main script
# if __name__ == '__main__':
#     # Collect song titles from the user
#     song_titles = []
#     print("Enter song titles (type 'done' when finished):")
#     while True:
#         song_title = input("Song title: ")
#         if song_title.lower() == 'done':
#             break
#         song_titles.append(song_title)

#     # Create a new playlist
#     playlist_name = input("Enter playlist name: ")
#     playlist_description = input("Enter playlist description: ")
#     playlist_id = create_playlist(playlist_name, playlist_description)

#     # Search for each song and add to the playlist
#     track_ids = []
#     for title in song_titles:
#         track_id = search_track(title)
#         if track_id:
#             track_ids.append(track_id)
#         else:
#             print(f"Song '{title}' not found on Spotify.")

#     # Add tracks to the playlist
#     if track_ids:
#         add_tracks_to_playlist(playlist_id, track_ids)
#         print(f"Playlist '{playlist_name}' created successfully with {len(track_ids)} tracks.")
#     else:
#         print("No valid songs were found to add to the playlist.")

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
scope = 'playlist-modify-public'

sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope=scope)

@app.route('/')
def index():
    if not session.get('token_info'):
        return redirect(url_for('login'))
    return '''
        <form action="/create_playlist" method="post">
            <label for="playlist_name">Playlist Name:</label>
            <input type="text" id="playlist_name" name="playlist_name">
            <label for="playlist_description">Playlist Description:</label>
            <input type="text" id="playlist_description" name="playlist_description">
            <label for="songs">Song Titles (comma separated):</label>
            <input type="text" id="songs" name="songs">
            <input type="submit" value="Create Playlist">
        </form>
    '''

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('index'))

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    if not session.get('token_info'):
        return redirect(url_for('login'))

    token_info = session.get('token_info')
    sp = spotipy.Spotify(auth=token_info['access_token'])

    user_id = sp.current_user()['id']
    playlist_name = request.form['playlist_name']
    playlist_description = request.form['playlist_description']
    song_titles = request.form['songs'].split(',')

    playlist_id = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=playlist_description)['id']
    
    track_ids = []
    for title in song_titles:
        result = sp.search(q=title.strip(), limit=1, type='track')
        tracks = result['tracks']['items']
        if tracks:
            track_ids.append(tracks[0]['id'])
    
    if track_ids:
        sp.playlist_add_items(playlist_id, track_ids)
        return f"Playlist '{playlist_name}' created successfully with {len(track_ids)} tracks."
    else:
        return "No valid songs were found to add to the playlist."

if __name__ == '__main__':
    app.run(debug=True, port=8888)
