'''
Created on Jan 29, 2014

@author:  Tea Kolevska
@contact: tea.kolevska@zhaw.ch
@organization: ICCLab, Zurich University of Applied Sciences

'''

import ceilometer_api
import compute_api
import keystone_api
import textwrap
import httplib2 as http
import sys, re
import json
from collections import namedtuple
import sqlite3

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
    


conn = sqlite3.connect('meters.db')

print "Opened database successfully";

#conn.execute('''CREATE TABLE METERS_COUNTER
#       (ID INT PRIMARY KEY     NOT NULL,
#      METER_NAME TEXT NOT NULL,
#       RESOURCE_ID TEXT  NOT NULL,
#       COUNTER_VOLUME TEXT NOT NULL,
#       UNIT TEXT NOT NULL,
#       TIMESTAMP DATETIME NOT NULL);''')
#print "Table created successfully";

conn.execute('''CREATE TABLE PRICE_FUNC
       (ID INT PRIMARY KEY     NOT NULL,
       PRICE REAL NOT NULL,
       TIMESTAMP DATETIME NOT NULL);''')
print "Table created successfully";


conn.commit()
print "Records created successfully";

conn.close()