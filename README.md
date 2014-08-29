# [Cyclops](https://github.com/piyush82/icclab-rcb)

##Developed by 

[InIT Cloud Computing Lab] (http://blog.zhaw.ch/icclab/)

##Description

Generic Rating, Charging & Billing framework for cloud services.

##System Requirements

1. CPU > 1.7 GHz
2. RAM > 2GB
3. Disp Space > 5 GB

##Known Issue

**Warning**: Django expects the mysql root user to not have a password. For a mysql root user with a password, an error is thrown at the stage of syncing & migration of the db schemas.

##Get started

1. Install git on the server
2. Load the coadbase on to the server ```git clone https://github.com/piyush82/icclab-rcb.git```
3. Change directory into "icclab-rcb" ```cd icclab-rcb```
4. Run the setup file ```sudo bash setup.sh {username} {password}```
  4.1 Here the username and password are the mysql account details that will be used by cyclops.
5. Edit the config.conf file to add the URL for authentication and mysql server login credentials, mysql username and password will be the values you provided while running the script.
6. Start the server ```python manage.py runserver 0.0.0.0:[port]```
