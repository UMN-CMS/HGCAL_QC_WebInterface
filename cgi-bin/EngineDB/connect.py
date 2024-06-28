#!/usr/bin/python3

import mysql.connector

def connect( num ):
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
        
# connects to the database with admin privileges
def connect_admin(passwd):

    try:
        connection = mysql.connector.connect(
            host = '',
            user='',
            password=passwd,
            database=get_db_name(),
            #cursorclass=mysql.connector.cursors.DictCursor
        )

        return connection
    except Exception as e:
        print("Failed to make DB connection. Wrong admin password")
        return None

def get_base_url():
    base = "http://cmslab1.spa.umn.edu/Factory/EngineDB/"
    return base

def get_db_name():
    name = "EngineDB"
    return name

