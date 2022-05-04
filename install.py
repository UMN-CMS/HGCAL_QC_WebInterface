#!/usr/bin/python3

import os
import sys
import subprocess 
import mysql.connector
import getpass

## Add tester in test DB
def add_tester( db ) : 
    try:
       cur = db.cursor()
       user = raw_input('Enter tester name : ')
       #print user
       cmd_user = 'INSERT INTO People set person_name="%s"' % (user)
       cur.execute(cmd_user) 
       db.commit()
    except mysql.connector.Error as err:
       print("<h3>lost DB connection!</h3>")

## Add test 
def add_test( db, nu ) : 
    try:
       testName     = raw_input('Enter test name : ')
       testDesShort = raw_input('Give short description : ')
       testDesLong  = raw_input('Give long description : ')
       cmd_test = 'insert into Test_Type set name="%s", required=1, desc_short="%s",desc_long="%s", relative_order=%d' % ( testName, testDesShort, testDesLong, nu )

       cur = db.cursor()
       cur.execute(cmd_test) 
       db.commit()
    except mysql.connector.Error as err:
       print("<h3>lost DB connection!</h3>")

## Grant Access 
def grant_access( db, name ) :
    try:

       cur = db.cursor()

       print 'DB Inserter Password : '
       inpw = getpass.getpass()
       cmd_gt  = "CREATE USER '%sInserter'@'localhost' IDENTIFIED BY '%s'" % (name, inpw)

       cur.execute(cmd_gt) 
       db.commit()
       cur.execute("GRANT INSERT ON %s.* TO '%sInserter'@'localhost'" % (name, name))
       db.commit()
       cur.execute("GRANT SELECT ON %s.* TO '%sInserter'@'localhost'" % (name, name))
       db.commit()

       print 'DB Reader Password : '
       rdpw = getpass.getpass()
       cmd_gt  = "CREATE USER '%sReadUser'@'localhost' IDENTIFIED BY '%s'" % (name, rdpw)
       cur.execute(cmd_gt) 
       db.commit()
       cur.execute("GRANT SELECT ON %s.* TO '%sReadUser'@'localhost'"%(name,name))
       db.commit()

       print 'DB Admin Password : '
       adpw = getpass.getpass()
       cmd_gt  = "CREATE USER '%sAdmin'@'localhost' IDENTIFIED BY '%s'" % (name, adpw)
       cur.execute(cmd_gt) 
       db.commit()
       cur.execute("GRANT SELECT ON %s.* TO '%sAdmin'@'localhost'"%(name,name))
       db.commit()
       cur.execute("GRANT INSERT ON %s.* TO '%sAdmin'@'localhost'"%(name,name))
       db.commit()

       text_file = open("connect.py", "w")
       text_file.write("import mysql.connector \n")
       text_file.write("def connect( num ):\n")
       text_file.write("    if(num==1):\n")
       text_file.write("       cnx = mysql.connector.connect(user='%sInserter', password='%s', database='%s')\n" % (name, inpw, name) )
       text_file.write("    if(num==0):\n")
       text_file.write("       cnx = mysql.connector.connect(user='%sReadUser', password='%s', database='%s')\n" % (name, rdpw, name) )
       text_file.write("    return cnx\n\n") 

       text_file.write("def connect_admin( passwd ):\n")
       text_file.write("    cnx = mysql.connector.connect(user='WagonDBAdmin', password='%%s' %% passwd, database='%s'\n") % (name, adpw, name))
       text_file.write("    return cnxi\n\n")

       text_file.write('def get_base_url():\n')
       text_file.write('    base = "http://cmslab3.spa.umn.edu/~cros0400/cgi-bin/"\n')
       text_file.write('    return base\n\n')
       
       text_file.write('def get_db_name():\n')
       text_file.write('    name = "%s"\n'%name)
       text_file.write('    return name\n\n')

       text_file.close()

    except mysql.connector.Error as err:
       print(err.errno)
       print("<h3>lost DB connection!</h3>")



## Setup area
#os.system("mkdir hcalDB")
#dbhome = subprocess.check_output("pwd")
os.chdir( os.getenv("HOME") )
#os.chdir("public_html")
dbhome = os.getcwd() 
print dbhome 
#os.system("git clone https://github.com/UMN-CMS/ePortage.git")
thePath = '%s%s' % (dbhome.rstrip() , "/WagonDB/cms-cgi-scripts-v1/cgi-bin")
print thePath
os.chdir(thePath) 
os.system("chmod a+x *.py")
os.chdir("../..") 

os.chdir("sql/") 
print 'MySQL Root password '
pw = getpass.getpass()
db = mysql.connector.connect(user='root', password= pw , database='')

database = raw_input("Enter database name: ")

cur = db.cursor()
cur.execute("create database %s;" % database)
db.commit()
cur.execute("use %s;" % database)
db.commit()

source_cmd = "mysql -u root --password=%s %s < schema_new.sql " % (pw, database)
#print(source_cmd)
os.system( source_cmd )


while True:
  add_tester( db ) 
  more_tester = raw_input(" Add more tester ? (Yes/No) " ) 
  if ( more_tester.lower() == 'no' or more_tester.lower() == 'n' ):
     break 

nu = 0 
while True:
  nu += 1 
  print ('Add test %d', nu ) 
  add_test( db, nu ) 
  more_test = raw_input(" Add more test ? (Yes/No) " ) 
  if ( more_test.lower() == 'no' or more_test.lower() == 'n' ):
     break 

grant_access( db, database )
os.system("chmod a+x connect.py")
os.system("mv connect.py ../cms-cgi-scripts-v1/cgi-bin/")

os.chdir("../cms-cgi-scripts-v1")
os.system("cp ../html/files/cmslogo.jpg static/files/")
os.system("cp ../html/files/us-cms.gif static/files/")

db.close()


