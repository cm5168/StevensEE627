# StevensEE627
Class Project for EE627

### Prerequisite
* Python 2
* Flask
* Nginx*
* uWSGI*

###### *optional


##### Flask
Install Flask

_pip install flask_

##### Nginx and uWSGI 
[Check out vladikk's tutorial](http://vladikk.com/2013/09/12/serving-flask-with-nginx-on-ubuntu/)

### Tutorial

1. Install Packages

sudo apt-get update
sudo apt-get install git
sudo apt-get install python-pip build-essential python-dev
sudo apt-get install nginx
(if not working, try the following before install nginx)
sudo add-apt-repository ppa:nginx/stable

sudo pip install uwsgi
(if getting errors try apt-get update)

2. Install Flask

sudo apt-get install flask
(or install flask on a virtual environment)
[Tutorial from Flask website](http://flask.pocoo.org/docs/0.10/installation/)

3. Copy to server

mkdir flask
git clone https://github.com/cm5168/StevensEE627.git

4. Configure nginx and uWSGI

sudo rm /etc/nginx/sites-enabled/default
sudo ln -s ~/flask/StevensEE627/nginx.conf /etc/nginx/conf.d/
sudo /etc/init.d/nginx start
uwsgi --ini uswgi.ini

5. Edit TeamInfo.txt

The Team information are stored in TeamInfo file. Follow the same format edit the team info.
teamName|Member1, Member2, Member3

6. Run server

python 627.py

7. The server is good to go!



