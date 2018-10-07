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
import os


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
sql_query = """SELECT met_archive.*, rankings.popularity_score FROM met_archive LEFT JOIN rankings ON met_archive.artist = rankings.artist;"""
data = pd.read_sql_query(sql_query,con)

# Deal with NAs --> need to turn them into 0s?

# Also bring in opera-arias.com data: composer & language. This will be a left join so you can get rid of the ones that don't have anything.
sql_query = """SELECT opera_info.opera, opera_info.composer, opera_info.language FROM opera_info;"""
opera_info = pd.read_sql_query(sql_query,con)
opera_info = opera_info.drop_duplicates()
# opera_info
# put these together
# Have to clean
data['opera'] = data['opera'].str.strip()
df = data.merge(opera_info, how='left', on = 'opera')

# test = df[df['opera'].str.contains("Le Nozze di Figato")]

# Get columns we want:
df = df[['role','opera', 'artist', 'date', 'CID', 'popularity_score', 'composer', 'language']]
# Want to collapse by opera and not have artist data atm
# Get rid of entries we have no info for
df = df.dropna()
# Popularity score
# df['popularity_score'] = df['popularity_score'].astype(str).astype(int)

# Collapse these
df = df.groupby(['date', 'opera', 'language', 'composer'],as_index=False).agg({'popularity_score': 'sum'})

# Make date date
df['date']  = pd.to_datetime(df['date'])

# Get day of the week
df['day_of_week'] = df['date'].dt.day_name()

# Get week number (how far along are we in the year?)
df['week'] = df['date'].dt.strftime('%V')
# Make sure this is an integer
df['week'] = df['week'].astype(str).astype(int)

# Get year and month as well
df['year'],df['month'] = df.date.dt.year, df.date.dt.month

# Start modeling process
# A lot of help from here: https://towardsdatascience.com/random-forest-in-python-24d0893d51c0
# For all of our categorical variables (day of the week, opera, language, composer) we have to do one-hot encoding
# One-hot encode the data using pandas get_dummies
features = pd.get_dummies(df)

# Labels are the values we want to predict
labels = np.array(features['popularity_score'])
# Remove the labels from the features
# axis 1 refers to the columns
features= features.drop('popularity_score', axis = 1)
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


# Use datetime for creating date objects for plotting
import datetime
# Dates of training values
months = features[:, feature_list.index('month')]
years = features[:, feature_list.index('year')]
# List and then convert to datetime object
dates = [str(int(year)) + '-' + str(int(month)) for year, month in zip(years, months)]
dates = [datetime.datetime.strptime(date, '%Y-%m') for date in dates]
# Dataframe with true values and dates
true_data = pd.DataFrame(data = {'date': dates, 'actual': labels})
# Dates of predictions
months = test_features[:, feature_list.index('month')]
years = test_features[:, feature_list.index('year')]
# Column of dates
test_dates = [str(int(year)) + '-' + str(int(month)) for year, month in zip(years, months)]
# Convert to datetime objects
test_dates = [datetime.datetime.strptime(date, '%Y-%m') for date in test_dates]
# Dataframe with predictions and dates
predictions_data = pd.DataFrame(data = {'date': test_dates, 'prediction': predictions})
# Plot the actual values
plt.plot(true_data['date'], true_data['actual'], 'b-', label = 'actual')
# Plot the predicted values
plt.plot(predictions_data['date'], predictions_data['prediction'], 'ro', label = 'prediction')
plt.xticks(rotation = '60');
plt.legend()
# Graph labels
plt.xlabel('Date'); plt.ylabel('Popularity Score'); plt.title('Actual and Predicted Values');


# How to use a model to predict new stuff:
# https://stackoverflow.com/questions/44026832/valueerror-number-of-features-of-the-model-must-match-the-input
# prepare the pipeline

# Or could we do something like...
# Load in new data
sql_query = """SELECT * FROM new_season;"""
new_season = pd.read_sql_query(sql_query,con)

# Make sure this is in the same format as the training / test data
new_season['opera'] = new_season['opera'].str.strip()
new_season = new_season.drop('index', axis = 1)

# Fix date, get weeks and days of the week
# Make date date
new_season['date']  = pd.to_datetime(new_season['date'])

# Get day of the week
new_season['day_of_week'] = new_season['date'].dt.day_name()

# Get week number (how far along are we in the year?)
new_season['week'] = new_season['date'].dt.strftime('%V')

# Empty popularity column
new_season["popularity_score"] = 0
# Make sure this is an integer
new_season['week'] = new_season['week'].astype(str).astype(int)

# Get year and month as well
new_season['year'],new_season['month'] = new_season.date.dt.year, new_season.date.dt.month

new_season = new_season.drop('date', axis = 1)

# Concatenate the data
old_season = df.drop('date', axis = 1)
old_season['label'] = 'train'
new_season['label'] = 'score'
# old_season['popularity_score'] = old_season['popularity_score'].astype(str).astype(int)

concat_df = pd.concat([old_season , new_season], sort=True)
# concat_df


# Create your dummies

new_features = pd.get_dummies(concat_df)

# Split your data
train_df = new_features[new_features['label_train'] == 1]
score_df = new_features[new_features['label_score'] == 1]
# print(train_df.columns.tolist())

# Drop your labels
train_df = train_df.drop('label_train', axis=1)
train_df = train_df.drop('label_score', axis=1)
score_df = score_df.drop('label_score', axis=1)
score_df = score_df.drop('label_train', axis=1)

# Start again
# Labels are the values we want to predict
labels = np.array(train_df['popularity_score'])
# Remove the labels from the features
# axis 1 refers to the columns
train_df= train_df.drop('popularity_score', axis = 1)

# Saving feature names for later use
train_df_list = list(train_df.columns)
# Convert to numpy array
train_df = np.array(train_df)

# Using Skicit-learn to split data into training and testing sets
# Split the data into training and testing sets
train_features, test_features, train_labels, test_labels = train_test_split(train_df, labels, test_size = 0.25, random_state = 42)

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

# NOW PREDICT ON ACTUAL SCORES
# You have to do to score df the same stuff to get it into an array
score_df1= score_df.drop('popularity_score', axis = 1)
score_df_test = np.array(score_df1)
predictions = rf.predict(score_df_test)
new_season["popularity_predictions"] = predictions
# new_season

# Sort from highest to lowest
new_season.sort_values('popularity_predictions')
new_season.to_csv('met_predictions2.csv')

con.close()
