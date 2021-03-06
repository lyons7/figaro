from flask import Flask, render_template, request, send_from_directory
import requests
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.metrics import jaccard_similarity_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import StandardScaler
# pd.options.display.max_columns=25
import distance
import datetime
import csv

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

#After they submit the survey, the recommender page redirects to recommendations.html
@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    # Turn month number into phrase
    predicts = pd.read_csv('met_predictions.csv')
    # Just work with performances that are happening today and onwards
    predicts['date1']  = pd.to_datetime(predicts['date1'])
    predicts = predicts[predicts.date1 >= datetime.datetime.now()]
    predicts['month']  = pd.to_datetime(predicts['date1'])
    predicts['month'] = predicts['month'].dt.strftime('%B')

    # Capitalize somethings
    predicts['ending'] = predicts.ending.str.title()
    # predicts

    # Put input from user into some kind of format
    ending = str(request.form['ending'])
    kid = str(request.form['kid'])
    length = int(request.form['length'])
    composer = str(request.form['composer'])
    language = str(request.form['language'])
    story = str(request.form['story'])
    month = str(request.form['month'])

    # To test if this works
    # ending = str('Happy')
    # kid = int('0')
    # length = int(160)
    # composer = str('')
    # language = str('Italian')
    # story = str('')
    # month = str('January')
    #230
    if length == 230:
        length = ''
    else:
        # Have to fix length so that it fits in a category
        # Help from here: https://stackoverflow.com/questions/30112202/how-do-i-find-the-closest-values-in-a-pandas-series-to-an-input-number
        times = predicts['length']
        times = pd.DataFrame(times).reset_index()
        times = times[['length']]

        times_sort = times.iloc[(times['length']-length).abs().argsort()[:1]]
        length = times_sort['length'].tolist()
        length = int(length[0])

    new_df = pd.DataFrame({'ending':[ending],'kid':[kid],'length':[length], 'composer':[composer], 'language':[language], 'story':[story], 'month':[month]})
    # new_df = pd.DataFrame({'ending':[ending],'kid':[kid], 'composer':[composer], 'language':[language], 'story':[story], 'month':[month]})

    # Start figuring out recommendation process
    new_list1 = new_df.values.tolist()
    new_list=new_list1[0]

    special = predicts[['ending','kid','length','composer','language','story','month']]
    # special = predicts[['ending','kid','composer','language','story','month']]
    predict_list = special.values.tolist()
    # Test how this works
    # gruf = predict_list[1]
    # gruf
    # test = 200.0 * len(set(gruf) & set(new_list)) / (len(gruf) + len(new_list))

    # sm=difflib.SequenceMatcher(None,gruf, new_list)

    # Get scores
    sim_score=[]
    for i in predict_list:
        sim_score1 = jaccard_similarity_score(i, new_list, normalize=False)
        sim_score.append(str(sim_score1))

    # Put these back with original df
    se = pd.Series(sim_score)
    predicts['sim_score'] = se.values
    reco = predicts.sort_values(by=['sim_score', 'popularity_predictions'])
    reco = reco.reindex()
    cos_sims1 = reco.opera.tail(3)
    selection = cos_sims1.values.tolist()


    # Setting up dictionary of values that will print out for the user:
    # Help from here: https://stackoverflow.com/questions/11102326/python-csv-to-nested-dictionary
    delimiter = ','
    opera_info = {}
    with open("met_predictions.csv", 'r') as data_file:
        data = csv.reader(data_file, delimiter=delimiter)
        headers = next(data)[1:] # month names starting from 2nd column in csv
        for row in data:
            temp_dict = {}
            name = row[0]
            values = []
            # converting each value from string to int / float
            # (as suggested by OP's example)
            for x in row[1:]:
                try:
                    values.append(x)
                except ValueError:
                    try:
                        values.append(int(x))
                    except ValueError:
                        print("Skipping value '{}' that cannot be converted " +
                              "to a number - see following row: {}"
                              .format(x, delimiter.join(row)))
                        values.append(0)
            for i in range(len(values)):
                if values[i]: # exclude 0 values
                    temp_dict[headers[i]] = values[i]
            opera_info[name] = temp_dict

        # Do same for youtube links and scene info
        # Will add wiki info later
    delimiter = ','
    top_scenes = {}
    with open("top_scenes.csv", 'r') as data_file:
        data = csv.reader(data_file, delimiter=delimiter)
        headers = next(data)[1:] # month names starting from 2nd column in csv
        for row in data:
            temp_dict = {}
            name = row[0]
            values = []
                # converting each value from string to int / float
                # (as suggested by OP's example)
            for x in row[1:]:
                try:
                    values.append(x)
                except ValueError:
                    try:
                        values.append(int(x))
                    except ValueError:
                        print("Skipping value '{}' that cannot be converted " +
                              "to a number - see following row: {}"
                              .format(x, delimiter.join(row)))
                        values.append(0)
            for i in range(len(values)):
                if values[i]: # exclude 0 values
                    temp_dict[headers[i]] = values[i]
            top_scenes[name] = temp_dict

        #arguments are whatever comes out of your app, in my case a cos_sim and the recommended florist
        #the structure is render_template('your_html_file.html', x=x, y=y, etc...)
        #refer to my recommendations.html to see how variables work
    return render_template('recommendations.html', selection = selection, opera_info = opera_info, top_scenes=top_scenes)

    # return render_template('recommendations.html', cos_sims = cos_sims, florist_info = florist_info)

# To have a favicon image in some browsers
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

if __name__ == '__main__':
    #this runs your app locally
    app.run(host='0.0.0.0', port=8080, debug=True)
