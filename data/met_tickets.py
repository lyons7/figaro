
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import re
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import time


# Collect page on one performance
page = requests.get('https://web.archive.org/web/20170928060212/https://www.metopera.org/Season/2017-18-Season/zauberflote-mozart-tickets/')
# Create a BeautifulSoup object
soup = BeautifulSoup(page.text, 'html.parser')

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


# For later this will be useful!
# URL composition of web archive stuff: 'https://web.archive.org/web', '20170928060212', 'www.metopera.org'
