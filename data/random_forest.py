# Trying out Random Forests model with popularity data
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
%matplotlib inline
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 30, 15
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2

# Get data and put in data frame from SQL database
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
# What we are doing here is saying give me everything from the artist data set that matches up with artist entries in the Met Archives -- if there is no match, return NAs
sql_query = """SELECT met_archive.*, artist_data.artist_popularity, artist_data.spotify_id FROM met_archive LEFT JOIN artist_data ON met_archive.artist = artist_data.artist;"""
data = pd.read_sql_query(sql_query,con)
data
# To see if it worked
# data

# Want to collapse by opera and not have artist data atm
# Popularity score
data['artist_popularity'] = data['artist_popularity'].astype(str).astype(int)

# Collapse these
data = data.groupby(['date'],as_index=False).agg({'artist_popularity': 'sum'})

# Make date date
data['date']  = pd.to_datetime(data['date'])
