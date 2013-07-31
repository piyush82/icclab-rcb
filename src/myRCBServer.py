############################################################
#@author: Piyush Harsh (piyush.harsh@zhaw.ch)
#@version: 0.1
#@summary: Module implementing RCB Rest Interface
#
#
############################################################
from bottle import get, post, request, route, run, response
import ConfigParser
import sqlite3 as db
import sys, getopt

#list of database tables, this list is used to do DB sanity check whenever needed
dbtables = ['user', 'project', 'session']

@get('/rcb/web/')
def index():
    response.set_header('Content-Language', 'en')
    response.set_header('Content-Type', 'text/html')
    content = '''
        <div style='padding:5px;width:700px;margin-left:auto;margin-right:auto;font-family:Helvetica;font-size:10pt;background:#4A4F65;color:white;'>
        <h3>Welcome to <a style='color:#8BACD7;' href='http://www.cloudcomp.ch/' target='_blank'>ICCLab</a>'s OpenCharge&trade; Platform!</h3>
        
        <i>OpenCharge&trade;</i> is a one of its kind - fully generic rating, charging, and billing platform designed to fully support
        any generic business process your company supports. You have full control over how you manage customer usage data collection, 
        mediation strategies, rating, charging, pricing and billing configuration. The platform supports special promotions, discounts
        and refunds in your overall billing functions.<br><br>
        
        <form action="/rcb/login" method="post" style='background:#6D8AB1;padding:5px;'>
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            <input value="Login" type="submit" />
        </form>
        
        <b>Salient Features:</b>
        <ul>
            <li>Support for OpenStack Grizzly Release</li>
            <li>REST API for seamless integration with your service
            <li>Customizable Analytics Module
            <li>OpenSource Licensing
        </ul>
        
        <br>
    '''
    return header() + content + footer() + '</div>'

def footer():
    content = '''
    <table style='margin:0px;background:#C3CAD3;font-color:#80858B;font-family:Verdana;font-size:8pt;width:700px;text-align:left;'>
        <tr>
            <td style='width:300px;background:white;'><img src='http://www.cloudcomp.ch/wp-content/uploads/2012/05/icclogo-left-300x86.png'></td>
            <td style='border-style:dashed;border-right-width:1px;border-left-width:0px;border-top-width:0px;border-bottom-width:0px;border-color:black;' valign='top'>
                <a style='color:black;text-decoration:none;' href='http://www.cloudcomp.ch/research/foundation/themes/initiatives/rating-charging-billing/' target='_blank'>ICCLab RCB Initiative</a><br>
                <a style='color:black;text-decoration:none;' href='javascript:void(0);' target='_blank'>Open Source License</a><br>
                <a style='color:black;text-decoration:none;' href='javascript:void(0);' target='_blank'>Development Team</a><br>
                <a style='color:black;text-decoration:none;' href='javascript:void(0);' target='_blank'>Mobile Cloud Networking</a><br>
                <a style='color:black;text-decoration:none;' href='javascript:void(0);' target='_blank'>Design Specs</a>
            </td>
            <td style='' valign='top'>
                <a style='color:black;text-decoration:none;' href='http://www.cloudcomp.ch/research/foundation/themes/initiatives/rating-charging-billing/' target='_blank'>ICCLab RCB Initiative</a><br>
                <a style='color:black;text-decoration:none;' href='javascript:void(0);' target='_blank'>Community Help Page</a><br>
                <a style='color:black;text-decoration:none;' href='javascript:void(0);' target='_blank'>Developer's API Guide</a><br>
                <a style='color:black;text-decoration:none;' href='javascript:void(0);' target='_blank'>ICCLab AUP</a><br>
                <a style='color:black;text-decoration:none;' href='javascript:void(0);' target='_blank'>Contact Us</a>
            </td>
        </tr>
    </table>
    '''
    return content

def header():
    content = '''
        <div style='padding:0px;width:700px;margin-left:auto;margin-right:auto;margin-bottom:0px;padding:5px;color:white;background:#4A4F65;'>
            <img src='http://www.cise.ufl.edu/~pharsh/public/rcb-header.png' style='padding:0px;'>
        </div>
    '''
    return content

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
            CREATE TABLE user(id INT, username VARCHAR(45), password VARCHAR(128));
            DROP TABLE IF EXISTS project;
            CREATE TABLE project(id INT, name VARCHAR(45), userid INT, cfile TEXT);
            DROP TABLE IF EXISTS session;
            CREATE TABLE session(id INT, userid INT, taccess INT, projectid INT, isvalid BOOLEAN);
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
        print 'myRCBServer.py -c <configfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'myRCBServer.py -c <configfile> [-i]'
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
        Config.read("/Users/harh/Codes/ZHAW/Eclipse/workspace/TestPyServer/config.ini")
    else:
        Config.read(confFile)
    dbPath = Config.get("Database", "File")
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

