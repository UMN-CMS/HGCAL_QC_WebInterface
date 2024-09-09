#!/usr/bin/python3

import cgi, html
import base
from connect import connect
import settings
import os.path
import sys
import json
import cgitb

db=connect(0)
cur=db.cursor()

cgitb.enable()

print("content-type: text/html\n\n")
print('<!doctype html>')
print('<html lang="en">')
print('<head>')
print('<title> Config </title>')
print('</head>')
print('<body>')

form = cgi.FieldStorage()
config_id = base.cleanCGInumber(form.getvalue('config_id'))

cur.execute("SELECT role_id, component_id, teststand_id FROM Tester_Configuration WHERE config_id=%s" % (config_id));
components = cur.fetchall()

cur.execute('select name from Teststand where teststand_id=%s' % components[0][2])
teststand = cur.fetchall()[0][0]
print('<pre>')
print('Teststand: ' + teststand)
print('</pre>')

for c in components:
    cur.execute('select description from Tester_Roles where role_id=%s' % c[0])
    desc = cur.fetchall()[0][0]
    cur.execute('select full_id from Tester_Component where component_id=%s' % c[1])
    part = cur.fetchall()[0][0]
    print('<pre>')
    print(desc + ': ' + part)
    print('</pre>')



print('</body>')
print('</html>')

