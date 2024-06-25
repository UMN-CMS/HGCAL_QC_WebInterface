#!/usr/bin/python3

import cgi
import base
from connect import connect

db = connect(1)
cur = db.cursor()

#cgi header
print("Content-type: text/html\n")

base.header(title='Add information about the tester equipment')
base.top(False)

form = cgi.FieldStorage()

kria = form.getvalue('kria')
tester = form.getvalue('tester')
interposter = form.getvalue('interposer')
int_type = form.getvalue('interposer_type')
test_stand = form.getvalue('test_stand')

cur.execute('select role_id from Tester_Roles where description="Kria Controller"')
kria_id = cur.fetchall()[0][0]

cur.execute('select role_id from Tester_Roles where description="Wagon Tester"')
tester_id = cur.fetchall()[0][0]

if int_type == 'East':
    cur.execute('select role_id from Tester_Roles where description="East Interposer"')
    int_id = cur.fetchall()[0][0]
if int_type == 'West':
    cur.execute('select role_id from Tester_Roles where description="West Interposer"')
    int_id = cur.fetchall()[0][0]

cur.execute('select teststand_id from Teststand where name="%s"' % test_stand)
test_stand_id = cur.fetchall()[0][0]

try:
    wheel_1 = form.getvalue('wheel_1')
except:
    wheel_1 = None

try:
    wheel_2 = form.getvalue('wheel_2')
except:
    wheel_2 = None

try:
    wheel_3 = form.getvalue('wheel_3')
except:
    wheel_3 = None

try:
    wheel_4 = form.getvalue('wheel_4')
except:
    wheel_4 = None

base.bottom(False)

