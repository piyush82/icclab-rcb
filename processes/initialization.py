'''
Created on Feb 5, 2014

@author:  Tea Kolevska
@contact: tea.kolevska@zhaw.ch
@organization: ICCLab, Zurich University of Applied Sciences

'''
import sys
sys.path.append('/home/kolv/workspace/icc-lab-master/os_api')
import ceilometer_api
import compute_api
import keystone_api
import textwrap
import sqlite3
import json
import os

def main(argv):
    
    if not os.path.isfile('meters.db'):
        print "Creating database"
        conn = sqlite3.connect('meters.db')
        create_tables(conn)
        
        conn.close()
    else:
        conn = sqlite3.connect('meters.db')
        print "The database exists"
        all=[]
        default=["meters_counter","pricing_func","users","units","price_loop"]
        print "Opened database successfully"
        count=conn.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name != 'android_metadata' AND name != 'sqlite_sequence'")
        for i in count:
            total=i[0]
        print total
        tables=conn.execute("SELECT * FROM sqlite_master WHERE type = 'table' AND name != 'android_metadata' AND name != 'sqlite_sequence'")
        for i in tables:        
            all.append(i[2])
        print all
    
        for i in range(len(all)):
            all[i]=all[i].lower()     

        pom = json.dumps(all)
        pom=pom.translate(None,'"[] " "')
        pom=pom.split(",")
        all=pom
        print all 
        x=set(all)
        print x
        y=set(default)
        print y
        if x!=y:
            for i in range(len(all)):
                conn.execute("DROP TABLE "+str(all[i])) 
                create_tables(conn)
            
            print "Records created successfully";

        conn.close()    
            
def create_tables(conn):            
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
        print "Table created successfully"
        conn.execute('''CREATE TABLE PRICE_LOOP
           (ID INT PRIMARY KEY  NOT NULL,
           PRICE REAL NOT NULL,
           TIMESTAMP DATETIME NOT NULL,
           TENANT_ID TEXT NOT NULL);''')
        print "Table created successfully"
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
        print "Table created successfully" 
        conn.execute('''CREATE TABLE UNITS
           (ID INTEGER PRIMARY KEY,
           METER_NAME TEXT NOT NULL,
           METER_TYPE TEXT NOT NULL,
           METER_UNIT TEXT NOT NULL);''')
        print "Table created successfully"
        conn.execute('''CREATE TABLE USERS
           (ID INT PRIMARY KEY  NOT NULL,
           USER_ID TEXT NOT NULL,
           TENANT_ID TEXT NOT NULL);''')
        print "Table created successfully"
        conn.commit()
        return True
                      






    
if __name__ == '__main__':
    main(sys.argv[1:])  