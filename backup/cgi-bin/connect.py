import mysql.connector 
def connect( num ):
    if(num==1):
       cnx = mysql.connector.connect(user='WagonInserter', password='password', database='WagonDB')
    if(num==0):
       cnx = mysql.connector.connect(user='WagonReadUser', password='password', database='WagonDB')
    return cnx


def get_domain():
    domain = "http://cmslab3.spa.umn.edu/~cros0400/cgi-bin/"
    return domain

