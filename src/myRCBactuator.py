############################################################
#@author: Piyush Harsh (piyush.harsh@zhaw.ch)
#@version: 0.1
#@summary: Module implementing RCB Rest Interface
#
#@requires: bottle
############################################################

from bottle import get, post, request, route, run, response
import ConfigParser
import sqlite3 as db
import sys, getopt
import hashlib
import uuid
from myRCBwebui import header, footer
import config

@post('/rcb/web/doaction')
def actuator():
    response.set_header('Content-Language', 'en')
    response.set_header('Content-Type', 'text/html')
    actiontype = request.forms.get('actiontype')
    
    con = None
    try:
        con = db.connect(config.dbPath)
    except db.Error, e:
        print 'Error %s:' % e.args[0]
    
    content = ''
    
    if actiontype == 'register':
        username = request.forms.get('username')
        password = request.forms.get('password')
        password1 = request.forms.get('password1')
        email = request.forms.get('email')
        email1 = request.forms.get('email1')
        try:
            cur = con.cursor()
            cur.execute("SELECT count(*) from user WHERE username='" + username + "'");
            data = cur.fetchone()
            print 'Count: %d' %data[0]
            if data[0] != 0:
                content += "<br><p style='color:#EEBDBD;font-family:Times;font-size:11pt;'>This username is already in use! Please use a different id and try again.</p>"
                content += "<a style='text-decoration:none;color:#8BACD7;' href='Javascript:void(0);' onClick='history.go(-1);'>go back</a><br><br>"
            else:
                #now here create a new user account
                if (password != password1) or (email != email1) or len(password.strip()) == 0 or len(username.strip()) == 0 or len(email.strip()) == 0:
                    content += "<br><p style='color:#EEBDBD;font-family:Times;font-size:11pt;'>Invalid form input detected. Fix and try again.</p>"
                    content += "<a style='text-decoration:none;color:#8BACD7;' href='Javascript:void(0);' onClick='history.go(-1);'>go back</a><br><br>"
                else:
                    md5sum = hashlib.md5(password.strip()).hexdigest()
                    cur.execute("SELECT max(id) from user")
                    data = cur.fetchone()
                    id = -1
                    if data[0] != None:
                        id = data[0]
                    id += 1
                    uid = uuid.uuid4()
                    values = (id, username, md5sum, uid.hex, email, 0)
                    statement = "INSERT INTO user VALUES(%d, " % id
                    statement += "'" + username + "', '" + md5sum + "', '" + uid.hex + "', '" + email + "', 0)"
                    print statement
                    cur.execute(statement)
                    con.commit()
                    content += "<br><p style='color:##E1F5A9;'>Account successfully created. Soon you will receive an email with activation link in it.</p>"
                    content += "Proceed back to <a style='text-decoration:none;color:white;' href='/rcb/web/'>home page</a>"
        except db.Error, e:
            print 'Error %s:' % e.args[0]
            content += "<br><p style='color:#EEBDBD;'>RCB DB error detected!</p><br>"
            
    if con:
        con.close()
        
    return header() + content + footer()