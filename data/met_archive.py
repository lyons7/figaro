import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import re
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import time

# First try to do one at a time to see what labels info we want is stored under

# Collect page on one performance
page = requests.get('http://69.18.170.204/archives/scripts/cgiip.exe/WService=BibSpeed/fullcit.w?xCID=130000&limit=5000&xBranch=ALL&xsdate=08/01/1940&xedate=09/01/2018&theterm=&x=0&xhomepath=&xhome=')

# Create a BeautifulSoup object
soup = BeautifulSoup(page.text, 'html.parser')

# Can be illustrative to look at data directly
# soup

# Get opera info (which is outside of weird text block)
tag = soup.find("cite")
opera = str(tag)
opera2 = re.sub('<.*?>', '', opera)
opera3 = re.sub('{.*?}','', opera2)
opera3

# Just gets ALL the text
test = soup.get_text('<br/>', strip=False)
test = "\n".join(test.split("<br/>"))
# type(test)
# print(test)

# Extract the date out of the text
match = re.search(r'\d{2}/\d{1,2}/\d{4}', test)
date = datetime.strptime(match.group(), '%m/%d/%Y').date()
print (date)

# Make the string a list so we can manipulate it
def Convert(string):
    li = list(string.split("\n"))
    return li

test2 = Convert(test)
# print(test2)

# Roles
roles = [k for k in test2 if '...' in k and 'Director' not in k and 'Conductor' not in k and 'Set designer' not in k and 'Costume designer' not in k and 'Dance' not in k and 'Choreographer' not in k]
roles2 = [i.split('.', 1)[0] for i in roles]
roles2

# Just get performers step 1
performers = [k for k in test2 if '...' in k and 'Director' not in k and 'Conductor' not in k and 'Set designer' not in k and 'Costume designer' not in k and 'Dance' not in k and 'Choreographer' not in k]
performers
# Have to add on to this because the Met changes how these roles are called

#Have to figure out a way to just get everything after the last dot... perhaps some help from here: https://stackoverflow.com/questions/26665265/regex-to-find-text-after-period
# Get rid of character names
performers2 = [i.split('.', 1)[1] for i in performers]
performers3 = [re.sub(r'\.', '', i) for i in performers2]
performers4 = [re.sub(r' \[Debut\]', '', i) for i in performers3]
performers4

# Extract the CID for reference
CID = [k for k in test2 if 'CID' in k]
CID2 = [re.sub(r'CID:', '', i) for i in CID]
CID3 = [re.sub(r'\[Met Performance\] ', '', i) for i in CID2]
CID3 = str(CID3)

# Create a data frame where we have performers connected to the date and CID and opera name
# Test
df = pd.DataFrame({'artists':performers4})
# Add values to list
df['CID'] = CID3
df['opera'] = opera
df['date'] = date
print(df)

# Ok, now we have a series of commands we can use on each url to get the information that we want... how do we do it iteratively?
