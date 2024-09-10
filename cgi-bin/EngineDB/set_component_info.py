#!./cgi_runner.sh

import cgi
import cgitb
import base
from connect import connect

db = connect(1)
cur = db.cursor()

#cgi header
print("Content-type: text/html\n")

cgitb.enable()
form = cgi.FieldStorage()

label = form.getvalue('label')
working = form.getvalue('working')
comments = cgi.escape(form.getvalue('comments'))

if working == 'Yes':
    working = 1
else:
    working = 0

cur.execute('update Tester_Component set working=%s where full_id="%s"' % (working, label))
cur.execute('update Tester_Component set comments="%s" where full_id="%s"' % (comments, label))

db.commit()
