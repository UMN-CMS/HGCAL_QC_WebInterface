#!/usr/bin/python3

import mysql.connector 

def connect( num ):
    if(num==1):
       cnx = mysql.connector.connect(user='WagonInserter', password='password', database='WagonDB', port='3306')
    if(num==0):
       cnx = mysql.connector.connect(user='WagonReadUser', password='password', database='WagonDB', port='3306')
    return cnx
