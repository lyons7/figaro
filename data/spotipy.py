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
singer['artists']['items']
singer

# This will tell us this artist's popularity score
for i, t in enumerate(singer['artists']['items']):
    artist_id = (t['id'])
    artist_popularity = (t['popularity'])
    artist = (t['name'])

artist_id
artist_popularity
artist

# Now do this ... iteratively
# Get popularity and artist ids from a data frame that has a column of singers
# First have to access database where this information is stored
os.chdir("/Users/katelyons/Documents/Insight/figaro/data")
from sql import dbname, username

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
    if artist_results['artists']['items'] == []:
        continue
    for i, t in enumerate(artist_results['artists']['items']):
        artist_popularity = (t['popularity'])
        artist_popularity = str(artist_popularity)
        artist_id = (t['id'])
        artist = (t['name'])

    tempdf = pd.DataFrame(columns=['artist', 'artist_popularity', 'spotify_id'])
    tempdf = tempdf.append({'artist':artist, 'artist_popularity':artist_popularity, 'spotify_id':artist_id}, ignore_index=True)
    # tempdf = tempdf.append({'spotify_id':artist_id}, ignore_index=True)

    # tempdf = pd.DataFrame({'artist_popularity': artist_popularity, 'spotify_id': 'artist_id'})
    dfs.append(tempdf)
    # time.sleep(1)


masterDF = pd.concat(dfs, ignore_index=True)
masterDF
# Save / update SQL database
# Just keep stuff we are interested in
# met_data3 = masterDF.drop(['index'], axis=1)

artist_data = masterDF

# Save in database
artist_data.to_sql('artist_data', engine, if_exists='replace')

# Close connection
con.close()

# Next --> get song attributes / most popular tracks in an opera!
# Try this out for tracks
track = sp.search(q="nessun dorma", type="track", limit=1)
for i, t in enumerate(track['tracks']['items']):
    track_popularity = (t['popularity'])
    name = (t['name'])
track_popularity
name

# Just getting ones for output
os.chdir("/Users/katelyons/Documents/Insight/figaro/")
predicts = pd.read_csv('met_predictions.csv')

# We have duplicates of operas names in this dataset, let's slim it down!
# All we need are artist scores, so just pull out those and get rid of duplicates
met_operas = predicts.drop_duplicates(subset='opera', keep='first')
met_operas = met_operas[['opera']]
# Fix Götterdammerung and Pelleas et Melisande
met_operas['opera'] = met_operas['opera'].str.replace('Götterdämmerung','Götterdammerung')
met_operas['opera'] = met_operas['opera'].str.replace('Pelléas et Mélisande','Pelléas et Melisande')


# Now have to match this up with our opera aria data
sql_query = """SELECT * FROM opera_info;"""
opera_info = pd.read_sql_query(sql_query,con)
# Want to keep scene_name, opera, act, scene_type, voice
opera_info = opera_info[['scene_name', 'opera', 'act', 'scene_type', 'voice']]
# Ok, now we want to join these, returning all instances that opera_info matches met_operas
df = met_operas.merge(opera_info, how='left', on = 'opera')

# Combine opera name column with scene_name in new track column to have better search results
df['track'] = df['opera'] + " " + df['scene_name']

# Good to keep this for later
season_opera_info = df
season_opera_info.to_sql('season_opera_info', engine, if_exists='replace')

# Track will be our search string
# Looping thru data frame
# Probably a dumb solution but it will work at least -- make column of names in pandas df a list
dfList = df['track'].tolist()

dfs =[]
for track_name in dfList:
    track_results = sp.search(q=track_name, type="track", limit=1)
    if track_results['tracks']['items'] == []:
        continue
    for i, t in enumerate(track_results['tracks']['items']):
        track_popularity = (t['popularity'])
        track_popularity = str(track_popularity)
        name = (t['name'])

    tempdf = pd.DataFrame(columns=['track_popularity', 'name', 'track_name'])
    tempdf = tempdf.append({'track_popularity':track_popularity, 'name':name, 'track_name':track_name}, ignore_index=True)
    # tempdf = tempdf.append({'spotify_id':artist_id}, ignore_index=True)

    # tempdf = pd.DataFrame({'artist_popularity': artist_popularity, 'spotify_id': 'artist_id'})
    dfs.append(tempdf)
    # time.sleep(1)

masterDF = pd.concat(dfs, ignore_index=True)
masterDF

# Save / update SQL database
# Just keep stuff we are interested in
# met_data3 = masterDF.drop(['index'], axis=1)

track_ratings = masterDF
# Save in database
track_ratings.to_sql('track_ratings', engine, if_exists='replace')

# Close connection
con.close()
# Pair this back with original data
# Want to match track_ratings and original df by track_name ... and just keep the operas that are present in track_ratings
df['track_name'] = df['track']
track_ratings2 = track_ratings.merge(df, how='inner', on = 'track_name')
opera_data = track_ratings2[['opera', 'track', 'act', 'scene_type', 'track_popularity']]
opera_data['track_popularity'] = opera_data['track_popularity'].apply(pd.to_numeric)
opera_data = opera_data.sort_values(by = ['opera','track_popularity'], ascending=False)

test = opera_data.groupby('opera').head(5).reset_index(drop=True)
top_tracks = test
top_tracks.to_sql('top_tracks', engine, if_exists='replace')
top_tracks
