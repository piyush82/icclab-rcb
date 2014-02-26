'''
Created on Feb 5, 2014

@author:  Tea Kolevska
@contact: tea.kolevska@zhaw.ch
@organization: ICCLab, Zurich University of Applied Sciences
@summary: Initialize the database.

'''
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'os_api')))
import ceilometer_api
import compute_api
import keystone_api
import textwrap
import sqlite3
import json
import logging


path=(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'logs')))
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.FileHandler(path+'/init.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def main(argv):
    global logger
    
    #if database doesnt exist, create it
    if not os.path.isfile('meters.db'):
        logger.info('Creating database')

        conn = sqlite3.connect('meters.db')
        create_tables(conn)        
        conn.close()
    #if database exists, check if tables match the original, if not, drop all tables and create them again   
    else:
        conn = sqlite3.connect('meters.db')
        logger.info('The database exists')

        all=[]
        default=["meters_counter","pricing_func","users","units","price_loop","udr","price_cdr","price_daily"]
        logger.info('Opened database successfully')

        count=conn.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table'  AND name != 'sqlite_sequence'")
        for i in count:
            total=i[0]

        tables=conn.execute("SELECT * FROM sqlite_master WHERE type = 'table'  AND name != 'sqlite_sequence'")
        for i in tables:        
            all.append(i[2])

    
        for i in range(len(all)):
            all[i]=all[i].lower()     

        pom = json.dumps(all)
        pom=pom.translate(None,'"[] " "')
        pom=pom.split(",")
        all=pom

        x=set(all)

        y=set(default)

        if x!=y:
            for i in range(len(all)):
                conn.execute("DROP TABLE "+str(all[i])) 
            create_tables(conn)
            logger.info('Drop all tables')
            
            logger.info('Records created  successfully')


        conn.close()    
            
def create_tables(conn):    
        global logger        
        conn.execute('''CREATE TABLE METERS_COUNTER
           (ID INT PRIMARY KEY  NOT NULL,
           METER_ID TEXT NOT NULL,
           METER_NAME TEXT NOT NULL,
           USER_ID TEXT NOT NULL,
           RESOURCE_ID TEXT  NOT NULL,
           COUNTER_VOLUME TEXT NOT NULL,
           UNIT TEXT NOT NULL,
           TIMESTAMP DATETIME NOT NULL,
           TENANT_ID TEXT NOT NULL);''')
        logger.info('Table created successfully')

        conn.execute('''CREATE TABLE PRICE_LOOP
           (ID INT PRIMARY KEY  NOT NULL,
           PRICE REAL NOT NULL,
           TIMESTAMP DATETIME NOT NULL,
           TENANT_ID TEXT NOT NULL);''')
        logger.info('Table created successfully')

        conn.execute('''CREATE TABLE PRICING_FUNC
           (ID INTEGER PRIMARY KEY AUTOINCREMENT,
           USER_ID TEXT NOT NULL,
           PARAM1 TEXT,
           SIGN1 TEXT,
           PARAM2 TEXT,
           SIGN2 TEXT,
           PARAM3 TEXT,
           SIGN3 TEXT,
           PARAM4 TEXT,
           SIGN4 TEXT,
           PARAM5 TEXT);''')
        logger.info('Table created successfully')

        conn.execute('''CREATE TABLE UNITS
           (ID INTEGER PRIMARY KEY,
           METER_NAME TEXT NOT NULL,
           METER_TYPE TEXT NOT NULL,
           METER_UNIT TEXT NOT NULL);''')
        logger.info('Table created successfully')

        conn.execute('''CREATE TABLE USERS
           (ID INT PRIMARY KEY  NOT NULL,
           USER_ID TEXT NOT NULL,
           TENANT_ID TEXT NOT NULL);''')
        logger.info('Table created successfully')
        
        conn.execute('''CREATE TABLE UDR
           (ID INTEGER PRIMARY KEY AUTOINCREMENT,
           USER_ID TEXT NOT NULL,
           TIMESTAMP DATETIME NOT NULL,
           PRICING_FUNC_ID INT NOT NULL,
           PARAM1 TEXT,
           PARAM2 TEXT,
           PARAM3 TEXT,
           PARAM4 TEXT,
           PARAM5 TEXT,
           FOREIGN KEY(PRICING_FUNC_ID) REFERENCES PRICING_FUNC(ID));''')
        logger.info('Table created successfully')      
        
        conn.execute('''CREATE TABLE PRICE_CDR
           (ID INTEGER PRIMARY KEY AUTOINCREMENT,
           PRICE REAL,
           TIMESTAMP DATETIME NOT NULL,
           TENANT_ID TEXT NOT NULL,
           PRICING_FUNC_ID INT NOT NULL,
           FOREIGN KEY(PRICING_FUNC_ID) REFERENCES PRICING_FUNC(ID));''')
        logger.info('Table created successfully')     
        
        conn.execute('''CREATE TABLE PRICE_DAILY
           (ID INTEGER PRIMARY KEY AUTOINCREMENT,
           PRICE REAL,
           TIMESTAMP DATETIME NOT NULL,
           TENANT_ID TEXT NOT NULL,
           PRICING_FUNC_ID INT NOT NULL,
           FOREIGN KEY(PRICING_FUNC_ID) REFERENCES PRICING_FUNC(ID));''')
        logger.info('Table created successfully')               

        conn.commit()
        return True
                      






    
if __name__ == '__main__':
    main(sys.argv[1:])  