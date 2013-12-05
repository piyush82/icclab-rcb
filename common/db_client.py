# -*- coding: ascii -*-
#--------------------------------------------------------------
#Created on Dec 2, 2013
#
#@author: Piyush Harsh
#@contact: piyush.harsh@zhaw.ch
#@organization: ICCLab, Zurich University of Applied Sciences
#@summary: module for database operations, supported DB - sqlite3, planned: mangodb, mysql
# Note:
#@var 
#@requires: python 2.7, sqlite3
#--------------------------------------------------------------

import sqlite3 as db

def query(path, field_list, table, condition, fetchOne):
    con = None
    data = None
    try:
        con = db.connect(path)
    except db.Error, e:
        print 'Error %s:' % e.args[0]
        return False, None
    
    try:
        cur = con.cursor()
        statement = "SELECT " + field_list + " from " + table + " WHERE " + condition
        cur.execute(statement);
        if fetchOne:
            data = cur.fetchone()
        else:
            data = cur.fetchall()
    except db.Error, e:
        print 'Error %s:' % e.args[0]
        return False, None
    if con:
        con.close()
    return True, data

def add(path, table, values):
    con = None
    data = None
    max = -1
    try:
        con = db.connect(path)
    except db.Error, e:
        print 'Error %s:' % e.args[0]
        return False
    
    try:
        cur = con.cursor()
        statement = "INSERT into " + table + " VALUES(" + values + ")"
        cur.execute(statement)
        con.commit()
    except db.Error, e:
        print 'Error %s:' % e.args[0]
        return False
    if con:
        con.close()
    return True

def getMax(path, field, table):
    con = None
    data = None
    max = -1
    try:
        con = db.connect(path)
    except db.Error, e:
        print 'Error %s:' % e.args[0]
        return False, None
    
    try:
        cur = con.cursor()
        statement = "SELECT max(" + field + ") from " + table
        cur.execute(statement)
        data = cur.fetchone()
        if data[0] != None:
            max = data[0]
    except db.Error, e:
        print 'Error %s:' % e.args[0]
        return False, None
    if con:
        con.close()
    return True, max

def count(path, field, table, condition):
    con = None
    data = None
    count = 0
    try:
        con = db.connect(path)
    except db.Error, e:
        print 'Error %s:' % e.args[0]
        return False, None
    
    try:
        cur = con.cursor()
        statement = "SELECT count(" + field + ") from " + table + " WHERE " + condition
        cur.execute(statement)
        data = cur.fetchone()
        if data[0] != None:
            count = data[0]
    except db.Error, e:
        print 'Error %s:' % e.args[0]
        return False, None
    if con:
        con.close()
    return True, count