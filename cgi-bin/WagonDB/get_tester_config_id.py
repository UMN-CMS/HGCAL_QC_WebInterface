#!./cgi_runner.sh

import cgi, html
import cgitb
import base
from connect import connect

db = connect(1)
cur = db.cursor()

#cgi header
print("Content-type: text/html\n")

cgitb.enable()

base.header(title='Get Current Configuration for a given teststand')
base.top()

form = cgi.FieldStorage()

test_stand = form.getvalue('test_stand')

cur.execute('select teststand_id from Teststand where name="%s"' % test_stand)
test_stand_id = cur.fetchall()
if test_stand_id:
    test_stand_id = test_stand_id[0][0]
    cur.execute('select config_id from Tester_Configuration where teststand_id=%s order by config_id desc' % test_stand_id)
    print('Begin')
    print(cur.fetchall()[0][0])
    print('End')


base.bottom()

