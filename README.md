# [Cyclops](https://github.com/piyush82/icclab-rcb)

##Developed by 

[InIT Cloud Computing Lab] (http://blog.zhaw.ch/icclab/)

##Description

Generic Rating, Charging & Billing framework for cloud services.

##System Requirements

1. CPU
2. RAM > 2GB
3. Disp Space > 5 GB

##Known Issue

**Warning**: Django expects the root user to not have a password. When a password is entered as part of the setup script's argument, the script is known to fail.

##Get started

1. Install git on the server
2. Load the coadbase on to the server ```git clone https://github.com/piyush82/icclab-rcb.git```
3. Change directory into "icclab-rcb" ```cd icclab-rcb```
4. Run the setup file ```sudo bash setup.sh {username}```
5. Edit the config.conf file to add the URL for authentication and DB login credentials
