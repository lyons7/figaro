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


# Now what we want to do is put a dataframe together of each entry + name (to match up)
# You also want to get the url for each thing so... you are going to commit many CS sins and do an ugly nested for loop because that is all you know how to do right now
