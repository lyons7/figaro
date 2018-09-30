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
import dateutil.parser



# Figure out how to get stuff that we want
os.getcwd()
os.chdir('/Users/katelyons/Downloads/rush/20151024054825/www.metopera.org/Season/Tickets/Rush-Page/')
HtmlFile = open('index.html', 'r', encoding='utf-8')
source_code = HtmlFile.read()

soup = BeautifulSoup(source_code, 'html.parser')
soup
# Figure out how to isolate aspects of page

# Date of scraping
scripts = soup.find_all('script')
page_date = re.sub('\D', '', str(scripts[3]))
page_date = page_date[:-8]
page_date = datetime.strptime(page_date, "%Y%m%d").date()
page_date

# Date of performance
perf_date = soup.find('p', class_ = 'performance-list-day-text')
perf_date = re.sub('<[^>]+>', '', str(perf_date))
perf_date = re.sub('\\n', '', str(perf_date))
perf_date = str.strip(perf_date)
perf_date = datetime.strptime(perf_date, "%a, %b %d").strftime("%m-%d")
perf_date

# Availability
avail = soup.find('div', class_ = 'performance-list-performance-purchase force-show-btn')
avail = re.sub('<[^>]+>', '', str(avail))
avail = re.sub('\\n', '', str(avail))
avail

# At the end make sure to close
HtmlFile.close()



# Iterate!
page_date = []
perf_date = []
avail = []
# We know this works I think, just have to get the iteration part down...

for entry in os.scandir('/Users/katelyons/Downloads/rush/'):
    try:
        HtmlFile = open('index.html', 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        soup = BeautifulSoup(source_code, 'html.parser')

    except entry.is_dir():
        continue

    # Date of performance
        perf_date1 = soup.find('p', class_ = 'performance-list-day-text')
        perf_date2 = re.sub('<[^>]+>', '', str(perf_date1))
        perf_date3 = re.sub('\\n', '', str(perf_date2))
        perf_date4 = str.strip(perf_date3)
        perf_date5 = datetime.strptime(perf_date4, "%a, %b %d").strftime("%m-%d")
        perf_date.append(str(perf_date5))


        # Date of scraping
        scripts = soup.find_all('script')
        page_date1 = re.sub('\D', '', str(scripts[3]))
        page_date2 = page_date1[:-8]
        page_date3 = datetime.strptime(page_date2, "%Y%m%d").date()
        page_date.append(str(page_date3))

        # Availability
        avail1 = soup.find('div', class_ = 'performance-list-performance-purchase force-show-btn')
        avail2 = re.sub('<[^>]+>', '', str(avail1))
        avail3 = re.sub('\\n', '', str(avail2))
        avail.append(avail3)
        HtmlFile.close()

rush_data = pd.DataFrame({'page_date': page_date,'perf_date': perf_date,'avail': avail})

rush_data
