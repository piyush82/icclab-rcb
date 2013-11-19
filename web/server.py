############################################################
#@author: Piyush Harsh (piyush.harsh@zhaw.ch)
#@version: 0.1
#@summary: Module implementing RCB Restful Web Interface
#
#@requires: bottle
############################################################

from bottle import get, post, request, route, run, response
import ConfigParser
import sqlite3 as db
import sys, getopt
import web_ui
import worker
import config

#list of database tables, this list is used to do DB sanity check whenever needed
dbtables = ['user', 'project', 'session']

def startServer(host, port):
    print 'Starting a simple REST server.'
    run(host=host, port=port)
    print 'Interrupt caught. Server stopped.'

def checkdbconsistency(dbpath):
    print 'Starting the consistency check: ' + dbpath
    con = None
    try:
        con = db.connect(dbpath)
        cur = con.cursor()
        cur.execute('SELECT SQLITE_VERSION()')
        data = cur.fetchone()
        print "INFO: SQLite version: %s" % data
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tlist = cur.fetchall()
        print "The count of tables found: %d" % len(tlist)
        if len(tlist) == len(dbtables):
            for tname in tlist:
                if tname[0] not in dbtables:
                    print 'The table ' + tname + ' was not found in the control list!'
                    return False
        else:
            print 'DB is inconsistent.'
            return False
    except db.Error, e:
        print 'Error %s:' % e.args[0]
        sys.exit(1)
    finally:
        if con:
            con.close()
    print 'DB is consistent!\n'
    return True

def initializedb(dbpath):
    print 'Initializing the database: ' + dbpath
    con = None
    try:
        con = db.connect(dbpath)
        cur = con.cursor()
        cur.executescript('''
            DROP TABLE IF EXISTS user;
            CREATE TABLE user(id INT, username VARCHAR(45), password VARCHAR(128), cookiekey VARCHAR(128), email VARCHAR(128), isactive INT);
            DROP TABLE IF EXISTS project;
            CREATE TABLE project(id INT, name VARCHAR(45), userid INT, cfile TEXT);
            DROP TABLE IF EXISTS session;
            CREATE TABLE session(id INT, userid INT, taccess INT, projectid INT, isvalid INT);
        ''')
        con.commit()
    except db.Error, e:
        print 'Error %s:' % e.args[0]
        sys.exit(1)
    finally:
        if con:
            con.close()
    return True

def main(argv):
    confFile = None
    try:
        opts, args = getopt.getopt(argv, "hc:i", "config=")
    except getopt.GetoptError:
        print 'server.py -c <configfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'server.py -c <configfile> [-i]'
            print 'To initialize a configuration file: use switch -i'
            sys.exit()
        elif opt in ("-c", "--config"):
            confFile = arg     
    Config = ConfigParser.ConfigParser()
    for opt, arg in opts:
        if opt == '-i':
            if confFile != None:
                cfgfile = open(confFile,'w')
                Config.add_section('Server')
                Config.add_section('Database')
                Config.set('Server', 'Port', 8080)
                Config.set('Database', 'File', 'rcb.db')
                Config.set('Database', 'Driver', 'sqlite')
                Config.write(cfgfile)
                cfgfile.close()
                print 'New configuration file has been created. Change the parameters as needed and start the program with -c flag.'
                sys.exit()
            else:
                print 'Please specify the configuration file name. Use -c flag when using -i option.'
                sys.exit(2)
    if confFile == None:
        Config.read("/Users/harh/Codes/ZHAW/Eclipse/workspace/icclab-rcb/config.ini")
    else:
        Config.read(confFile)
    dbPath = Config.get("Database", "File")

    config.dbPath = dbPath
    
    #Now performing sanitaion checks on the database
    dbtest = checkdbconsistency(dbPath)
    dbinitstatus = True
    if dbtest != True:
        dbinitstatus = initializedb(dbPath)
    serverPort = Config.get("Server", "Port")
    if dbinitstatus != False:
        print "Starting the ICCLab RCB Online Service\n"
        startServer('localhost', serverPort)
    else:
        print 'DB is not consistent, and it could not be initialized properly!'

if __name__ == "__main__":
    main(sys.argv[1:])

