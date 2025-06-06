#!./cgi_runner.sh

import cgi, html
import base
from connect import connect
import settings
import os.path
import sys
import json

db=connect(0)
cur=db.cursor()


form = cgi.FieldStorage()
config_id = base.cleanCGInumber(form.getvalue('config_id'))

cur.execute("select role_id, component_id, teststand_id from Tester_Configuration where config_id=%s" % (config_id));

if not cur.with_rows:
    print("Content-type: text/html\n")
    base.header("Attachment Request Error")
    base.top(False)
    print('<div class="col-md-6 ps-4 pt-4 mx-2 my-2">')
    print("<h1>Teststand Info not available</h1>")
    print('</div>')
    base.bottom(False)
else:    
    thevals=cur.fetchall()
    parts = {}
    for t in thevals:
        cur.execute('select full_id from Tester_Component where component_id=%s' % t[1])
        sn = cur.fetchall()[0][0]

        cur.execute('select description from Tester_Roles where role_id=%s' % t[0])
        role = cur.fetchall()[0][0]
        parts[role] = sn

    cur.execute('select name from Teststand where teststand_id=%s' % thevals[0][2])
    parts['Teststand'] = cur.fetchall()[0][0]

    print("Content-type: text/plain\n")
    for k,v in parts.items():
        print(f'{k}: {v}')
