import urllib.request
import urllib.parse
import re
import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import difflib
import pandas as pd
def print_full(x):
    pd.set_option('display.max_rows', len(x))
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.float_format', '{:20,.2f}'.format)
    pd.set_option('display.max_colwidth', -1)
    print(x)
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')
# Get most popular Youtube videos for top 5 tracks per opera

# First bring in our track data
os.chdir("/Users/katelyons/Documents/Insight/figaro/data")
from sql import dbname, username

engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))
print(engine.url)

# Connect to make queries using psycopg2
con = None
con = psycopg2.connect(database = dbname, user = username)

# query:
sql_query = """SELECT * FROM top_tracks;"""
top_tracks = pd.read_sql_query(sql_query,con)
# print_full(top_tracks)
# Now put this in a for loop of code from here: https://www.codeproject.com/Articles/873060/Python-Search-Youtube-for-Video
dfList = top_tracks['track'].tolist()
dfs =[]
for track in dfList:
    query_string = urllib.parse.urlencode({"search_query" : track})
    html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
    youtube_link = "http://www.youtube.com/watch?v=" + search_results[0]

    tempdf = pd.DataFrame(columns=['track', 'youtube_link'])
    tempdf = tempdf.append({'track':track, 'youtube_link':youtube_link}, ignore_index=True)

    dfs.append(tempdf)

youtube = pd.concat(dfs, ignore_index=True)
youtube

# Put this together with track data
opera_recs = top_tracks.merge(youtube, how = "outer", on = "track")
opera_recs

# Save this to SQL
# Save in database
opera_recs.to_sql('youtube_links', engine, if_exists='replace')
opera_recs.to_csv('opera_recs.csv')

# Close connection
con.close()

# So now we have to organize things a bit for our website output
# Want to have rows of track 1, track 2, track 3, track 4, track 5: top 5 most popular scenes from this opera
# First we want to just get the scene name because maybe not that pretty to have opera name + track name
# To do that we have to go back to our spotify data...
# Get data
sql_query = """SELECT * FROM season_opera_info;"""
season_operas = pd.read_sql_query(sql_query,con)

# Just keep stuff we will work with
merge = opera_recs[['track','track_popularity','youtube_link']]
season_operas = season_operas.merge(merge, how = "outer", on="track")
season_operas = season_operas.dropna()
print_full(season_operas)

# To make things easier later on
season_operas = season_operas.rename(index=str, columns={"opera": "opera3"})
season_operas = season_operas[['opera3', 'scene_name', 'act', 'scene_type', 'voice', 'track', 'track_popularity', 'youtube_link']]
season_operas = season_operas.sort_values(by=['opera3','track_popularity'], ascending=False)

# Now we are grouping things by the things we want to have columns of
season_operas['count'] = season_operas.groupby('opera3').cumcount() + 1
season_operas['count']=season_operas['count'].apply(str)
season_operas['term'] = "track"
season_operas['term_2'] = "youtube"
season_operas['term_3'] = "act"
season_operas['track_no'] = season_operas['term'] + "_" + season_operas['count']
season_operas['link_no'] = season_operas['term_2'] + "_" + season_operas['count']
season_operas['act_no'] = season_operas['term_3'] + "_" + season_operas['count']
season_operas = season_operas.reset_index()

season_operas = season_operas[['track_no', 'link_no', 'act_no', 'opera3', 'scene_name', 'act', 'scene_type','voice', 'track_popularity', 'youtube_link']]
season_tracks = season_operas.pivot(index='opera3', columns='track_no', values='scene_name').reset_index()
season_links = season_operas.pivot(index='opera3', columns='link_no', values='youtube_link').reset_index()
season_scenes = season_operas.pivot(index='opera3', columns='act_no', values='act').reset_index()

# We can't just drop data we don't have because html output wont like that...
season_tracks = season_tracks.fillna(" ")
season_links = season_links.fillna(" ")
season_scenes = season_scenes.fillna(" ")

# Combine this with our met_data.csv and save it !
os.chdir("/Users/katelyons/Documents/Insight/figaro")
predicts = pd.read_csv('met_predictions.csv')
top_scenes = predicts.merge(season_tracks, how = "left", on="opera3")
top_scenes = top_scenes.merge(season_links, how = "left", on="opera3")
top_scenes = top_scenes.merge(season_scenes, how = "left", on = "opera3")
top_scenes = top_scenes.fillna(" ")
# Save this
top_scenes = top_scenes[['opera1', 'track_1', 'track_2', 'track_3', 'track_4', 'track_5','youtube_1', 'youtube_2', 'youtube_3', 'youtube_4', 'youtube_5', 'act_1', 'act_2', 'act_3', 'act_4', 'act_5']]
print_full(top_scenes)
top_scenes.to_csv('top_scenes.csv')
