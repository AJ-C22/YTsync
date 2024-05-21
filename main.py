from pytube import Playlist, YouTube, Channel
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from flask import Flask, request, url_for, session, redirect, render_template, jsonify
import requests

app = Flask(__name__)
app.secret_key = "abcdefg"
TOKEN_INFO = "token_info"

# Spotify API credentials
CLIENT_ID = 'e61032d8b5654366b5b33d91eede43ad'
CLIENT_SECRET = 'e755df87f9bf440d811c2f3ea305d95e'
REDIRECT_URI = 'http://127.0.0.1:5000/redirect' 

#Initial OAUTH route
@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

#Spotify API rediret route
@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code, check_cache=False)
    session[TOKEN_INFO] = token_info
    print("Token Info:", token_info)
    return redirect(url_for('youtube_scrape'))

#Scrapes YouTube Music Playlist
@app.route('/youtube_scrape', methods=['POST', 'GET'])
def youtube_scrape():
    if request.method == 'POST':
        link = request.json.get('link')
        print("Link:", link)

        if link:
            # Scrape YouTube playlist
            vlinks = Playlist(link)
            playlist_title = vlinks.title
            print("\n")

            song_uris = []

            for song in vlinks:
                item = YouTube(song)
                channel_url = item.channel_url
                c = Channel(channel_url)
                name = c.channel_name.split('-')[0].strip()
                title = item.title.replace(",", "")
                print(name + " " + title)
                print("\n")
                song_uris.append(search_spotify(name, title))

            # Create Spotify playlist
            sp = get_spotify_client()
            playlist_id = create_spotify_playlist(sp, playlist_title, song_uris)

            return jsonify({'message': 'Playlist created successfully', 'playlist_id': playlist_id})
        else:
            return jsonify({'error': 'No link provided'})
    else:
        return render_template('index.html')

# Searches for Spotify song 
def search_spotify(artist_name, song_name):
    sp = get_spotify_client()
    results = sp.search(q=f'{song_name} {artist_name}', type='track')

    if results['tracks']['items']:
        return results['tracks']['items'][0]['uri']
    else:
        print(f"Song: {song_name} by {artist_name} not found on Spotify")
        return None

# Spotify token verification and spotipy activation
def get_spotify_client():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise Exception("Token not found in session")

    sp = spotipy.Spotify(auth=token_info['access_token'])
    return sp

# Creates a playlist using the song uris
def create_spotify_playlist(sp, name, song_uris):
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id, name, public=False)
    sp.user_playlist_add_tracks(user_id, playlist['id'], song_uris)
    return playlist['id']

# Spotify OAuth
def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-library-read playlist-modify-public playlist-modify-private"
    )

if __name__ == '__main__':
    app.run(debug=True)
