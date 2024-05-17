from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import csv

# Define the URL of the YouTube Music playlist
url_to_scrape = "https://music.youtube.com/playlist?list=PL5C2tAj5shVP1N_Fci6gn86Oh_Nksu2MO"

# Initialize an HTML session
session = HTMLSession()

# Send a GET request to the URL
response = session.get(url_to_scrape)

# Render the JavaScript on the page
response.html.render(timeout=30, sleep=2)

# Parse the rendered HTML using BeautifulSoup
soup = BeautifulSoup(response.html.html, 'html.parser')

# Find all song title elements
songs = soup.find_all('a', class_="yt-simple-endpoint style-scope yt-formatted-string")

# Open the CSV file for writing
filename = 'songs.csv'
with open(filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Song', 'Artist'])

    # Iterate through the found song elements
    for song in songs:
        song_title = song.text.strip()
        print(song_title)
        # Write the song title to the CSV file
        writer.writerow([song_title, ''])

print("Done")
