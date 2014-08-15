#!/bin/bash

sudo apt-get update

sudo apt-get install -y python-pip

sudo apt-get install -y python-django

sudo apt-get install -y python-setuptools

easy_install fpdf

easy_install python-dateutil

pip install sympy

pip install httplib2

pip install South

sudo apt-get install -y python2.7-mysqldb

sudo apt-get install -y mysql-server

mysqladmin create db_cyclops

EXPECTED_ARGS=3
E_BADARGS=65
MYSQL=`which mysql`

Q1="CREATE DATABASE IF NOT EXISTS $1;"
Q2="GRANT ALL ON *.* TO '$2'@'localhost' IDENTIFIED BY '$3';"
Q3="FLUSH PRIVILEGES;"
SQL="${Q1}${Q2}${Q3}"

if [ $# -ne $EXPECTED_ARGS ]
then
  echo "Usage: $0 dbname dbuser dbpass"
  exit $E_BADARGS
fi

$MYSQL -uroot -p -e "$SQL"

python manage.py syncdb --migrate