# Putting everything together

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import datetime

# Define a database name
# Set your postgres username
dbname = 'figaro'
username = 'katelyons' # change this to your username

## 'engine' is a connection to a database
## Here, we're using postgres, but sqlalchemy can connect to other things too.
engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))
print(engine.url)

# Connect to make queries using psycopg2
con = None
con = psycopg2.connect(database = dbname, user = username)

# Example query for specific stuff:
# query:
#sql_query = """
#SELECT * FROM met_archive WHERE opera ='Le Nozze di Figaro ';
#"""

# Start with combining all Met Archive files
sql_ma_one = """SELECT * FROM met_archive_one;"""
ma_one = pd.read_sql_query(sql_ma_one,con)
ma_one

sql_ma_two = """SELECT * FROM met_archive_two;"""
ma_two = pd.read_sql_query(sql_ma_two,con)
ma_two

sql_ma_three = """SELECT * FROM met_archive_three;"""
ma_three = pd.read_sql_query(sql_ma_three,con)
ma_three

sql_ma_four = """SELECT * FROM met_archive_four;"""
ma_four = pd.read_sql_query(sql_ma_four,con)
ma_four

sql_ma_five = """SELECT * FROM met_archive_five;"""
ma_five = pd.read_sql_query(sql_ma_five,con)
ma_five

sql_ma_six = """SELECT * FROM met_archive_six;"""
ma_six = pd.read_sql_query(sql_ma_six,con)
ma_six

sql_ma_seven = """SELECT * FROM met_archive_seven;"""
ma_seven = pd.read_sql_query(sql_ma_seven,con)
ma_seven

sql_ma_eight = """SELECT * FROM met_archive_eight;"""
ma_eight = pd.read_sql_query(sql_ma_eight,con)
ma_eight

sql_ma_nine = """SELECT * FROM met_archive_nine;"""
ma_nine = pd.read_sql_query(sql_ma_nine,con)
ma_nine

sql_ma_ten = """SELECT * FROM met_archive_ten;"""
ma_ten = pd.read_sql_query(sql_ma_ten,con)
ma_ten

sql_ma_eleven = """SELECT * FROM met_archive_eleven;"""
ma_eleven = pd.read_sql_query(sql_ma_eleven,con)
ma_eleven

# Combine everything together
frames = [ma_one, ma_two, ma_three, ma_four, ma_five, ma_six, ma_seven, ma_eight, ma_nine, ma_ten, ma_eleven]
result = pd.concat(frames)
result = result.sort_values(by=['date', 'opera'])
result

# Get performances we are interested if __name__ == '__main__':
result = result[result['CID'].str.contains("Performance")]
result


# print(result.to_string())

# Just get stuff past... 2007?
# First get columns we want
met_2007_2018 = result[['role','opera', 'artist', 'date', 'CID']]

# Just get stuff past 2006
# Help from here: https://stackoverflow.com/questions/22898824/filtering-pandas-dataframes-on-dates
met_2007_2018 = met_2007_2018[(met_2007_2018['date']>datetime.date(2007,9,1))]
# Get rid of buggy stuff that might mess up spotify
met_2007_2018 = met_2007_2018[~met_2007_2018['role'].str.contains("\"")]
met_2007_2018 = met_2007_2018.reset_index(drop=True)
met_2007_2018

# Save this in our SQL database
met_2007_2018.to_sql('met_archive', engine, if_exists='replace')

# Play around a bit
sql_query = """SELECT * FROM met_archive WHERE artist ='Juan Diego Flórez';"""

# Start with combining all Met Archive files
play = pd.read_sql_query(sql_query,con)
play
