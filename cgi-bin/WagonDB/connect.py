#!/usr/bin/python3

import mysql.connector

def connect( num ):
    if(num==1):

        connection = mysql.connector.connect(
            host = 'localhost',
            user='WagonDBInserter',
            password='HGCALrocks',
            database=get_db_name(),
            #cursorclass=mysql.connector.cursors.DictCursor
        )
    
    if(num==0):

        connection = mysql.connector.connect(
            host = 'localhost',
            user='WagonDBReadUser',
            password='HGCALrocks',
            database=get_db_name(),
            #cursorclass=mysql.connector.cursors.DictCursor
        )

    return connection
        
def connect_admin(passwd):

    connection = mysql.connector.connect(
        host = 'localhost',
        user='WagonDBAdmin',
        password=passwd,
        database=get_db_name(),
        #cursorclass=mysql.connector.cursors.DictCursor
    )

    return connection

def get_base_url():
    base = "http://cmslab3.umncmslab/~cros0400/cgi-bin/WagonDB"
    return base

def get_db_name():
    name = "WagonDB"
    return name

