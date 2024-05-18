from pytube import Playlist, YouTube, Channel
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from flask import Flask, request, url_for, session, redirect, render_template
import csv


app = Flask(__name__)

clientID = 'e61032d8b5654366b5b33d91eede43ad'
clientSecret = 'e755df87f9bf440d811c2f3ea305d95e'

app.secret_key = "abcdefg"
app.config['Session_Cookie_Name'] = "Ajai's Cookie"
TOKEN_INFO = "token_info"

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code, check_cache=False)
    session[TOKEN_INFO] = token_info
    print("Token Info:", token_info)
    return redirect(url_for('youtube_scrape', _external=True))

@app.route('/youtube_scrape')
def youtube_scrape():

    link = "https://music.youtube.com/playlist?list=PL5C2tAj5shVO0V5suzCsd885u7CVo94K_"

    vlinks = Playlist(link)

    f = open('songs.csv', 'r+')
    f.truncate(0)

    filename = 'songs.csv'
    f = open(filename, 'a')
    headers = 'Artist,Song\n'
    f.write(headers)

    for song in vlinks:
        
        item = YouTube(song)
        channel_url = item.channel_url
        c = Channel(channel_url)
        name = c.channel_name
        name = name.split('-')[0].strip()
        title = item.title.replace(",","")
        name = name.replace(",","")
        f.write(name +', '+ title +', ' + '\n')
        print(name +" "+ title)
        print("\n")
    f.close()
    
    
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect('/')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    
    song_uris = []
    user_id = sp.current_user()['id']
    
    csv_file = 'songs.csv'
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            song_name = row['Song']
            artist_name = row['Artist']

            # Search for song
            results = sp.search(q=song_name +' '+ artist_name, type='track')
            
            # Get song URI if found
            if results['tracks']['items']:
                song_uri = results['tracks']['items'][0]['uri']
                song_uris.append(song_uri)
                print(f"Song: {song_name} by {artist_name}, URI: {song_uri}")
            else:
                print(f"Song: {song_name} by {artist_name} not found on Spotify")
    file.close()

    name = "Youtube Playlist"
    yt_playlist = sp.user_playlist_create(user_id, name, True)
    yt_playlist_id = yt_playlist['id']
    sp.user_playlist_add_tracks(user_id, yt_playlist_id, song_uris)

    return "done"
def get_token():
    token_info = session.get(TOKEN_INFO, None)

    if not token_info:
        raise Exception("Token not found in session")
    now = int(time.time())

    is_expired = token_info['expires_at'] - now <60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
            client_id='e61032d8b5654366b5b33d91eede43ad',
            client_secret='e755df87f9bf440d811c2f3ea305d95e',
            redirect_uri=url_for('redirectPage', _external=True),
            scope = "user-library-read playlist-modify-public playlist-modify-private")

app.run()