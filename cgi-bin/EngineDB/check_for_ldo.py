#!./cgi_runner.sh

import cgi, html
import base
import os
from connect import connect

#cgi header
print("Content-type: text/html\n")

base.header(title='Check For LDO')
base.top()

db = connect(0)
cur = db.cursor()

form = cgi.FieldStorage()

board_id = html.escape(form.getvalue('full_id'))

cur.execute('select LDO from Board where full_id="%s"' % board_id)
ldo = cur.fetchall()

try:
    ldox = ldo[0][0]
except:
    raise Exception

print('Begin')

for t in ldo:
    print(t[0])

print('End')

base.bottom()
