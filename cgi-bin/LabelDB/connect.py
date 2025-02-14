#!/usr/bin/python3

import mysql.connector

def connect( num ):
    if(num==1):

        # insert permissions
        connection = mysql.connector.connect(
            host = '',
            user='',
            password='',
            database=get_db_name(),
            #cursorclass=mysql.connector.cursors.DictCursor
        )
    
    if(num==0):

        # read permissions
        connection = mysql.connector.connect(
            host = '',
            user='',
            password='',
            database=get_db_name(),
            #cursorclass=mysql.connector.cursors.DictCursor
        )

    return connection
        
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
    base = "http://cmslab1.spa.umn.edu/Factory/LabelDB/"
    return base

def get_db_name():
    name = "HGCAL_Labeling"
    return name

