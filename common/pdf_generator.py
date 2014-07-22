# -*- coding: ascii -*-
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
#--------------------------------------------------------------
#  Created on Jul 08, 2014
#
#  @author: Piyush Harsh
#  @contact: piyush.harsh@zhaw.ch
#  @organization: ICCLab, Zurich University of Applied Sciences
#  @summary: Module to generate simple PDF files
#  Note: 
#  @var 
#  @requires: python 2.7, fpdf
#  Source can be downloaded from: 
#  https://pypi.python.org/pypi?:action=display&name=fpdf&version=1.7
#--------------------------------------------------------------

from fpdf import FPDF
from dateutil.relativedelta import *
import datetime
import time
import sys
import os


class PDF(FPDF):

    def __init__(self, logo_path, company_name, address1, address2):
        super(PDF, self).__init__()
        self.logo_path = logo_path
        self.company_name = company_name
        self.address1 = address1
        self.address2 = address2

        
    def header(self):
        # Logo
        self.image(self.logo_path,10,8,16)
        # Arial bold 15
        self.set_font('Arial','B',18)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30,8,self.company_name,0,1,'C')
        self.set_font('Arial','',12)
        self.cell(190,5,self.address1,0,1,'C')
        self.cell(190,5,self.address2,0,1,'C')
        # Line break
        self.ln(10)
        
    def section_title(self, label):
        #Arial 12
        self.set_font('Arial','B',12)
        #Background color
        self.set_fill_color(200,220,255)
        #Title
        self.cell(0,6,"%s"%(label),0,1,'L',1)
        #Line break
        self.ln(2)
    
    def section_body(self,value):
        #Read text file
        txt=value
        #Times 12
        self.set_font('Times','',12)
        #Output justified text
        self.multi_cell(0,5,txt)
        #Line break
        self.ln()
        #Mention in italics

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial','I',8)
        # Page number
        self.cell(0,10,'Page '+str(self.page_no())+'/{nb}',0,0,'C')


def generate_pdf(data):
    fileName =  data['prefix'] + data['userid'] + '.pdf'
    pdf = PDF(data['logo'], data['company'], data['company-address-1'], data['company-address-2'])
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(140, 10, 'ICCLab External Cloud Usage Bill for period:', 0, 0, 'L')
    pdf.set_font('Arial', 'B', 12)
    month_value = '%s - %s' % (data['bill-start'], data['bill-end'])
    pdf.cell(50, 10, month_value, 1, 0, 'R')
    pdf.ln(20)
    pdf.set_font('Times', 'B', 12)
    pdf.cell(190, 8, data['user-name'], 0, 1, 'R')
    pdf.set_font('Times', 'I', 10)
    pdf.cell(190, 1, data['user-address-1'], 0, 1, 'R')
    pdf.set_font('Times', '', 10)
    pdf.cell(190, 7, data['user-address-2'], 0, 0, 'R')
    pdf.ln(30)
    pdf.section_title('Itemized Price Breakdown')
    pdf.ln(5)
    ######## here just go over the itemized data and print out a line
    pdf.set_font('Times', 'B', 10)
    pdf.cell(100, 8, 'Meter Name', 1, 0, 'L')
    pdf.cell(55, 8, 'Units Consumed', 1, 0, 'R')
    pdf.cell(35, 8, 'Price', 1, 1, 'R')
    pdf.set_font('Courier', 'I', 10)
    for key in data['itemized-data'].keys():
        item = data['itemized-data'][key]
        pdf.cell(100, 8, str(item['name']), 0, 0, 'L')
        pdf.cell(55, 8, str(item['value']), 0, 0, 'R')
        pdf.cell(35, 8, str(item['price']), 0, 1, 'R')
    pdf.set_font('Times', '', 9)
    if str(data['unit'])=='0.01':
        pdf.cell(190,7,'* P r i c e s  p e r   u n i t   a r e   i n   c e n t s',0,1,'L')
    pdf.set_font('Times', 'B', 10)
    pdf.cell(155, 8, 'Total Amount Due', 1, 0, 'L')
    pdf.cell(25, 8, str(data['amount-due']), 'T B L', 0, 'R')
    pdf.cell(10,8,str(data['currency']),'T B R',1,'L')
    ############################
    pdf.ln(30)
    pdf.section_title('Important Dates')
    payment_hint = 'Your payment is due by: %s' % (data['due-date'])
    pdf.set_font('Times', 'B', 10)
    pdf.cell(190, 7, payment_hint, 0, 0, 'L')
    pdf.ln(30)
    pdf.section_title('Additional Notes')
    pdf.set_font('Times', '', 9)
    pdf.section_body(data['notes'])
    tmp_path=os.path.join(os.path.dirname( __file__ ), '..','..')
    if not os.path.exists(tmp_path+"/tmp/cyclops/generated-bills/"):
        os.makedirs(tmp_path+"/tmp/cyclops/generated-bills/")
    file_path=tmp_path+"/tmp/cyclops/generated-bills/"+fileName
    pdf.output(name=file_path, dest='F')
    print fileName
    
    return file_path


def main(argv):
    now = datetime.datetime.now()
    prefix = '%d-%d-%d-' % (now.year, now.month, now.day)
    directory = "/Users/harh/Desktop/"
    userid = 'piyush'
    logo = '/Users/harh/Desktop/icclab1.png'
    company_name = 'InIT Cloud Computing Lab'
    one_month_ago = datetime.datetime.now() - relativedelta(months=1)
    ######### This is how the dictionary is to be created, all entries are self explanatory
    data = {}
    data['prefix'] = prefix
    data['directory'] = directory
    data['userid'] = userid
    data['logo'] = logo
    data['company'] = company_name
    data['company-address-1'] = 'Obere Kirchgasse 2'
    data['company-address-2'] = '8400, Winterthur, Switzerland'
    data['user-name'] = 'Patrik Eschel'
    data['user-address-1'] = 'Team-IAMP, Technikumstrasse 9'
    data['user-address-2'] = '8400 Winterthur, Switzerland'
    data['bill-start'] = one_month_ago.strftime("%B")
    data['bill-end'] = now.year
    data['itemized-data'] = {}
    #each itemized entry must have 3 parts: meter-name, meter-value (with unit), item price
    data['itemized-data'][0] = {}
    data['itemized-data'][0]['name'] = 'Network-Bytes-Out (in bytes)'
    data['itemized-data'][0]['value'] = 1762341
    data['itemized-data'][0]['price'] = 1.034
    data['itemized-data'][1] = {}
    data['itemized-data'][1]['name'] = 'vCPU-Time (in ns)'
    data['itemized-data'][1]['value'] = 187254172
    data['itemized-data'][1]['price'] = 6.034
    data['itemized-data'][2] = {}
    data['itemized-data'][2]['name'] = 'Disk-Bytes-Written (in bytes)'
    data['itemized-data'][2]['value'] = 1725517
    data['itemized-data'][2]['price'] = 3.134
    data['amount-due'] = 10.202
    data['notes'] = 'As a public service to our research and student community, currently we do not charge you for using our cloud facilities. This arrangement may change in the future.'
    data['due-date'] = str(datetime.date.today() + datetime.timedelta(20)) 
    
    generate_pdf(data)
    return True

if __name__ == "__main__":
    main(sys.argv[1:])