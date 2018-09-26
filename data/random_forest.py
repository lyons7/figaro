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
# Load scikit's random forest classifier library
from sklearn.ensemble import RandomForestClassifier
# Set random seed
np.random.seed(0)
import datetime
from time import gmtime, strftime
from sklearn.model_selection import train_test_split


# Get data and put in data frame from SQL database
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
# What we are doing here is saying give me everything from the artist data set that matches up with artist entries in the Met Archives -- if there is no match, return NAs
sql_query = """SELECT met_archive.*, artist_data.artist_popularity, artist_data.spotify_id FROM met_archive LEFT JOIN artist_data ON met_archive.artist = artist_data.artist;"""
data = pd.read_sql_query(sql_query,con)
data
# To see if it worked
# data

# Deal with NAs --> need to turn them into 0s?

# Also bring in opera-arias.com data: composer & language. This will be a left join so you can get rid of the ones that don't have anything.
sql_query = """SELECT opera_info.opera, opera_info.composer, opera_info.language FROM opera_info;"""
opera_info = pd.read_sql_query(sql_query,con)
opera_info = opera_info.drop_duplicates()
opera_info
# put these together
# Have to clean
data['opera'] = data['opera'].str.strip()
df = data.merge(opera_info, how='left', on = 'opera')

# Get columns we want:
df = df[['role','opera', 'artist', 'date', 'CID', 'artist_popularity', 'composer', 'language']]
# Want to collapse by opera and not have artist data atm
# Get rid of entries we have no info for
df = df.dropna()
# Popularity score
df['artist_popularity'] = df['artist_popularity'].astype(str).astype(int)

# Collapse these
df = df.groupby(['date', 'opera', 'language', 'composer'],as_index=False).agg({'artist_popularity': 'sum'})

# Make date date
df['date']  = pd.to_datetime(df['date'])

# Get day of the week
df['day_of_week'] = df['date'].dt.day_name()

# Get week number (how far along are we in the year?)
df['week'] = df['date'].dt.strftime('%V')
# Make sure this is an integer
df['week'] = df['week'].astype(str).astype(int)

# Start modeling process
# A lot of help from here: https://towardsdatascience.com/random-forest-in-python-24d0893d51c0
# For all of our categorical variables (day of the week, opera, language, composer) we have to do one-hot encoding
# One-hot encode the data using pandas get_dummies
features = pd.get_dummies(df)

# Labels are the values we want to predict
labels = np.array(features['artist_popularity'])
# Remove the labels from the features
# axis 1 refers to the columns
features= features.drop('artist_popularity', axis = 1)
features= features.drop('date', axis = 1)

# Saving feature names for later use
feature_list = list(features.columns)
# Convert to numpy array
features = np.array(features)

# Using Skicit-learn to split data into training and testing sets
# Split the data into training and testing sets
train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.25, random_state = 42)

# Import the model we are using
from sklearn.ensemble import RandomForestRegressor
# Instantiate model with 1000 decision trees
rf = RandomForestRegressor(n_estimators = 1000, random_state = 42)
# Train the model on training data
rf.fit(train_features, train_labels);

# Use the forest's predict method on the test data
predictions = rf.predict(test_features)
# Calculate the absolute errors
errors = abs(predictions - test_labels)
# Print out the mean absolute error (mae)
print('Mean Absolute Error:', round(np.mean(errors), 2), 'points.')

# Calculate mean absolute percentage error (MAPE)
mape = 100 * (errors / test_labels)
# Calculate and display accuracy
accuracy = 100 - np.mean(mape)
print('Accuracy:', round(accuracy, 2), '%.')

# Get numerical feature importances
importances = list(rf.feature_importances_)
# List of tuples with variable and importance
feature_importances = [(feature, round(importance, 2)) for feature, importance in zip(feature_list, importances)]
# Sort the feature importances by most important first
feature_importances = sorted(feature_importances, key = lambda x: x[1], reverse = True)
# Print out the feature and importances
[print('Variable: {:20} Importance: {}'.format(*pair)) for pair in feature_importances];


# Set the style
plt.style.use('fivethirtyeight')
# list of x locations for plotting
x_values = list(range(len(importances)))
# Make a bar chart
plt.bar(x_values, importances, orientation = 'vertical')
# Tick labels for x axis
plt.xticks(x_values, feature_list, rotation='vertical')
# Axis labels and title
plt.ylabel('Importance'); plt.xlabel('Variable'); plt.title('Variable Importances');
