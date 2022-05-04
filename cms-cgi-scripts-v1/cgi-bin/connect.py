import mysql.connector 

def connect( num ):
    if(num==1):
       cnx = mysql.connector.connect(user='WagonDBInserter', password='password', database='WagonDB')
    if(num==0):
       cnx = mysql.connector.connect(user='WagonDBReadUser', password='password', database='WagonDB')
    return cnx

def connect_admin( passwd ):
    cnx = mysql.connector.connect(user='WagonDBAdmin', password='%s' % passwd, database='WagonDB')
    return cnx

def get_base_url():
    base = "http://cmslab3.spa.umn.edu/~cros0400/cgi-bin/"
    return base

def get_db_name():
    name = "WagonDB"
    return name

