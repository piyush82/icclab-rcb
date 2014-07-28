#! /usr/local/bin/python



sudo apt-get install python-django

easy_install fpdf

easy_install python-dateutil

pip install sympy

pip install httplib2

sudo apt-get install python2.7-mysqldb

sudo apt-get install mysql-server

mysqladmin create db_cyclops

python manage.py syncdb --migrate
