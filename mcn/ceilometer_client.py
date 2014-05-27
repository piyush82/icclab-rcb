#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2014 Zuercher Hochschule fuer Angewandte Wissenschaften
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

'''
Created on May 22, 2014
 
@author: Piyush Harsh (piyush.harsh@zhaw.ch)
 
This is RCB client to send metrics for IaaS providers

This module requires python-ceilometerclient to be installed.

Instructions: sudo apt-get install python-pip git-core
              sudo pip install python-ceilometerclient

'''

from ceilometerclient import client
from os import environ as env
from ceilometerclient.common import utils


def get_meters(keystone):
    '''
    returns the list of relevant meters that this user can use
    '''
    ceilometer_client = client.get_client(2,**keystone)
    meter_list = []
    meters = ceilometer_client.meters.list()
    for meter in meters:
        if meter._info['user_id'] != None:
            list_element = {}
            list_element['user_id'] = meter._info['user_id']
            list_element['meter_id'] = meter._info['meter_id']
            list_element['meter_name'] = meter._info['name']
            list_element['resource_id'] = meter._info['resource_id']
            list_element['meter_type'] = meter._info['type']
            list_element['meter_unit'] = meter._info['unit']
            meter_list.append(list_element)
    #return this formatted list
    return meter_list

def classify_meters(meter_list, classifier):
    '''
    returns a dictionary with list of meters classified by the parameter
    parameters currently supported are: resource, type
    '''
    groups = {}
    if classifier == 'resource':
        #now we make the meters classification available by resources belonging to this user
        for meter in meter_list:
            if groups.get(meter['resource_id']) == None:
                groups[meter['resource_id']] = []
            list_element = {}
            list_element['meter_name'] = meter['meter_name']
            list_element['meter_type'] = meter['meter_type']
            list_element['meter_unit'] = meter['meter_unit']
            list_element['user_id'] = meter['user_id']
            (groups[meter['resource_id']]).append(list_element)
        return groups
    if classifier == 'type':
        #now we make the meters classification available by types belonging to this user
        for meter in meter_list:
            if groups.get(meter['meter_type']) == None:
                groups[meter['meter_type']] = []
            list_element = {}
            list_element['meter_name'] = meter['meter_name']
            list_element['resource_id'] = meter['resource_id']
            list_element['meter_unit'] = meter['meter_unit']
            list_element['user_id'] = meter['user_id']
            (groups[meter['meter_type']]).append(list_element)
        return groups

def get_statistics(keystone, meterName, query, period, groupBy):
    '''
    returns a dictionary of dictionaries of lists - dict[user id][resource id]->list[statistics list]
    '''
    ceilometer_client = client.get_client(2,**keystone)
    stats = ceilometer_client.statistics.list(meterName, query, period, groupBy)
    stat_list = {}
    for stat in stats:
        if (stat._info['groupby'])['user_id'] != None:
            if stat_list.get((stat._info['groupby'])['user_id']) == None:
                stat_list[(stat._info['groupby'])['user_id']] = {}
            if (stat_list[(stat._info['groupby'])['user_id']]).get((stat._info['groupby'])['resource_id']) == None:
                (stat_list[(stat._info['groupby'])['user_id']])[(stat._info['groupby'])['resource_id']] = []
            # Now add this statistic entry into this two level dictionary's list
            stat_element = {}
            stat_element['count'] = stat._info['count']
            stat_element['duration_start'] = stat._info['duration_start']
            stat_element['duration_end'] = stat._info['duration_end']
            stat_element['period_start'] = stat._info['period_start']
            stat_element['period_end'] = stat._info['period_end']
            stat_element['unit'] = stat._info['unit']
            stat_element['sum'] = stat._info['sum']
            stat_element['avg'] = stat._info['avg']
            stat_element['max'] = stat._info['max']
            stat_element['min'] = stat._info['min']
            ((stat_list[(stat._info['groupby'])['user_id']])[(stat._info['groupby'])['resource_id']]).append(stat_element)
    return stat_list

def filter_statistics(stat_list, userid, resourceid):
    '''
    returns a list of statistics samples filtered by user id and resource id for all time intervals
    '''
    return (stat_list[userid])[resourceid]

def filter_statistics_by_time(stats_list, period_start):
    '''
    return the relevant statistics entries after a particular time specified in the call
    '''
    filteredList = []
    for stat in stats_list:
        startDate = ((stat['period_start']).split('T'))[0] #gets the date
        if startDate >= period_start:
            filteredList.append(stat)
    return filteredList

if __name__ == '__main__':
    #getting the credentials
    keystone = {}
    keystone['os_username']='your-user'
    keystone['os_password']='your-pass'
    keystone['os_auth_url']='http://160.85.4.224:5000/v2.0'
    keystone['os_tenant_name']='MCN-RCBaaS'
    mList = get_meters(keystone)
    #===========================================================================
    # for element in mList:
    #     print element
    #===========================================================================
    rList = classify_meters(mList, 'resource')
    print "Now printing the meters grouped by resources: "
    for resource in rList.keys():
        print "------------"
        print "Lists of meters for resource %s" % (resource)
        print "Length os this list is %d" % (len(rList[resource]))
        for meter in rList[resource]:
            print meter
    tList = classify_meters(mList, 'type')
    print "Now printing the meters grouped by meter-type: "
    for type in tList.keys():
        print "------------"
        print "Lists of meters of type %s" % (type)
        print "Length os this list is %d" % (len(tList[type]))
        for meter in tList[type]:
            print meter
    print "Now printing a test statistics call output"
    stats = get_statistics(keystone, 'network.incoming.bytes', None, '86400', ["resource_id", "user_id"])
    for user_id in stats.keys():
        print "++"
        print "Printing all relevant data for user: %s" % (user_id)
        for resource_id in (stats[user_id]).keys():
            candidates = filter_statistics(stats, user_id, resource_id)
            filteredStats = filter_statistics_by_time(candidates, '2014-05-26')
            if len(filteredStats) > 0:
                print "------ Showing entries after %s only out of %d entries for Resource ID : %s ------" % ('2014-05-26', len((stats[user_id])[resource_id]), resource_id)
                for entry in filteredStats:
                    print entry
            #===================================================================
            # for entry in (stats[user_id])[resource_id]:
            #     print entry
            #===================================================================
