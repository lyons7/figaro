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
