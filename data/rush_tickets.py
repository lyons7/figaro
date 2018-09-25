# Update: was able to get stuff from Wayback Machine -- we'll now feed in those html files and for each one grab information we need
# We have html of every wayback archive of a particular url, but in nested folders
# This command 'walks' through those folders to access each html file
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import re
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import time
import os

# Figure out how to get stuff that we want
os.getcwd()
os.chdir('/Users/katelyons/Documents/Insight/figaro/data')
HtmlFile = open('index.html', 'r', encoding='utf-8')
source_code = HtmlFile.read()

soup = BeautifulSoup(source_code, 'html.parser')

# Figure out how to isolate aspects of page
movie_containers = html_soup.find_all('div', class_ = 'lister-item mode-advanced')

spans = soup.find('')



lines = [span.get_text() for span in spans]
lines


# At the end make sure to close
HtmlFile.close

# Slowly figure out how to identify price
# Help from here: https://stackoverflow.com/questions/16248723/how-to-find-spans-with-a-specific-class-containing-specific-text-using-beautiful
spans = soup.find_all('span', class_ = 'purchase-btn-price')
lines = [span.get_text() for span in spans]
# Check if this worked
# lines[0]
price = re.sub('\D', '', str(lines[1]))
price

# Date
scripts = soup.find_all('script')
page_date = re.sub('\D', '', str(scripts[3]))
page_date

# Opera
opera = soup.find('title')
opera = re.sub('\\n', '', opera.text)
opera2 = re.sub('\\t', '', opera)
opera2



file = open('index.html', 'r')

for root, dirs, files in os.walk(/Users/katelyons/Downloads/rush):
    for name in files:
        if name.endswith((".html", ".htm")):
            file = open("test.html", "r")
