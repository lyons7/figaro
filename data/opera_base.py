import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import re
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import time
import os
import random
from bs4 import UnicodeDammit
import difflib

# Collect page on one performance
page = requests.get('http://operabase.com/a2list.cgi?lang=en&name=isabel+leonard&soundex=on&majorS=')
# Create a BeautifulSoup object
soup = BeautifulSoup(page.text, 'html.parser')


# Slowly figure out how to identify price
# Help from here: https://stackoverflow.com/questions/16248723/how-to-find-spans-with-a-specific-class-containing-specific-text-using-beautiful
spans = soup.find_all('span')

artist = re.sub('<[^>]+>', '', str(spans[0]))
artist = re.sub('\\xa0', '', str(artist))
artist = re.sub('Artists', '', str(artist))
artist = artist.strip()
# artist

perf_record = re.sub('<[^>]+>', '', str(spans[2]))
perf_record = re.sub('\([^)]*\)', '', str(perf_record))
perf_record = re.sub('\D', '', str(perf_record))
# perf_record

# Performance locations
# Figured out image tags for festivals and opera houses are consistent, we can count those
place = []
urls = ['/pix/icons/ens.gif', '/pix/icons/festival.gif']
pics = soup.find_all('img')
for pic in pics:
    if pic['src'] not in urls:
        continue
    place1 = pic['src']
    place.append(str(place1))
place
houses = len(place)

# Iterate
# Get artist data from database
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

# To search them in URLs --> do all lowercase and replace spaces with pluses
met_data['artist'] = met_data['artist'].str.lower()
met_data['artist'] = met_data['artist'].str.replace('*', '')
met_data['artist'] = met_data['artist'].str.strip()
met_data['artist'] = met_data['artist'].str.replace(' ', '+')
artist_names = met_data['artist'].tolist()
# artist_names

# Great! Now we have a list of names properly formatted, we just want to feed it in to a loop where we extract info. Let's do a small subset just to play around and test
# test = random.sample(artist_names, 50)

# Iterate
pages = []
name = []
perf_record =[]
houses = []

headers = {'User-Agent': 'Kate Lyons, https://lyons7.github.io/', 'From': 'k.lyons7@gmail.com'}

for i in artist_names:
    url = 'http://operabase.com/a2list.cgi?lang=en&name=' + i + '&soundex=on&majorS='
    pages.append(url)

for item in pages:
    page = requests.get(item, headers = headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    # Get artist name
    spans = soup.find_all('span')
    try:
        artist = re.sub('<[^>]+>', '', str(spans[0]))
    except IndexError:
        continue
    artist = re.sub('\\xa0', '', str(artist))
    artist = re.sub('Artists', '', str(artist))
    artist = artist.strip()
    if artist == '':
        continue
    name.append(artist)

    # Get number of performances
    perf_record1 = re.sub('<[^>]+>', '', str(spans[2]))
    perf_record1 = re.sub('\([^)]*\)', '', str(perf_record1))
    perf_record1 = re.sub('\D', '', str(perf_record1))
    perf_record.append(perf_record1)

    # Get number of houses
    place = []
    urls = ['/pix/icons/ens.gif', '/pix/icons/festival.gif']
    pics = soup.find_all('img')
    for pic in pics:
        if pic['src'] not in urls:
            continue
        place1 = pic['src']
        place.append(str(place1))
    houses1 = len(place)
    houses.append(houses1)

perf_record = pd.DataFrame({'artist': name,
                           'perf_record': perf_record,
                           'houses': houses})
perf_record

# Get rid of columns with no information
result = perf_record[~perf_record['artist'].str.contains(": PRO ARTIST")]
perf_record = result
perf_record
# Save in database
perf_record.to_sql('perf_record', engine, if_exists='replace')

# Close connection
con.close()

# Putting this all together and making a total score...
sql_query = """SELECT * FROM artist_data;"""
spotify_data = pd.read_sql_query(sql_query,con)
spotify_data = spotify_data[['artist','artist_popularity']]

sql_query = """SELECT * FROM perf_record;"""
perf_data = pd.read_sql_query(sql_query,con)
perf_data = perf_data[['artist','houses']]

# Rank each one...
# From smallest to greatest
spotify_data[['artist_popularity']] = spotify_data[['artist_popularity']].apply(pd.to_numeric)
spot = spotify_data.sort_values(by=['artist_popularity'])
spot = spot.drop_duplicates('artist')

perf_data[['houses']] = perf_data[['houses']].apply(pd.to_numeric)
perf = perf_data.sort_values(['houses'])
perf = perf.drop_duplicates('artist')

# Add a new column from 0 or 1 up to each to constitute rank
# Help from here: https://stackoverflow.com/questions/38862293/how-to-add-incremental-numbers-to-a-new-column-using-pandas
spot = spot.reset_index()
spot['spotify_rank'] = spot.index + 0

perf = perf.reset_index()
perf['house_rank'] = perf.index + 0

# Now combine these together
# Want to do... a full join to get everything
# Also have to do a fuzzy join of sorts because of different formatting...
# Help from here: https://stackoverflow.com/questions/13636848/is-it-possible-to-do-fuzzy-match-merge-with-python-pandas
# For later
copy = perf.copy()

copy.artist = copy.artist.map(lambda x: difflib.get_close_matches(x, spot.artist))
copy['artist'] = copy['artist'].str[0]
copy['artist2'] = perf['artist']

# Get back ones we lost
# Help from here: https://stackoverflow.com/questions/29177498/python-pandas-replace-nan-in-one-column-with-value-from-corresponding-row-of-sec
copy.artist.fillna(copy.artist2, inplace=True)
del copy['artist2']
copy

rankings = spot.merge(copy, how='outer', on = 'artist')
rankings = rankings[['artist','spotify_rank','house_rank']]
# Turn NaNs to 0s
rankings = rankings.fillna(0)

rankings['popularity_score'] = rankings['spotify_rank'] + rankings['house_rank']
# rankings.sort_values(by=['popularity_score'])


# Export to SQL database
# Get rid of columns with no information
rankings = rankings[['artist','popularity_score']]

# Also just keep ones with higher popularity scores if there are duplicates
# Help from here: https://stackoverflow.com/questions/33423582/pandas-keep-duplicated-with-highest-value
rankings = rankings.sort_values(['popularity_score'])
rankings = rankings.drop_duplicates('artist', keep='first')
# rankings
# Save in database
rankings.to_sql('rankings', engine, if_exists='replace')
# rankings.sort_values(by=['popularity_score'])
# Close connection
con.close()
