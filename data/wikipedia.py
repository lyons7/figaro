import wikipedia
import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import difflib
import pandas as pd

wikipedia.summary("Falstaff opera")

falstaff = wikipedia.page("Falstaff opera")
falstaff.url


# Put this all together
# Get data from Met predictions
os.chdir("/Users/katelyons/Documents/Insight/figaro")
predicts = pd.read_csv('met_predictions.csv')
predicts['term'] = "opera"
predicts['search_term'] = predicts['opera3'] + " " + predicts['term']

# Now what we want to do is put a dataframe together of each entry + name (to match up)
# You also want to get the url for each thing so... you are going to commit many CS sins and do an ugly nested for loop because that is all you know how to do right now
dfList = predicts['search_term'].tolist()
dfs =[]
for search_term in dfList:
    summary = wikipedia.summary(search_term)
    page = wikipedia.page(search_term)
    wiki_link = page.url

    tempdf = pd.DataFrame(columns=['search_term', 'summary', 'wiki_link'])
    tempdf = tempdf.append({'search_term':search_term, 'summary':summary, 'wiki_link':wiki_link}, ignore_index=True)

    dfs.append(tempdf)

wikipedia_df = pd.concat(dfs, ignore_index=True)
wikipedia_df

# Put this together with opera data
wiki_data = predicts.merge(wikipedia_df, how = "outer", on = "search_term")
wiki_data.columns
wiki_data = wikipedia_df[['summary','wiki_link']]
wiki_data.to_csv('wiki_data.csv')


# Have to do some individual ones bc of weird Met practices
# Il Trittico and Iolanta

dfList = ['bartok bluebeards castle opera', 'il tabarro', 'suor angelica','gianni schicchi','il trittico']
dfs =[]
for search_term in dfList:
    summary = wikipedia.summary(search_term)
    page = wikipedia.page(search_term)
    wiki_link = page.url

    tempdf = pd.DataFrame(columns=['search_term', 'summary', 'wiki_link'])
    tempdf = tempdf.append({'search_term':search_term, 'summary':summary, 'wiki_link':wiki_link}, ignore_index=True)

    dfs.append(tempdf)

wikipedia_df = pd.concat(dfs, ignore_index=True)

wikipedia_df.to_csv('backups.csv')
