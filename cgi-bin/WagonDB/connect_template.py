#!/usr/bin/python3

import mysql.connector
from hashlib import sha256

# connects to the database, 1 is for inserting and 0 is for reading
def connect( num ):
    try:
        if(num==1):
            connection = mysql.connector.connect(
                host = '',
                user='',
                password='',
                database=get_db_name(),
                #cursorclass=mysql.connector.cursors.DictCursor
            )
        if(num==0):
            connection = mysql.connector.connect(
                host = '',
                user='',
                password='',
                database=get_db_name(),
                #cursorclass=mysql.connector.cursors.DictCursor
            )

        return connection
    except Exception as e:
        print("Failed to make DB connection. Wrong admin password")
        return None

def connect_admin(passwd):

    if sha256(passwd.encode('utf-8')).hexdigest() == '6f69716360fb991f244305c59c1facc04a04f2548a49aed17e38eb0873f687a1':
        return connect(1)
    else:
        print("Failed to make DB connection. Wrong admin password")
        return None

# holds the directory location
def get_base_url():
    base = "http://cmslab1.spa.umn.edu/Factory/WagonDB/"
    return base

def get_db_name():
    name = "WagonDB_PRO"
    return name

