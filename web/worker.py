############################################################
#@author: Piyush Harsh (piyush.harsh@zhaw.ch)
#@version: 0.1
#@summary: Module implementing RCB Rest Interface
#
#@requires: bottle
############################################################

from bottle import get, post, request, route, run, response
import ConfigParser
import sys, getopt
sys.path.append('/Users/harh/Codes/ZHAW/Eclipse/workspace/os_rcb')  #change this to point to the correct path where icclab-rcb is located
import hashlib
import uuid
from web_ui import header
from web_ui import footer
from common import db_client
import config

def validate(username, password):
    userid = -1;
    try:
        status, data = db_client.query(config.globals[0], "id, password, isactive", "user", "username='" + username + "'", True)
        if(data is not None):
            userid = data[0]
        md5sum = hashlib.md5(password.strip()).hexdigest()
        if data != None and md5sum == data[1]:
            return True, userid
        else:
            return False, userid
    except e:
        print 'Error %s:' % e.args[0]
        content += "<br><p style='color:#EEBDBD;'>RCB DB error detected!</p><br>"
    return False, userid

def validate_conf(conf):
    #for now we will test with only OpenStack credentials
    lines = conf.split('\n')
    res = ''
    for line in lines:
        if not (line.strip().startswith('#')) and (line.strip().startswith('export')) and len(line.strip()) > 0 and not '$' in line:
            if len(res) > 0:
                res += '\n' + line.strip()
            else:
                res += line.strip()
            
    if len(res) > 0 and 'OS_TENANT_ID' in res and 'OS_TENANT_NAME' in res and 'OS_USERNAME' in res:
        return True, res
    else:
        return False, res

@post('/rcb/web/doaction')
def actuator():
    response.set_header('Content-Language', 'en')
    response.set_header('Content-Type', 'text/html')
    actiontype = request.forms.get('actiontype')
    
    content = ''
    
    if actiontype == 'register':
        username = request.forms.get('username')
        password = request.forms.get('password')
        password1 = request.forms.get('password1')
        email = request.forms.get('email')
        email1 = request.forms.get('email1')
        try:
            condition = "username='" + username + "'"
            status, user_count = db_client.count(config.globals[0], "*", "user", condition)
            
            if status and user_count != 0:
                content += "<br><p style='color:#EEBDBD;font-family:Times;font-size:11pt;'>This username is already in use! Please use a different id and try again.</p>"
                content += "<a style='text-decoration:none;color:#8BACD7;' href='Javascript:void(0);' onClick='history.go(-1);'>go back</a><br><br>"
            else:
                #now here create a new user account
                if (password != password1) or (email != email1) or len(password.strip()) == 0 or len(username.strip()) == 0 or len(email.strip()) == 0:
                    content += "<br><p style='color:#EEBDBD;font-family:Times;font-size:11pt;'>Invalid form input detected. Fix and try again.</p>"
                    content += "<a style='text-decoration:none;color:#8BACD7;' href='Javascript:void(0);' onClick='history.go(-1);'>go back</a><br><br>"
                else:
                    md5sum = hashlib.md5(password.strip()).hexdigest()
                    id = -1
                    status, id = db_client.getMax(config.globals[0], "id", "user")
                    if status:
                        id += 1
                        uid = uuid.uuid4()
                        values = (id, username, md5sum, uid.hex, email, 0)
                        values = "%d, " % id
                        values += "'" + username + "', '" + md5sum + "', '" + uid.hex + "', '" + email + "', 0"
                        status = db_client.add(config.globals[0], "user", values)
                        if status:
                            content += "<br><p style='color:##E1F5A9;'>Account successfully created. Soon you will receive an email with activation link in it.</p>"
                            content += "Proceed back to <a style='text-decoration:none;color:white;' href='/rcb/web/'>home page</a>"
                        else:
                            content += "<br><p style='color:#EEBDBD;'>RCB DB error detected!</p><br>"
                    else:
                        content += "<br><p style='color:#EEBDBD;'>RCB DB error detected!</p><br>"
        except e:
            print 'Error %s:' % e.args[0]
            content += "<br><p style='color:#EEBDBD;'>RCB DB error detected!</p><br>"
    elif actiontype == 'dologin':
        username = request.forms.get('username')
        password = request.forms.get('password')
        try:
            authenticated, userId = validate(username, password)
            if authenticated:
                content += '<p style="font-family:Verdana;font-size:10pt;">Welcome %s!</p>' % username
                condition = "userid=%d" % userId
                status, data = db_client.query(config.globals[0], "*", "project", condition, False)
                if data != None and len(data) != 0:
                    print 'Found a project'
                else:
                    content += "No registered project found. You can create a new project next.<br><br>"
                    content += "<form style='font-family:Times; font-size:11pt;border:2px;' method='post' action='/rcb/web/doaction'>"
                    content += "<fieldset><legend>Create a new project:</legend>"
                    content += "<table cellspacing='2' cellpadding='2' style='font-family:Times;font-size:10pt;color:white;'>"
                    content += '''
                        <tr> <td>Project Name <td> <input name='project-name' type='text'> <input type="hidden" name="actiontype" value="createproject">
                        <tr> <td valign='top'>Project Configuration Data<br>(leave empty if not known)<td><textarea name='project-conf' cols='60' rows='8'></textarea>
                        <tr><td> <td align='right'><input type='submit' value='create'>
                    '''
                    content += "<input type=\"hidden\" name=\"username\" value=\"%s\">" % username
                    content += "<input type=\"hidden\" name=\"password\" value=\"%s\">" % password
                    content += "</table></fieldset></form><br><br>"
            else:
                content += '<p style="color:#EEBDBD;">Incorrect username / password entered. Please go back and try again.</p>'
        except e:
            print 'Error %s:' % e.args[0]
            content += "<br><p style='color:#EEBDBD;'>RCB DB error detected!</p><br>"
    elif actiontype == 'createproject':
        username = request.forms.get('username')
        password = request.forms.get('password')
        authenticated, userId = validate(username, password)
        if authenticated:
            print username, password, userId
            projName = request.forms.get("project-name")
            projConf = request.forms.get("project-conf")
            isValid, conf = validate_conf(projConf)
            #TODO: implement the conf string parser function to extract individual parameters of the extracted configuration
            
            if isValid and len(projName.strip()) > 0:
                try:
                    id = -1
                    status, id = db_client.getMax(config.globals[0], "id", "project")
                    if status:
                        id += 1
                        values = "%d, " % id
                        values += "'" + projName.strip() + "', %d" % userId
                        values += ", '" + conf + "'"
                        status = db_client.add(config.globals[0], "project", values)
                        if status:
                            content += "<br><p style='color:##E1F5A9;'>Project successfully created.</p>"
                            content += "Proceed back to <a style='text-decoration:none;color:white;' href='/rcb/web/'>home page</a>"
                        else:
                            content += "<br><p style='color:#EEBDBD;'>RCB DB error detected!</p><br>"
                    else:
                        content += "<br><p style='color:#EEBDBD;'>RCB DB error detected!</p><br>"
                except e:
                    print 'Error %s:' % e.args[0]
                    content += "<br><p style='color:#EEBDBD;'>RCB DB error detected!</p><br>"
                print conf
            else:
                content += '<p style="color:#EEBDBD;">Invalid form data. Please make sure that the data you entered is valid. It is recommended you simply copy and paste your cloud credentials file. Go back and try again.</p>'
        else:
            content += '<p style="color:#EEBDBD;">Incorrect username / password entered. Please go back and try again.</p>'
        
    return header() + content + footer()