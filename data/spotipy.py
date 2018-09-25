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
os.chdir("/Users/katelyons/Documents/Insight/figaro/data")
from keys import client_id, client_secret

client_credentials_manager = SpotifyClientCredentials(client_id = client_id, client_secret = client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# For a singer
sp.search(q="Luciano Pavarotti", type="artist", limit=1)

# For an album
sp.search(q="Lucia di Lammermoor", type="album", limit=1)

# For tracks of an album (will have to iterate quite a bit...)
sp.search(q="nessun dorma", type="track", limit=1)

# Collect Spotify data
singer = sp.search(q="Ezio Pinza", type="artist", limit=1)
singer

# This will tell us this artist's popularity score
for i, t in enumerate(singer['artists']['items']):
    artist_id = (t['id'])
    artist_popularity = (t['popularity'])

artist_id
artist_popularity

# Now do this ... iteratively
# Get popularity and artist ids from a data frame that has a column of singers
# First have to access database where this information is stored
dbname = 'figaro'
username = 'katelyons'

## 'engine' is a connection to a database
## Here, we're using postgres, but sqlalchemy can connect to other things too.
engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))
print(engine.url)

# Connect to make queries using psycopg2
con = None
con = psycopg2.connect(database = dbname, user = username)

# query:
sql_query = """SELECT * FROM met_archive;"""
met_data = pd.read_sql_query(sql_query,con)

# We have duplicates of artist's names in this dataset, let's slim it down!
# All we need are artist scores, so just pull out those and get rid of duplicates
met_data = met_data.drop(['role', 'opera', 'date','CID'], axis=1)
met_data = met_data.drop_duplicates(subset='artist', keep='first').set_index('index')

# Looping thru data frame
# Probably a dumb solution but it will work at least -- make column of names in pandas df a list
dfList = met_data['artist'].tolist()

dfs = []
for artist in dfList:
    artist_results = sp.search(q=artist, type="artist", limit=1)

    try:
        for i, t in enumerate(artist_results['artists']['items']):
            artist_popularity = (t['popularity'])
            artist_popularity = str(artist_popularity)
            artist_id = (t['id'])
    except:
        artists_results= None

    tempdf = pd.DataFrame(columns=['artist_popularity', 'spotify_id'])
    tempdf = tempdf.append({'artist_popularity':artist_popularity, 'spotify_id':artist_id}, ignore_index=True)
    # tempdf = tempdf.append({'spotify_id':artist_id}, ignore_index=True)

    # tempdf = pd.DataFrame({'artist_popularity': artist_popularity, 'spotify_id': 'artist_id'})
    dfs.append(tempdf)
    # time.sleep(1)


masterDF = pd.concat(dfs, ignore_index=True)

# Sandwich this together with original df
met_data2 = met_data.reset_index()
masterDF2 = pd.concat([met_data2, masterDF], axis = 1, sort = False)

# Save / update SQL database
# Just keep stuff we are interested in
met_data3 = masterDF2.drop(['index'], axis=1)

artist_data = met_data3

# Save in database
artist_data.to_sql('artist_data', engine, if_exists='replace')

# Next --> get song attributes / most popular tracks in an opera!
