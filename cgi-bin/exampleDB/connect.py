#!/usr/bin/python3

import mariadb
from hashlib import sha256

# connects to the database, 1 is for inserting and 0 is for reading
def connect(num):
    if(num==1):
        connection = mariadb.connect(
            host='localhost',
            user ='',
            password ='',
            database=get_db_name(),
            #cursorclass=mariadb.cursors.DictCursor
        )
    if(num==0):
        connection = mariadb.connect(
            host='localhost',
            user='',
            password='',
            database=get_db_name(),
            #cursorclass=mariadb.cursors.DictCursor
        )

    return connection

# for requiring an admin password to perform certain actions with the database
def connect_admin(passwd):

    if sha256(passwd.encode('utf-8')).hexdigest() == '':
        return connect(1)
    else:
        print("Failed to make DB connection. Wrong admin password")
        return None

# holds the directory location
def get_base_url():
    # TODO replace this with the web address for your directory
    base = "http://cmslab1.spa.umn.edu/Factory/WagonDB/"
    return base

def get_db_name():
    name = ""
    return name

def get_image_location():
    # TODO add absolute path to image directory here
    fp = "/path/to/images/"
    return fp

