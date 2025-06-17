#!/usr/bin/python3

import mysql.connector
from hashlib import sha256

# connects to the database, 1 is for inserting and 0 is for reading
def connect(num):
    if(num==1):
        # fill in with hostname, username, and password
        connection = mysql.connector.connect(
            host = '',
            user='',
            password='',
            database=get_db_name(),
            #cursorclass=mysql.connector.cursors.DictCursor
        )
    if(num==0):
        # fill in with hostname, username, and password
        connection = mysql.connector.connect(
            host = '',
            user='',
            password='',
            database=get_db_name(),
            #cursorclass=mysql.connector.cursors.DictCursor
        )

    return connection

# for requiring an admin password to perform certain actions with the database
def connect_admin(passwd):

    # insert the hash for the admin password of your choosing
    if sha256(passwd.encode('utf-8')).hexdigest() == '':
        return connect(1)
    else:
        print("Failed to make DB connection. Wrong admin password")
        return None

# holds the directory location
def get_base_url():
    # replace this with the web address for your directory
    base = "http://cmslab1.spa.umn.edu/Factory/WagonDB/"
    return base

def get_db_name():
    # add database name here
    name = ""
    return name

def get_image_location():
    # add absolute path to image directory here
    fp = "/path/to/images/"
    return fp

