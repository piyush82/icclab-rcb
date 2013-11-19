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

@get('/rcb/web/')
def index():
    response.set_header('Content-Language', 'en')
    response.set_header('Content-Type', 'text/html')
    content = '''
        <h3>Welcome to <a style='color:#8BACD7;' href='http://www.cloudcomp.ch/' target='_blank'>ICCLab</a>'s OpenCharge&trade; Platform!</h3>
        
        <i>OpenCharge&trade;</i> is a one of its kind - fully generic rating, charging, and billing platform designed to fully support
        any generic business process your company supports. You have full control over how you manage customer usage data collection, 
        mediation strategies, rating, charging, pricing and billing configuration. The platform supports special promotions, discounts
        and refunds in your overall billing functions.<br><br>
        
        <form action="/rcb/web/doaction" method="post" style='background:#6D8AB1;padding:5px;'>
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            <input type="hidden" name="actiontype" value="dologin">
            <input value="Login" type="submit" />
        </form>
        
        If you do not have an account, you can create one <a style='text-decoration:none;color:#6D8AB1;' href='/rcb/web/register'>here</a>.<br><br>
        
        <b>Salient Features:</b>
        <ul>
            <li>Support for OpenStack Grizzly, Havana Release</li>
            <li>REST API for seamless integration with your service
            <li>Customizable Analytics Module
            <li>OpenSource Licensing
        </ul>
        
        <br>
    '''
    return header() + content + footer() 

@get('/rcb/web/register')
def register():
    response.set_header('Content-Language', 'en')
    response.set_header('Content-Type', 'text/html')
    content = '''
        <p>Use the form to create a new service account. All fields are necessary.</p>
        <table style='font-family:Verdana;font-size:10pt;color:white;' align='left' cellspacing='2' cellpadding='2'>
            <form action="/rcb/web/doaction" method="post" style='background:#6D8AB1;padding:5px;'>
                <tr><td>Choose a username: <td><input name="username" type="text" />
                <tr><td>Password: <td><input name="password" type="password" />
                <tr><td>Retype Password: <td><input name="password1" type="password" />
                <tr><td>Email: <td><input name="email" type="text" />
                <tr><td>Retype Email: <td><input name="email1" type="text" /> <sup><i>Account activation link will be sent at this address</i></sup>
                <input type="hidden" name="actiontype" value="register">
                <tr><td><td align='left'><input value="Register" type="submit" />
            </form>
        </table>
    '''
    return header() + content + footer() + '</div>'

def header():
    content = '''
        <div style='padding:0px;width:700px;margin-left:auto;margin-right:auto;margin-bottom:0px;padding:5px;color:white;background:#4A4F65;'>
            <img src='http://www.cise.ufl.edu/~pharsh/public/rcb-header.png' style='padding:0px;'>
        </div>
        <div style='padding:5px;width:700px;margin-left:auto;margin-right:auto;font-family:Helvetica;font-size:10pt;background:#4A4F65;color:white;'>
    '''
    return content

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
    </div>
    '''
    return content