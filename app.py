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
    # for x in cos_sims:
    #     print (x)
        # Now we have to input all of this additional information ...

    #for my app the recommender gives an image of the florist and a link
    # opera_info = {
    # 'Adriana_Lecouvreur1':
    #     {'name':'Adriana Lecouvreur', 'date':'December 31, 2018', 'composer':'Cilea', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15133#/'},
    # 'Adriana_Lecouvreur2':
    #     {'name':'Adriana Lecouvreur', 'date':'January 4, 2019', 'composer':'Cilea', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15134#/'},
    # 'Adriana_Lecouvreur3':
    #     {'name':'Adriana Lecouvreur', 'date':'January 8, 2019', 'composer':'Cilea', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15135#/'},
    # 'Adriana_Lecouvreur4':
    #     {'name':'Adriana Lecouvreur', 'date':'January 12, 2019', 'composer':'Cilea', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15136#/'},
    # 'Adriana_Lecouvreur5':
    #     {'name':'Adriana Lecouvreur', 'date':'January 16, 2019', 'composer':'Cilea', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15137#/'},
    # 'Adriana_Lecouvreur6':
    #     {'name':'Adriana Lecouvreur', 'date':'January 19, 2019', 'composer':'Cilea', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15138#/'},
    # 'Adriana_Lecouvreur7':
    #     {'name':'Adriana Lecouvreur', 'date':'January 23, 2019', 'composer':'Cilea', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15139#/'},
    # 'Adriana_Lecouvreur8':
    #     {'name':'Adriana Lecouvreur', 'date':'January 26, 2019', 'composer':'Cilea', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15140#/'},
    # 'Aida1':
    #     {'name':'Aida', 'date':'September 26, 2018', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15142'},
    # 'Aida2':
    #     {'name':'Aida', 'date':'September 29, 2018', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15143'},
    # 'Aida3':
    #     {'name':'Aida', 'date':'October 2, 2018', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15144'},
    # 'Aida4':
    #     {'name':'Aida', 'date':'October 6, 2018', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15145'},
    # 'Aida5':
    #     {'name':'Aida', 'date':'October 11, 2018', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15146'},
    # 'Aida6':
    #     {'name':'Aida', 'date':'October 15, 2018', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15147'},
    # 'Aida7':
    #     {'name':'Aida', 'date':'October 18, 2018', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15148'},
    # 'Aida8':
    #     {'name':'Aida', 'date':'January 7, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15149'},
    # 'Aida9':
    #     {'name':'Aida', 'date':'January 11, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15150'},
    # 'Aida10':
    #     {'name':'Aida', 'date':'January 14, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15151'},
    # 'Aida11':
    #     {'name':'Aida', 'date':'January 18, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15152'},
    # 'Aida12':
    #     {'name':'Aida', 'date':'February 28, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15153'},
    # 'Aida13':
    #     {'name':'Aida', 'date':'March 4, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15154'},
    # 'Aida14':
    #     {'name':'Aida', 'date':'March 7, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/errors/restricted-access-messaging/?perf=15155'},
    # 'Carmen1':
    #     {'name':'Carmen', 'date':'October 30, 2018', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15191#/'},
    # 'Carmen2':
    #     {'name':'Carmen', 'date':'November 3, 2018', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15192#/'},
    # 'Carmen3':
    #     {'name':'Carmen', 'date':'November 6, 2018', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15193#/'},
    # 'Carmen4':
    #     {'name':'Carmen', 'date':'November 10, 2018', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15194#/'},
    # 'Carmen5':
    #     {'name':'Carmen', 'date':'November 15, 2018', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15195#/'},
    # 'Carmen6':
    #     {'name':'Carmen', 'date':'January 9, 2019', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15196#/'},
    # 'Carmen7':
    #     {'name':'Carmen', 'date':'January 12, 2019', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15197#/'},
    # 'Carmen8':
    #     {'name':'Carmen', 'date':'January 17, 2019', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15198#/'},
    # 'Carmen9':
    #     {'name':'Carmen', 'date':'January 21, 2019', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15199#/'},
    # 'Carmen10':
    #     {'name':'Carmen', 'date':'January 26, 2019', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15200#/'},
    # 'Carmen11':
    #     {'name':'Carmen', 'date':'January 29, 2019', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15201#/'},
    # 'Carmen12':
    #     {'name':'Carmen', 'date':'February 2, 2019', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15202#/'},
    # 'Carmen13':
    #     {'name':'Carmen', 'date':'February 5, 2019', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15203#/'},
    # 'Carmen14':
    #     {'name':'Carmen', 'date':'February 8, 2019', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15204#/'},
    # 'Carmen15':
    #     {'name':'Carmen', 'date':'January 12, 2019', 'composer':'Bizet', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15197#/'},
    # 'Das_Rheingold1':
    #     {'name':'Das Rheingold', 'date':'March 14, 2019', 'composer':'Wagner', 'link':'https://www.metopera.org/season/reserve/date-comparison/?perf=15307'},
    # 'Dialogues_Carmelites1':
    #     {'name':'Dialogues des Carmélites', 'date':'May 3, 2019', 'composer':'Poulenc', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15186#/'},
    # 'Dialogues_Carmelites2':
    #     {'name':'Dialogues des Carmélites', 'date':'May 8, 2019', 'composer':'Poulenc', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15187#/'},
    # 'Dialogues_Carmelites3':
    #     {'name':'Dialogues des Carmélites', 'date':'May 11, 2019', 'composer':'Poulenc', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15188#/'},
    # 'Die_Walküre1':
    #     {'name':'Die Walküre', 'date':'March 25, 2019', 'composer':'Wagner', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15380#/'},
    # 'Die_Walküre2':
    #     {'name':'Die Walküre', 'date':'March 30, 2019', 'composer':'Wagner', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15381#/'},
    # 'Die_Walküre3':
    #     {'name':'Die Walküre', 'date':'April 25, 2019', 'composer':'Wagner', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15382#/'},
    # 'Die_Walküre4':
    #     {'name':'Die Walküre', 'date':'April 30, 2019', 'composer':'Wagner', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15383#/'},
    # 'Die_Walküre5':
    #     {'name':'Die Walküre', 'date':'May 7, 2019', 'composer':'Wagner', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15384#/'},
    # 'Die_Walküre3':
    #     {'name':'Die Walküre', 'date':'April 25, 2019', 'composer':'Wagner', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15385#/'},
    # 'Die_Zauberflöte1':
    #     {'name':'Die Zauberflöte', 'date':'December 19, 2018', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15232#/'},
    # 'Die_Zauberflöte2':
    #     {'name':'Die Zauberflöte', 'date':'December 22, 2018', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15233#/'},
    # 'Die_Zauberflöte3':
    #     {'name':'Die Zauberflöte', 'date':'December 24, 2018', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15234#/'},
    # 'Die_Zauberflöte4':
    #     {'name':'Die Zauberflöte', 'date':'December 27, 2018', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15235#/'},
    # 'Die_Zauberflöte5':
    #     {'name':'Die Zauberflöte', 'date':'December 29, 2018', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15236#/'},
    # 'Die_Zauberflöte6':
    #     {'name':'Die Zauberflöte', 'date':'January 1, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15237#/'},
    # 'Die_Zauberflöte7':
    #     {'name':'Die Zauberflöte', 'date':'January 3, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15238#/'},
    # 'Die_Zauberflöte8':
    #     {'name':'Die Zauberflöte', 'date':'January 5, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15239#/'},
    # 'Don_Giovanni1':
    #     {'name':'Don Giovanni', 'date':'January 30, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15242#/'},
    # 'Don_Giovanni2':
    #     {'name':'Don Giovanni', 'date':'February 2, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15243#/'},
    # 'Don_Giovanni3':
    #     {'name':'Don Giovanni', 'date':'February 6, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15244#/'},
    # 'Don_Giovanni4':
    #     {'name':'Don Giovanni', 'date':'February 9, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15245#/'},
    # 'Don_Giovanni5':
    #     {'name':'Don Giovanni', 'date':'February 13, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15246#/'},
    # 'Don_Giovanni6':
    #     {'name':'Don Giovanni', 'date':'February 16, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15247#/'},
    # 'Don_Giovanni7':
    #     {'name':'Don Giovanni', 'date':'February 20, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15248#/'},
    # 'Don_Giovanni8':
    #     {'name':'Don Giovanni', 'date':'April 4, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15249#/'},
    # 'Don_Giovanni9':
    #     {'name':'Don Giovanni', 'date':'April 9, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15250#/'},
    # 'Don_Giovanni10':
    #     {'name':'Don Giovanni', 'date':'April 12, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15251#/'},
    # 'Don_Giovanni11':
    #     {'name':'Don Giovanni', 'date':'April 15, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15252#/'},
    # 'Don_Giovanni12':
    #     {'name':'Don Giovanni', 'date':'April 18, 2019', 'composer':'Mozart', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15253#/'},
    # 'Falstaff1':
    #     {'name':'Falstaff', 'date':'February 22, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15206#/'},
    # 'Falstaff2':
    #     {'name':'Falstaff', 'date':'February 27, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15207#/'},
    # 'Falstaff3':
    #     {'name':'Falstaff', 'date':'March 2, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15208#/'},
    # 'Falstaff4':
    #     {'name':'Falstaff', 'date':'March 5, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15209#/'},
    # 'Falstaff5':
    #     {'name':'Falstaff', 'date':'March 8, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15210#/'},
    # 'Falstaff6':
    #     {'name':'Falstaff', 'date':'March 12, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15211#/'},
    # 'Falstaff7':
    #     {'name':'Falstaff', 'date':'March 16, 2019', 'composer':'Verdi', 'link':'https://www.metopera.org/smart-seat/?performanceNumber=15212#/'},
    # 'Götterdämmerung1':
    #     {'name':'Götterdämmerung', 'date':'May 4, 2019', 'composer':'Wagner', 'link':'https://www.metopera.org/season/tickets/the-ring-cycle/ring-cycle/'},
    # 'Götterdämmerung2':
    #     {'name':'Götterdämmerung', 'date':'May 11, 2019', 'composer':'Wagner', 'link':'https://www.metopera.org/season/tickets/the-ring-cycle/ring-cycle/'},
    # #START HERE




































        #
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
        #

        #arguments are whatever comes out of your app, in my case a cos_sim and the recommended florist
        #the structure is render_template('your_html_file.html', x=x, y=y, etc...)
        #refer to my recommendations.html to see how variables work
    return render_template('recommendations.html', selection = selection, opera_info = opera_info)

    # return render_template('recommendations.html', cos_sims = cos_sims, florist_info = florist_info)

# To have a favicon image in some browsers
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

if __name__ == '__main__':
    #this runs your app locally
    app.run(host='0.0.0.0', port=8080, debug=True)
