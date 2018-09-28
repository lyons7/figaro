from flask import Flask, render_template, request
import requests
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.metrics import jaccard_similarity_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import StandardScaler
pd.options.display.max_columns=25
import os
import distance
import datetime
import difflib

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

#After they submit the survey, the recommender page redirects to recommendations.html
@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    # Turn month number into phrase
    predicts = pd.read_csv('met_predictions.csv')
    predicts['month']  = pd.to_datetime(predicts['month'])
    predicts['month'] = predicts['month'].dt.strftime('%B')

    # Capitalize somethings
    predicts['ending'] = predicts.ending.str.title()
    predicts

    # Put input from user into some kind of format
    ending = str(request.form['ending'])
    kid = str(request.form['kid'])
    # length = int(request.form['length'])
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

    # new_df = pd.DataFrame({'ending':[ending],'kid':[kid],'length':[length], 'composer':[composer], 'language':[language], 'story':[story], 'month':[month]})
    new_df = pd.DataFrame({'ending':[ending],'kid':[kid], 'composer':[composer], 'language':[language], 'story':[story], 'month':[month]})

    # Start figuring out recommendation process
    new_list1 = new_df.values.tolist()
    new_list=new_list1[0]

    # special = predicts[['ending','kid','length','composer','language','story','month']]
    special = predicts[['ending','kid','composer','language','story','month']]
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
    reco = predicts.sort_values(['sim_score', 'popularity_predictions'])
    cos_sims1 = reco.tail(1)
    cos_sims = cos_sims1.values.tolist()
    # cos_sims
    # for x in cos_sims:
    #     print (x)
        # Now we have to input all of this additional information ...

        #for my app the recommender gives an image of the florist and a link
        # florist_info = {
        # 'Flora_by_Nora':
        #     {'name':'Flora by Nora', 'img_src':'/static/img/flora_by_nora.png', 'link':'https://www.florabynora.com/'},
        # 'Madelyn_Claire_Floral_Design_&_Events':
        #     {'name':'Madlyn Claire Floral Design', 'img_src':'/static/img/madelyn_claire.png', 'link':'https://madelynclairefloraldesign.com/'},
        # 'Little_Shop_of_Floral':
        #     {'name':'Little Shop of Floral', 'img_src':'/static/img/little_shop_of_floral.png', 'link':'https://www.littleshopoffloral.com/'},
        # 'Lumme_Creations':
        #     {'name':'Lumme Creations', 'img_src':'/static/img/lumme.png', 'link':'https://www.lummecreations.com/'},
        # 'Rooted':
        #     {'name':'Rooted Floral and Design', 'img_src':'/static/img/rooted.png', 'link':'https://www.rootedfloralanddesign.com/'},
        # 'Blush_&_Bay':
        #     {'name':'Blush and Bay', 'img_src':'/static/img/blush_and_bay.png', 'link':'http://www.blushandbay.com/'}}


        #arguments are whatever comes out of your app, in my case a cos_sim and the recommended florist
        #the structure is render_template('your_html_file.html', x=x, y=y, etc...)
        #refer to my recommendations.html to see how variables work
    return render_template('recommendations.html', cos_sims = cos_sims)

    # return render_template('recommendations.html', cos_sims = cos_sims, florist_info = florist_info)


if __name__ == '__main__':
    #this runs your app locally
    app.run(host='0.0.0.0', port=8080, debug=True)
