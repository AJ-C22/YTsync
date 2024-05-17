from pytube import Playlist, YouTube, Channel
import pandas as pd

link = "https://music.youtube.com/playlist?list=PL5C2tAj5shVP1N_Fci6gn86Oh_Nksu2MO"

vlinks = Playlist(link)

songs = []
for song in vlinks:
    
    item = YouTube(song)
    channel_url = item.channel_url
    c = Channel(channel_url)
    name = c.channel_name
    name = name.split('-')[0].strip()
    
    print(name)
    print(item.title)

