# Get Spotify data of performers
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

# Open file where you have stored your API key and secret for Spotify
# Help from here: https://stackoverflow.com/questions/29056008/using-github-with-secret-keys
from keys import client_id, client_secret

client_credentials_manager = SpotifyClientCredentials(client_id = client_id, client_secret = client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# For a singer
sp.search(q="Luciano Pavarotti", type="artist", limit=1)

# For an album
sp.search(q="Lucia di Lammermoor", type="album", limit=1)

# For tracks of an album (will have to iterate quite a bit...)
sp.search(q="nessun dorma", type="track", limit=1)
