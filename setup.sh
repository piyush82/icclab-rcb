#!/bin/bash
echo "Cyclops setup script run initiating ... some package installation may take time, so please be patient!"
if [ $# -eq 0 ]
  then
    echo "No arguments supplied, expected (mysql_user, mysql_user_password)"
    echo "Usage sudo bash setup.sh [mysql user] [mysql user password]"
    exit 1
fi
apt-get update
# Installing python pip package
apt-get install -y python-pip
# Installing django
apt-get install -y python-django
# Installing associated tools
apt-get install -y python-setuptools
# Installing various python libraries needed for cyclops
easy_install fpdf
easy_install python-dateutil
pip install sympy
pip install httplib2
pip install South
apt-get install -y python2.7-mysqldb
# installing mysql server
echo "Installing mysql server, we recommend to leave the root password blank"
echo "You can always secure mysql service by securing user access correctly"
apt-get install -y mysql-server

# mysqladmin create db_cyclops

MYSQL=`which mysql`

Q1="CREATE DATABASE IF NOT EXISTS db_cyclops;"
Q2="GRANT ALL PRIVILEGES ON db_cyclops.* TO '$1'@'localhost' IDENTIFIED BY '$2' WITH GRANT OPTION;"
Q3="FLUSH PRIVILEGES;"
SQL="${Q1}${Q2}${Q3}"

echo "---------------------------------------------------------------------------"
echo "| Next you will be asked to provide the mysql password for the user root."
echo "| If you left it blank in the previous step, simply press enter."
echo "---------------------------------------------------------------------------"
read -p "Press any key to continue ..." -n1 -s

$MYSQL -uroot -p -e "$SQL"

# Now creating correct schemas in the db
echo "----------------------------------------------------------------------------"
echo "| Now performing db schema syncs, if certain tables already exists, you may see error messages ..."
echo "| Please just ignore them."
echo "----------------------------------------------------------------------------"
read -p "Press any key to continue ..." -n1 -s

python manage.py syncdb --migrate
echo "----------------------------------------------------------------------------"
echo "| Cyclops installation script run done. Please update the config.conf file before starting the application."
echo "| You can start your application using: python manage.py runserver 0.0.0.0:8000"
echo "----------------------------------------------------------------------------"
read -p "Press any key to modify the config file now ... " -n1 -s
updatedb
CONFFILE=`locate icclab-rcb/config.conf`
nano ${CONFFILE}
echo ""
echo "Start your server using: python manage.py runserver 0.0.0.0:[port]"
echo ""
