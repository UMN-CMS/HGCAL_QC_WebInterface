#!/usr/bin/python3

import mysql.connector

# connects to the database, 1 is for inserting and 0 is for reading
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

# holds the directory location
def get_base_url():
    base = "http://cmslab1.spa.umn.edu/Factory/WagonDB/"
    return base

# holds the database name
def get_db_name():
    name = "WagonDB"
    return name

