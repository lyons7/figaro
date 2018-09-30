# Get data on pieces and operas themselves
# A lot of help from here: https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3
# And here: https://www.dataquest.io/blog/web-scraping-beautifulsoup/
import requests
from bs4 import BeautifulSoup, NavigableString, Tag, Comment, SoupStrainer
import re
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import time

# Collect and parse first page
page = requests.get('http://www.opera-arias.com/scenes/&page=1#x')
soup = BeautifulSoup(page.text, 'html.parser')

uneven_containers = soup.find_all('div', class_ = 'tr_uneven')
even_containers = soup.find_all('div', class_ = 'tr_even')

# ID
start = even_containers[0]
# As this increases by one, you get all the odd numbers

scene_id = start.find('span', class_='span_s s_id')
scene_id = scene_id.text
scene_id

# Scene name
scene_name = start.a.text
scene_name

# Opera
scene_opera = start.find('span', class_='span_s s_opera')
scene_opera = scene_opera.text
scene_opera

# Composer
scene_composer = start.find('span', class_='span_s s_composer')
scene_composer = scene_composer.text
scene_composer

# Act
scene_act = start.find('span', class_='span_s s_act')
scene_act = scene_act.text
scene_act

# Type
scene_type = start.find('span', class_='span_s s_type')
scene_type = scene_type.text
scene_type

# Voice
scene_voice = start.find('span', class_='span_s s_voice')
scene_voice = scene_voice.text
scene_voice

# Language
scene_language = start.find('span', class_='span_s s_lang')
scene_language = scene_language.text
scene_language

# Role
scene_role = start.find('span', class_='span_s s_role')
scene_role = scene_role.text
scene_role

# ITERATE
# Blatantly stolen from here: https://www.dataquest.io/blog/web-scraping-beautifulsoup/
import requests
from bs4 import BeautifulSoup, NavigableString, Tag, Comment, SoupStrainer
import re
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import time
# To make our scraping seem more like a human, less like a robot
# from time import sleep
# from random import randint

# To help keep the output clean of it updating all of our requests
# from IPython.core.display import clear_output

# To warn you if something is up
# from warnings import warn


# Setting lists to store data in
pages = []
scene_id = []
scene_name = []
opera = []
composer = []
act = []
scene_type = []
voice = []
language = []
role = []

# Let people know who you are so you don't freak them out
dfs = []
headers = {
    'User-Agent': 'Kate Lyons, https://lyons7.github.io/',
    'From': 'k.lyons7@gmail.com'
}

# URL is http://www.opera-arias.com/scenes/&page=1#x
# Goes up to 252, will first do 251 to avoid index error

# To update the page numbers in the crawl
for i in range(1, 252):
    url = 'http://www.opera-arias.com/scenes/&page=' + str(i) + '#x'
    pages.append(url)

# Preparing the monitoring of the loop
#start_time = time()
#requests = 0

# For every year in the interval 2000-2017
for item in pages:
    page = requests.get(item, headers = headers)

    # Pause the loop
    #sleep(randint(8,15))

     # Monitor the requests
    #requests += 1
    #elapsed_time = start_start_time() - start_time
    #print('Request:{}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
    #clear_output(wait = True)

    # Throw a warning for non-200 status codes
    #if response.status_code != 200:
    #    warn('Request: {}; Status code: {}'.format(requests, response.status_code))

    # Break the loop if the number of requests is greater than expected
    #if requests > 72:
     #    warn('Number of requests was greater than expected.')
     #    break

    # Parse the content of the request with BeautifulSoup
    soup = BeautifulSoup(page.text, 'html.parser')

    # Select the thing you are you interested in -- let's do uneven ones first
    for t in range(0, 15):
        uneven_containers = soup.find_all('div', class_ = 'tr_uneven')
        start = uneven_containers[t]
    # Scene ID
    #scene_id1 = start.find('span', class_='span_s s_id')
    #scene_id2 = scene_id1.text
    #scene_id.append(scene_id2)

        # Scene name
        scene_name1 = start.a.text
        scene_name.append(scene_name1)

        #Opera
        scene_opera1 = start.find('span', class_='span_s s_opera')
        scene_opera2 = scene_opera1.text
        opera.append(scene_opera2)

        # Composer
        scene_composer1 = start.find('span', class_='span_s s_composer')
        scene_composer2 = scene_composer1.text
        composer.append(scene_composer2)

        # Act
        scene_act1 = start.find('span', class_='span_s s_act')
        scene_act2 = scene_act1.text
        act.append(scene_act2)

        # Type
        scene_type1 = start.find('span', class_='span_s s_type')
        scene_type2 = scene_type1.text
        scene_type.append(scene_type2)

        # Voice
        scene_voice1 = start.find('span', class_='span_s s_voice')
        scene_voice2 = scene_voice1.text
        voice.append(scene_voice2)

        # Language
        scene_language1 = start.find('span', class_='span_s s_lang')
        scene_language2 = scene_language1.text
        language.append(scene_language2)

        # Role
        scene_role1 = start.find('span', class_='span_s s_role')
        scene_role2 = scene_role1.text
        role.append(scene_role2)

    # Start again with evens
    # Select the thing you are you interested in -- let's do even ones now
    for k in range(0, 15):
        even_containers = soup.find_all('div', class_ = 'tr_even')
        start2 = even_containers[k]
    # Scene ID
    #scene_id3 = start2.find('span', class_='span_s s_id')
    #scene_id4 = scene_id3.text
    #scene_id.append(scene_id4)

        # Scene name
        scene_name2 = start2.a.text
        scene_name.append(scene_name2)

        #Opera
        scene_opera3 = start2.find('span', class_='span_s s_opera')
        scene_opera4 = scene_opera3.text
        opera.append(scene_opera4)

        # Composer
        scene_composer3 = start2.find('span', class_='span_s s_composer')
        scene_composer4 = scene_composer3.text
        composer.append(scene_composer4)

        # Act
        scene_act3 = start2.find('span', class_='span_s s_act')
        scene_act4 = scene_act3.text
        act.append(scene_act4)

        # Type
        scene_type3 = start2.find('span', class_='span_s s_type')
        scene_type4 = scene_type3.text
        scene_type.append(scene_type4)

        # Voice
        scene_voice3 = start2.find('span', class_='span_s s_voice')
        scene_voice4 = scene_voice3.text
        voice.append(scene_voice4)

        # Language
        scene_language3 = start2.find('span', class_='span_s s_lang')
        scene_language4 = scene_language3.text
        language.append(scene_language4)

        # Role
        scene_role3 = start2.find('span', class_='span_s s_role')
        scene_role4 = scene_role3.text
        role.append(scene_role4)

# Get last page with less than 30 entries
url = 'http://www.opera-arias.com/scenes/&page=252#x'
page = requests.get(url, headers = headers)
soup = BeautifulSoup(page.text, 'html.parser')
for t in range(0, 9):
    uneven_containers = soup.find_all('div', class_ = 'tr_uneven')
    start = uneven_containers[t]

    # Scene name
    scene_name1 = start.a.text
    scene_name.append(scene_name1)

    #Opera
    scene_opera1 = start.find('span', class_='span_s s_opera')
    scene_opera2 = scene_opera1.text
    opera.append(scene_opera2)

    # Composer
    scene_composer1 = start.find('span', class_='span_s s_composer')
    scene_composer2 = scene_composer1.text
    composer.append(scene_composer2)

    # Act
    scene_act1 = start.find('span', class_='span_s s_act')
    scene_act2 = scene_act1.text
    act.append(scene_act2)

    # Type
    scene_type1 = start.find('span', class_='span_s s_type')
    scene_type2 = scene_type1.text
    scene_type.append(scene_type2)

    # Voice
    scene_voice1 = start.find('span', class_='span_s s_voice')
    scene_voice2 = scene_voice1.text
    voice.append(scene_voice2)

    # Language
    scene_language1 = start.find('span', class_='span_s s_lang')
    scene_language2 = scene_language1.text
    language.append(scene_language2)

    # Role
    scene_role1 = start.find('span', class_='span_s s_role')
    scene_role2 = scene_role1.text
    role.append(scene_role2)

    # Start again with evens
    # Select the thing you are you interested in -- let's do even ones now
for k in range(0, 8):
    even_containers = soup.find_all('div', class_ = 'tr_even')
    start2 = even_containers[k]

    # Scene name
    scene_name2 = start2.a.text
    scene_name.append(scene_name2)

    #Opera
    scene_opera3 = start2.find('span', class_='span_s s_opera')
    scene_opera4 = scene_opera3.text
    opera.append(scene_opera4)

    # Composer
    scene_composer3 = start2.find('span', class_='span_s s_composer')
    scene_composer4 = scene_composer3.text
    composer.append(scene_composer4)

    # Act
    scene_act3 = start2.find('span', class_='span_s s_act')
    scene_act4 = scene_act3.text
    act.append(scene_act4)

    # Type
    scene_type3 = start2.find('span', class_='span_s s_type')
    scene_type4 = scene_type3.text
    scene_type.append(scene_type4)

    # Voice
    scene_voice3 = start2.find('span', class_='span_s s_voice')
    scene_voice4 = scene_voice3.text
    voice.append(scene_voice4)

    # Language
    scene_language3 = start2.find('span', class_='span_s s_lang')
    scene_language4 = scene_language3.text
    language.append(scene_language4)

    # Role
    scene_role3 = start2.find('span', class_='span_s s_role')
    scene_role4 = scene_role3.text
    role.append(scene_role4)

# Fix opera naming convention so it is closer to Met Archive version
# Help from here: https://stackoverflow.com/questions/15704943/switch-lastname-firstname-to-firstname-lastname-inside-list
opera2 = [" ".join(n.split(", ")[::-1]) for n in opera]

# Now we want to put everything everything together
opera_info = pd.DataFrame({'scene_name': scene_name,
                           'opera': opera2,
                           'composer': composer,
                           'act': act,
                           'scene_type': scene_type,
                           'voice': voice,
                           'language': language,
                           'role': role})
#print(opera_info.info())
# opera_info

# Put this in our database
os.chdir("/Users/katelyons/Documents/Insight/figaro/data")
from sql import dbname, username

## 'engine' is a connection to a database
## Here, we're using postgres, but sqlalchemy can connect to other things too.
engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))
print(engine.url)

# Connect to make queries using psycopg2
con = None
con = psycopg2.connect(database = dbname, user = username)

opera_info.to_sql('opera_info', engine, if_exists='replace')
