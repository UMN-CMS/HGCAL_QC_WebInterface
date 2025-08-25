#!./cgi_runner.sh

import cgi, html
import base
import add_test_functions
import os
from connect import connect

print("Content-type: text/html\n")

base.header(title='Get Manufacturer from code')
base.top()

db = connect(0)
cur = db.cursor()

# character #10 of serial number
form = cgi.FieldStorage()
code = form.getvalue("code")

cur.execute('select name from Manufacturers where letter_code="%s"' % code)
makers = cur.fetchall()

print('Begin')
for m in makers:
    print(m[0])
print('End')


base.bottom()

